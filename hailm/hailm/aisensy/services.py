from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import frappe
from frappe.utils import getdate

from hailm.hailm.client.admin import fetch_payments, fetch_user
from hailm.hailm.utils import normalize_mobile

from .api import send_aisensy_message


IST = ZoneInfo("Asia/Kolkata")

# Statuses meaning the user is done -- money is captured or held.
# `authorized` has paidAt == None, so status (not paidAt) decides completion.
COMPLETED_STATUSES = {"paid", "authorized"}

# Lag between the end of the hourly window and "now", so a payment that is
# still mid-capture is not called dropped. Observed create->capture gaps run
# to ~50 minutes, so this is a floor, not a guarantee.
SETTLE_BUFFER = timedelta(minutes=15)

# How many IST calendar days back each daily reminder looks.
SECOND_REMINDER_DAYS_AGO = 1
THIRD_REMINDER_DAYS_AGO = 2

# Extra days pulled below the earliest bucket. The API filters on createdAt,
# so a payment created just before the range but captured inside it would
# otherwise never register as a completion.
FETCH_LOOKBACK_PAD = timedelta(days=1)

EPOCH = datetime.min.replace(tzinfo=timezone.utc)

OLYMPIAD_REGISTRATION_CLOSING_DATES = {
    "student": (
        getdate("2026-09-18"),
        getdate("2026-09-25"),
        getdate("2026-10-03"),
        getdate("2026-10-11"),
        getdate("2026-10-19"),
        getdate("2026-10-27"),
        getdate("2026-10-31"),
    ),
    "teacher": (
        getdate("2026-09-16"),
        getdate("2026-09-22"),
        getdate("2026-10-01"),
        getdate("2026-10-09"),
        getdate("2026-10-17"),
        getdate("2026-10-24"),
        getdate("2026-10-30"),
    ),
}


# ---------------------------------------------------------------- helpers


def _parse_ts(value):
	"""ISO8601 string (or None) -> timezone-aware UTC datetime (or None)."""
	if not value:
		return None
	return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _completion_ts(payment):
	"""When a completed payment actually landed.

	paidAt is the real settlement time; createdAt can be ~50 minutes earlier.
	`authorized` rows carry no paidAt, so fall back to createdAt for those.
	"""
	return _parse_ts(payment.get("paidAt")) or _parse_ts(payment.get("createdAt"))


def _ist_date(dt):
	"""UTC datetime -> the IST calendar date it falls on."""
	return dt.astimezone(IST).date()


def _last_completion_by_user(payments):
	"""userId -> latest settlement time among that user's completed payments."""
	latest = {}
	for payment in payments:
		if payment.get("status") not in COMPLETED_STATUSES:
			continue

		user_id = payment.get("userId")
		settled_at = _completion_ts(payment)
		if not user_id or not settled_at:
			continue

		if settled_at > latest.get(user_id, EPOCH):
			latest[user_id] = settled_at

	return latest


def _is_exempt_school(payment):
	"""True only when the tenant is explicitly on the exempt list.

	A missing tenantId must NOT reach frappe.db.exists -- a None name falls
	through to a filterless lookup that returns the first row of the doctype,
	silently exempting every tenant-less payment.
	"""
	tenant_id = payment.get("tenantId")
	if not tenant_id:
		return False
	return bool(frappe.db.exists("WA Exempt Schools", tenant_id))


def _still_unpaid(payment, created_at, last_completion):
	"""No successful payment by this user after the dropped attempt."""
	return last_completion.get(payment.get("userId"), EPOCH) <= created_at


def _latest_attempt_per_user(payments):
	"""One payment per user -- their most recent attempt.

	Every beneficiary has their own account (a parent with two children has
	two userIds), so this still sends one message per child. Latest wins
	because the template prints the attempt date.
	"""
	latest = {}
	for payment in payments:
		user_id = payment.get("userId")
		created_at = _parse_ts(payment.get("createdAt"))
		if not user_id or not created_at:
			continue

		if user_id not in latest or created_at > latest[user_id][0]:
			latest[user_id] = (created_at, payment)

	return [payment for _, payment in latest.values()]


def _select_dropped(payments, last_completion, in_window):
	"""Dropped, non-exempt, still-unpaid payments matching `in_window`."""
	selected = []
	for payment in payments:
		created_at = _parse_ts(payment.get("createdAt"))
		if not created_at or not in_window(created_at):
			continue

		if payment.get("status") in COMPLETED_STATUSES:
			continue

		if _is_exempt_school(payment):
			continue

		if not _still_unpaid(payment, created_at, last_completion):
			continue

		selected.append(payment)

	return _latest_attempt_per_user(selected)


# ------------------------------------------------------- hourly selection


def get_recently_dropped_payments():
	"""Payments dropped roughly an hour ago and still unpaid.

	Rolling window -- this one genuinely is a timer, so it stays anchored on
	now rather than on a calendar day.

	All datetimes are UTC. The API reads its from/to params as UTC dates
	(verified against the endpoint), so anchoring on the Frappe system
	timezone would request a UTC day that has not begun during 00:00-05:30
	IST and return nothing.
	"""
	now = datetime.now(timezone.utc)
	window_end = now - SETTLE_BUFFER
	window_start = window_end - timedelta(hours=1)

	payments = fetch_payments(
		(window_start - FETCH_LOOKBACK_PAD).date(),
		now.date(),
	)
	last_completion = _last_completion_by_user(payments)

	return _select_dropped(
		payments,
		last_completion,
		lambda created_at: window_start <= created_at < window_end,
	)


