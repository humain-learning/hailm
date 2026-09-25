"""Run without a bench: python -m unittest hailm.hailm.test_hackathon_utils"""

import hashlib
import hmac
import unittest
from urllib.parse import parse_qs, urlsplit

from hailm.hailm.hackathon_utils import (
	ValidationError,
	clean_name,
	discount_code_payload,
	generate_code,
	match_payment,
	normalize_mobile,
	payment_page_url,
	verify_signature,
)

PRICE = 1499


def payment(amount=149900, contact="+919876543210", notes=None):
	return {"id": "pay_1", "amount": amount, "contact": contact, "notes": notes or {}}


def match(p, regs=("HHR-00001",), unpaid=None):
	unpaid = unpaid or {}
	return match_payment(p, PRICE, lambda n: n in regs, unpaid.get)


class TestInput(unittest.TestCase):
	def test_mobile_shapes(self):
		for raw in ("9876543210", "09876543210", "919876543210", "+91 98765-43210", "91919876543210"):
			self.assertEqual(normalize_mobile(raw), "+919876543210")

	def test_bad_mobile(self):
		for raw in ("", "12345", "5876543210", None):
			with self.assertRaises(ValidationError):
				normalize_mobile(raw)

	def test_name(self):
		self.assertEqual(clean_name("  Aarav   Sharma "), "Aarav Sharma")
		for raw in ("", "a", "12345", "x" * 121):
			with self.assertRaises(ValidationError):
				clean_name(raw)


class TestCode(unittest.TestCase):
	def test_code_shape(self):
		code = generate_code()
		self.assertRegex(code, r"^HLHACK-[A-HJKMNP-Z2-9]{6}$")

	def test_payload_is_single_use_100_percent_student_package(self):
		p = discount_code_payload("HLHACK-ABCDEF", "Aarav Sharma", "HHR-00001")
		self.assertEqual((p["scope"], p["valueType"], p["value"]), ("open", "percentage", 100))
		self.assertEqual((p["maxRedemptions"], p["perUserCap"]), (1, 1))
		self.assertEqual(p["packageIds"], ["STU-S1N1"])
		self.assertEqual(p["audiences"], ["student"])


class TestPaymentPage(unittest.TestCase):
	def test_prefill(self):
		url = payment_page_url(
			"https://pages.razorpay.com/pl_X/view", "Aarav S", "+919876543210", "HHR-00001"
		)
		q = parse_qs(urlsplit(url).query)
		self.assertEqual(
			q, {"phone": ["9876543210"], "full_name": ["Aarav S"], "registration_id": ["HHR-00001"]}
		)

	def test_signature(self):
		body = b'{"event":"payment.captured"}'
		sig = hmac.new(b"s3cret", body, hashlib.sha256).hexdigest()
		self.assertTrue(verify_signature(body, sig, "s3cret"))
		self.assertFalse(verify_signature(body, sig, "other"))
		self.assertFalse(verify_signature(body, sig, None))
		self.assertFalse(verify_signature(body, None, "s3cret"))


class TestMatchPayment(unittest.TestCase):
	def test_registration_id_in_notes_wins_even_at_other_amount(self):
		p = payment(amount=100, notes={"registration_id": "HHR-00001"})
		self.assertEqual(match(p), ("HHR-00001", "Registration ID"))

	def test_unknown_registration_id_falls_back_to_phone(self):
		p = payment(notes={"registration_id": "HHR-99999"})
		self.assertEqual(match(p, unpaid={"+919876543210": "HHR-00002"}), ("HHR-00002", "Phone + amount"))

	def test_phone_in_notes(self):
		p = payment(contact="+910000000000", notes={"phone": "98765 43210"})
		self.assertEqual(match(p, unpaid={"+919876543210": "HHR-00002"}), ("HHR-00002", "Phone + amount"))

	def test_phone_alone_at_wrong_amount_is_rejected(self):
		# A registered parent paying for something else on the same account.
		name, _ = match(payment(amount=99900), unpaid={"+919876543210": "HHR-00002"})
		self.assertIsNone(name)

	def test_no_matching_phone(self):
		name, _ = match(payment(), unpaid={})
		self.assertIsNone(name)

	def test_no_price_configured(self):
		name, _ = match_payment(payment(), None, lambda n: False, {"+919876543210": "HHR-00002"}.get)
		self.assertIsNone(name)


if __name__ == "__main__":
	unittest.main()
