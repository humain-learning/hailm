"""Humain Learning x HAILM Hackathon: registration -> Razorpay Payment Page -> code on WhatsApp.

1. humainlearning.ai calls `register` (server-side, API token). We store an Unpaid
   HAILM Hackathon Registration and return the Razorpay Payment Page URL, prefilled.
2. The student pays on the hosted page. No checkout on our side.
3. Razorpay calls `razorpay_webhook`; we mark the registration Paid.
4. `fulfil` (after commit) creates a single-use 100% code on the LMS and sends it on WhatsApp.

site_config.json:
	hailm_hackathon_amount                   price in rupees; must equal the Payment Page amount
	hailm_hackathon_payment_page_url         https://pages.razorpay.com/pl_XXXX/view
	hailm_hackathon_razorpay_webhook_secret  secret of the webhook pointing at razorpay_webhook
	hailm_hackathon_lms_url                  defaults to LMS staging
	hailm_hackathon_lms_identifier           LMS admin login used to create discount codes
	hailm_hackathon_lms_password
	hailm_hackathon_aisensy_campaign         AiSensy campaign; params [first name, code]. Uses AISENSY_API_KEY.
"""

import frappe
import requests
from frappe.utils import flt, now_datetime

from hailm.hailm.aisensy.api import send_aisensy_message
from hailm.hailm.hackathon_utils import (
	ValidationError,
	clean_name,
	discount_code_payload,
	first_name,
	generate_code,
	match_payment,
	normalize_mobile,
	payment_page_url,
	verify_signature,
)

DOCTYPE = "HAILM Hackathon Registration"
STAGING_LMS_URL = "https://api.staging.ailiteracymission.org/api/v1"


def _price():
	return flt(frappe.conf.get("hailm_hackathon_amount")) or None


# --- called by humainlearning.ai (server-side, API key auth) -----------------------------------


@frappe.whitelist(methods=["GET"])
def get_offer():
	page = frappe.conf.get("hailm_hackathon_payment_page_url")
	return {"active": bool(_price() and page), "amount": _price(), "currency": "INR"}


@frappe.whitelist(methods=["POST"])
def register():
	page = frappe.conf.get("hailm_hackathon_payment_page_url")
	if not (_price() and page):
		frappe.response.http_status_code = 400
		return {"error": "Registrations are not open yet."}

	data = frappe.request.get_json(silent=True) or {}
	try:
		full_name = clean_name(data.get("fullName"))
		mobile = normalize_mobile(data.get("mobile"))
	except ValidationError as exc:
		frappe.response.http_status_code = 400
		return {"error": str(exc)}

	# One registration per phone: returning visitors resume, payers aren't sent to pay again.
	name = frappe.db.get_value(DOCTYPE, {"mobile_no": mobile})
	if name:
		reg = frappe.get_doc(DOCTYPE, name)
		if reg.status == "Paid":
			return {"status": "paid", "token": reg.public_token}
		if reg.full_name != full_name:
			reg.db_set("full_name", full_name)
	else:
		utm = data.get("attribution") or {}
		reg = frappe.get_doc(
			{
				"doctype": DOCTYPE,
				"full_name": full_name,
				"mobile_no": mobile,
				"status": "Unpaid",
				"amount": _price(),
				"public_token": frappe.generate_hash(length=32),
				"utm_source": utm.get("custom_utm_source"),
				"utm_campaign": utm.get("custom_utm_campaign"),
			}
		).insert(ignore_permissions=True)

	return {
		"status": "unpaid",
		"token": reg.public_token,
		"paymentUrl": payment_page_url(page, reg.full_name, reg.mobile_no, reg.name),
	}


@frappe.whitelist(methods=["GET"])
def status(token=None):
	name = token and frappe.db.get_value(DOCTYPE, {"public_token": token})
	if not name:
		frappe.response.http_status_code = 404
		return {"error": "Registration not found"}
	reg = frappe.get_doc(DOCTYPE, name)
	result = {"status": reg.status.lower(), "firstName": first_name(reg.full_name)}
	if reg.status == "Paid":
		# Shown on the thank-you page too, so nobody is stuck waiting on WhatsApp.
		result.update(
			code=reg.discount_code or None, codeStatus=reg.code_status, whatsappStatus=reg.whatsapp_status
		)
	return result


# --- called by Razorpay --------------------------------------------------------------------------


