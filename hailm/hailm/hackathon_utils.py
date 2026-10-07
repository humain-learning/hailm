"""Pure helpers for the Humain Learning x HAILM Hackathon. No frappe import, so tests run anywhere."""

import hashlib
import hmac
import re
import secrets
from datetime import UTC, datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# No 0/O, 1/I/L: codes get read off WhatsApp and typed by hand.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

# Hackathon + 1 State + 1 National = the student state_national package. Pinning the 100% code
# to it stops it being spent on a pricier package.
PACKAGE_IDS = ["STU-S1N1"]

# Last State round is 11 Oct and its registration closes 7 Oct, so the code is useless after.
CODE_ENDS_AT = "2026-10-07T23:59:59.999+05:30"

REGISTRATION_ID = re.compile(r"\bHHR-\d{5,}\b")


class ValidationError(ValueError):
	"""User-correctable input problem; the message is safe to show."""


def normalize_mobile(raw):
	"""'+91XXXXXXXXXX' or ValidationError. Accepts 10 digits, 0/91/9191 prefixes."""
	digits = re.sub(r"\D", "", str(raw or ""))
	if len(digits) == 14 and digits.startswith("9191"):
		digits = digits[4:]
	elif len(digits) == 12 and digits.startswith("91"):
		digits = digits[2:]
	elif len(digits) == 11 and digits.startswith("0"):
		digits = digits[1:]
	if len(digits) != 10 or digits[0] not in "6789":
		raise ValidationError("Enter a valid 10-digit Indian mobile number.")
	return "+91" + digits


def clean_name(raw):
	name = re.sub(r"\s+", " ", str(raw or "")).strip()
	if not (2 <= len(name) <= 120) or not re.search(r"[A-Za-zऀ-ॿ]", name):
		raise ValidationError("Enter the student's full name.")
	return name


def first_name(full_name):
	return (full_name or "").split(" ", 1)[0]


def generate_code(rand=secrets.choice):
	return "HLHACK-" + "".join(rand(CODE_ALPHABET) for _ in range(6))


def discount_code_payload(code, student_name, registration, now=None):
	"""POST /payments/discount-codes body. Verified against LMS staging on 2026-09-25.

	`audiences` is dropped server-side for open codes; the STU- package lock is what keeps it
	student-only.
	"""
	now = now or datetime.now(UTC)
	return {
		"code": code,
		"name": f"HAILM Hackathon - {student_name}"[:100],
		"description": f"Humain Learning x HAILM Hackathon. Registration {registration}.",
		"scope": "open",
		"valueType": "percentage",
		"value": 100,
		"productScope": "olympiad",
		"courseIds": [],
		"packageIds": PACKAGE_IDS,
		"schoolIds": [],
		"audiences": ["student"],
		"startsAt": now.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
		"endsAt": CODE_ENDS_AT,
		"maxRedemptions": 1,
		"perUserCap": 1,
		"campaignLabel": "Humain Learning x HAILM Hackathon",
	}


def payment_page_url(page_url, full_name, mobile, registration):
	"""Prefill the Razorpay Payment Page via its long URL (pages.razorpay.com/pl_XXX/view).

	`phone` is a standard field; `full_name` and `registration_id` must exist as input fields on
	the page (Razorpay ignores unknown params). The registration id then comes back in the
	payment's notes, which is how the webhook finds the registration.
	"""
	parts = urlsplit(page_url)
	query = dict(parse_qsl(parts.query))
	query.update(
		{"phone": normalize_mobile(mobile)[3:], "full_name": full_name, "registration_id": registration}
	)
	return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def verify_signature(raw_body, signature, secret):
	"""Razorpay signs the raw webhook body with HMAC-SHA256 using the webhook secret."""
	if not (raw_body and signature and secret):
		return False
	body = raw_body if isinstance(raw_body, bytes) else raw_body.encode()
	expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
	return hmac.compare_digest(expected, signature)


def match_payment(payment, price, registration_exists, unpaid_for_mobile):
	"""Which registration a captured payment is for: (name, how) or (None, why).

	Razorpay webhooks are account-wide, so every payment on the account lands here. Accept one only if
	  1. its notes carry one of our registration ids, or
	  2. its phone matches an Unpaid registration AND the amount is exactly the hackathon price.
	Phone alone is never enough: a parent paying for something else must not be marked Paid.
	"""
	notes = payment.get("notes") or {}
	values = [str(v) for v in (notes.values() if isinstance(notes, dict) else notes)]

	for reg_id in dict.fromkeys(m for v in values for m in REGISTRATION_ID.findall(v)):
		if registration_exists(reg_id):
			return reg_id, "Registration ID"

	if not price or int(payment.get("amount") or 0) != round(float(price) * 100):
		return None, "amount is not the hackathon price"
	for raw in [*values, payment.get("contact")]:
		try:
			name = unpaid_for_mobile(normalize_mobile(raw))
		except ValidationError:
			continue
		if name:
			return name, "Phone + amount"
	return None, "no unpaid registration with that phone"