# -------------------------------------------------------- daily selection


def get_daily_dropped_payments():
	"""Buckets for the 24h and 48h reminders, as IST calendar days.

	Returns (second_reminder, third_reminder). A user appearing in both
	dropped on two consecutive days; they get the message for their most
	recent attempt (the second reminder) and the older one is discarded.
	Their recent attempt becomes a third-reminder candidate tomorrow, so
	the sequence is shifted by a day, not lost.
	"""
	today_ist = datetime.now(timezone.utc).astimezone(IST).date()
	second_day = today_ist - timedelta(days=SECOND_REMINDER_DAYS_AGO)
	third_day = today_ist - timedelta(days=THIRD_REMINDER_DAYS_AGO)

	# IST day boundaries sit at 18:30 UTC, so pad below the earliest bucket
	# before handing UTC dates to the API, then bucket locally.
	earliest = datetime.combine(third_day, time.min, tzinfo=IST) - FETCH_LOOKBACK_PAD
	payments = fetch_payments(
		earliest.astimezone(timezone.utc).date(),
		datetime.now(timezone.utc).date(),
	)
	last_completion = _last_completion_by_user(payments)

	second = _select_dropped(
		payments,
		last_completion,
		lambda created_at: _ist_date(created_at) == second_day,
	)
	third = _select_dropped(
		payments,
		last_completion,
		lambda created_at: _ist_date(created_at) == third_day,
	)

	# Same user in both buckets -> keep only their most recent attempt.
	second_user_ids = {payment.get("userId") for payment in second}
	third = [p for p in third if p.get("userId") not in second_user_ids]

	return second, third


# --------------------------------------------------------------- sending


def get_nearest_registration_closing_date(payment):
	role = (payment.get("beneficiary") or {}).get("role")
	closing_dates = OLYMPIAD_REGISTRATION_CLOSING_DATES.get(role)

	if not closing_dates:
		return None

	# Deliberately local: these are business-facing calendar deadlines, not
	# fetch-window boundaries.
	today = getdate()

	for date in closing_dates:
		if date >= today:
			return date

	return None


def build_template_params(campaign_name, payment):
	beneficiary_name = (payment.get("beneficiary") or {}).get("name") or ""

	if campaign_name == "Payment Failure":
		created_at = _parse_ts(payment.get("createdAt"))
		return [
			beneficiary_name,
			created_at.astimezone(IST).strftime("%-d %b %Y") if created_at else "",
		]

	if campaign_name == "Payment Failure 2":
		return [beneficiary_name]

	if campaign_name == "Payment Failure 3":
		closing_date = get_nearest_registration_closing_date(payment)
		return [
			beneficiary_name,
			closing_date.strftime("%-d %b %Y") if closing_date else "",
		]

	raise ValueError(f"Unknown campaign: {campaign_name}")


def _send_reminders(campaign_name, payments):
	"""One message per payment. A bad record must not kill the batch."""
	sent = 0
	for payment in payments:
		try:
			user = fetch_user(payment.get("userId")) or {}
			destination = normalize_mobile(user.get("phone"))
			# destination = "+919560709221"
			if not destination:
				frappe.log_error(
					message=f"No phone for userId {payment.get('userId')} "
					f"(payment {payment.get('supportReference')})",
					title=f"{campaign_name}: missing destination",
				)
				continue

			send_aisensy_message(
				campaign_name=campaign_name,
				destination=destination,
				payment=payment,
				template_params=build_template_params(campaign_name, payment),
			)
			sent += 1
		except Exception:
			frappe.log_error(
				message=f"Payment {payment.get('supportReference')}\n"
				f"{frappe.get_traceback()}",
				title=f"{campaign_name}: send failed",
			)

	return sent


# ------------------------------------------------------------ entrypoints


def initial_dropped_payment_reminder():
	"""Hourly cron. ~1 hour after the dropped attempt."""
	payments = get_recently_dropped_payments()
	if not payments:
		return "Payment Failure: no dropped payments found"

	sent = _send_reminders("Payment Failure", payments)
	return f"Payment Failure: sent {sent}/{len(payments)}"


def daily_dropped_payment_reminders():
	"""Daily cron (18:00 IST). Second and third reminders in one pass.

	Both buckets come from one fetch so a user in both can be collapsed to a
	single message before anything is sent.
	"""
	second, third = get_daily_dropped_payments()

	if not second and not third:
		return "Daily reminders: no dropped payments found"

	sent_second = _send_reminders("Payment Failure", second)
	sent_third = _send_reminders("Payment Failure", third)

	return (
		f"Payment Failure 2: sent {sent_second}/{len(second)}; "
		f"Payment Failure 3: sent {sent_third}/{len(third)}"
	)