@frappe.whitelist(allow_guest=True, methods=["POST"])
def razorpay_webhook():
	"""Razorpay webhook, events payment.captured + order.paid, URL:
	https://<site>/api/method/hailm.hailm.hackathon.razorpay_webhook
	"""
	raw = frappe.request.get_data()
	secret = frappe.conf.get("hailm_hackathon_razorpay_webhook_secret")
	if not verify_signature(raw, frappe.request.headers.get("X-Razorpay-Signature"), secret):
		frappe.response.http_status_code = 400
		return {"error": "Invalid signature"}

	event = frappe.parse_json(raw.decode())
	payment = (((event.get("payload") or {}).get("payment") or {}).get("entity")) or {}
	if event.get("event") not in ("payment.captured", "order.paid") or payment.get("status") != "captured":
		return {"note": "ignored"}

	# payment.captured and order.paid both arrive for one payment; handle it once.
	with frappe.cache.lock(f"lock:hailm_hackathon:{payment['id']}", timeout=60):
		if frappe.db.exists(DOCTYPE, {"payment_id": payment["id"]}):
			return {"note": "already processed"}

		name, how = match_payment(
			payment,
			_price(),
			registration_exists=lambda n: frappe.db.exists(DOCTYPE, n),
			unpaid_for_mobile=lambda m: frappe.db.get_value(DOCTYPE, {"mobile_no": m, "status": "Unpaid"}),
		)
		if not name:
			return {"note": f"no match: {how}"}

		reg = frappe.get_doc(DOCTYPE, name)
		if reg.status == "Paid":
			frappe.log_error(
				f"Second payment {payment['id']} for paid {name}", "HAILM Hackathon: duplicate payment"
			)
			return {"note": "duplicate payment"}

		reg.update(
			{
				"status": "Paid",
				"paid_at": now_datetime(),
				"payment_id": payment["id"],
				"amount_paid": flt(payment.get("amount")) / 100,
				"match_method": how,
				"webhook_payload": frappe.as_json(payment),
			}
		)
		reg.save(ignore_permissions=True)

	frappe.enqueue(fulfil, registration=name, queue="short", enqueue_after_commit=True)
	return {"note": f"paid: {name}"}


# --- fulfilment ----------------------------------------------------------------------------------


def _create_discount_code(reg):
	"""Single-use 100% STU-S1N1 code on the LMS. Returns (code, id); retries on a code clash."""
	base = (frappe.conf.get("hailm_hackathon_lms_url") or STAGING_LMS_URL).rstrip("/")
	login = requests.post(
		f"{base}/auth/login",
		json={
			"identifier": frappe.conf.get("hailm_hackathon_lms_identifier"),
			"password": frappe.conf.get("hailm_hackathon_lms_password"),
		},
		timeout=30,
	)
	login.raise_for_status()
	headers = {"Authorization": f"Bearer {login.json()['data']['accessToken']}"}

	for _ in range(3):
		payload = discount_code_payload(generate_code(), reg.full_name, reg.name)
		resp = requests.post(f"{base}/payments/discount-codes", json=payload, headers=headers, timeout=30)
		if resp.status_code != 409:  # 409 = code already exists, try another
			break
	if not resp.ok:
		raise RuntimeError(f"LMS {resp.status_code}: {resp.text[:300]}")
	doc = resp.json().get("data") or {}
	return doc.get("code") or payload["code"], doc.get("_id")


def fulfil(registration):
	"""Create the code, then WhatsApp it. Each step records its status, so re-running is safe."""
	reg = frappe.get_doc(DOCTYPE, registration)
	if reg.status != "Paid":
		return

	if not reg.discount_code:
		try:
			code, code_id = _create_discount_code(reg)
			reg.db_set(
				{
					"discount_code": code,
					"discount_code_id": code_id,
					"code_status": "Generated",
					"error": None,
				}
			)
		except Exception as exc:
			reg.db_set({"code_status": "Failed", "error": str(exc)[:1000]})
			frappe.log_error(title=f"HAILM Hackathon: code failed for {reg.name}")
			return

	if reg.whatsapp_status == "Sent":
		return
	campaign = frappe.conf.get("hailm_hackathon_aisensy_campaign")
	if not (campaign and frappe.conf.get("AISENSY_API_KEY")):
		reg.db_set("whatsapp_status", "Not Configured")
		return
	try:
		send_aisensy_message(
			campaign, reg.mobile_no, reg.full_name, [first_name(reg.full_name), reg.discount_code]
		)
		reg.db_set({"whatsapp_status": "Sent", "whatsapp_sent_at": now_datetime(), "error": None})
	except Exception as exc:
		reg.db_set({"whatsapp_status": "Failed", "error": str(exc)[:1000]})
		frappe.log_error(title=f"HAILM Hackathon: WhatsApp failed for {reg.name}")


@frappe.whitelist(methods=["POST"])
def retry(registration):
	"""Re-run fulfilment for a paid registration, e.g. once AiSensy is configured."""
	frappe.only_for("System Manager")
	frappe.enqueue(fulfil, registration=registration, queue="short")
	return {"queued": True}
