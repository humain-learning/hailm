import frappe
from .client.admin import fetch_single_school,fetch_school_progress
from .overrides.whitelisted import create_contact
from .utils import normalize_mobile
from frappe.utils import cint

@frappe.whitelist()
def sync_school(school_id):
	if not school_id:
		frappe.throw("School ID is required.")

	try:
		school_data = fetch_single_school(school_id)
	except Exception:
		school_data = None
	try:
		school_progress = fetch_school_progress(school_id)
	except Exception:
		school_progress = None


	if not school_data and not school_progress:
		frappe.throw("Could not sync school data")


	if school_data and school_data.get("status") == "deactivated":
		return


	school = frappe.get_doc("CRM Deal", {"custom_school_id": school_id})

	if school_data:
		parts = (school_data.get("coordinatorName") or "").split(maxsplit=1)

		coordinator_first_name = parts[0] if parts else ""
		coordinator_last_name = parts[1] if len(parts) > 1 else ""

		student_strength = school_data.get("studentStrength") or 0
		teacher_strength = school_data.get("teacherStrength") or 0

		student_strength = (
			student_strength
			if student_strength <= 10000
			else 1000
		)

		teacher_strength = (
			teacher_strength
			if teacher_strength <= 5000
			else 60
		)

		student_count = school_data.get("studentCount", 0)
		teacher_count = school_data.get("teacherCount", 0)

		contact_was_created = _update_primary_contact(
			school,
			coordinator_first_name,
			coordinator_last_name,
			school_data.get("coordinatorEmail"),
			normalize_mobile(school_data.get("coordinatorPhone")),
		)
		if not contact_was_created:
			school.reload()
		_refresh_primary_contact_snapshot(school)

		school.update({
			"organization_name": school_data.get("name"),
			"custom_school_id": school_data.get("_id"),
			"first_name": coordinator_first_name,
			"last_name": coordinator_last_name,
			"email": school_data.get("coordinatorEmail"),
			"mobile_no": normalize_mobile(school_data.get("coordinatorPhone")),
			"custom_principal_name": school_data.get("principalName"),
			"custom_principal_email": school_data.get("principalEmail"),
			"custom_kyc_status": (school_data.get("kyc") or {}).get("status"),
			"custom_school_type": school_data.get("schoolType"),
			"custom_interested_in_ai_club": 1 if school_data.get("interestedInAiClub") else 0,
			"custom_interested_in_ai_hub": 1 if school_data.get("interestedInAiHub") else 0,
			"custom_student_strength": student_strength,
			"custom_teacher_strength": teacher_strength,
			"custom_student_count": student_count,
			"custom_teacher_count": teacher_count,
			"custom_education_board": school_data.get("educationBoard"),
			"custom_school_dashboard_url": f"https://{school_data.get("slug")}.school.ailiteracymission.org/login",
			"custom_teacher_registration_url": school_data.get("teacherRegistrationUrl"),
			"custom_student_registration_url": school_data.get("studentRegistrationUrl"),
			"custom_address": school_data.get("address"),
			"custom_city": school_data.get("city"),
			"custom_state": school_data.get("state"),
			"custom_pincode": school_data.get("pincode"),
		})
	if school_progress:
		student_progress = school_progress.get("students")
		teacher_progress = school_progress.get("teachers")
		school.update({
			"custom_student_logged_in": student_progress.get("active"),
			"custom_student_foundational_enrolled": student_progress.get("foundational").get("enrolled"),
			"custom_student_foundational_completed": student_progress.get("foundational").get("completed"),
			"custom_student_intermediate_enrolled": student_progress.get("intermediate").get("enrolled"),
			"custom_student_intermediate_completed": student_progress.get("intermediate").get("completed"),
			"custom_student_advanced_enrolled": student_progress.get("advanced").get("enrolled"),
			"custom_student_advanced_completed": student_progress.get("advanced").get("completed"),
			"custom_student_state_1_olympiad_purchases": student_progress.get("olympiadPurchases").get("state1"),
			"custom_student_state_2_olympiad_purchases": student_progress.get("olympiadPurchases").get("state2"),
			"custom_student_national_olympiad_purchases": student_progress.get("olympiadPurchases").get("national"),


			"custom_teacher_logged_in": teacher_progress.get("active"),
			"custom_teacher_foundational_enrolled": teacher_progress.get("foundational").get("enrolled"),
			"custom_teacher_foundational_completed": teacher_progress.get("foundational").get("completed"),
			"custom_teacher_intermediate_enrolled": teacher_progress.get("intermediate").get("enrolled"),
			"custom_teacher_intermediate_completed": teacher_progress.get("intermediate").get("completed"),
			"custom_teacher_advanced_enrolled": teacher_progress.get("advanced").get("enrolled"),
			"custom_teacher_advanced_completed": teacher_progress.get("advanced").get("completed"),
			"custom_teacher_state_1_olympiad_purchases": teacher_progress.get("olympiadPurchases").get("state1"),
			"custom_teacher_state_2_olympiad_purchases": teacher_progress.get("olympiadPurchases").get("state2"),
			"custom_teacher_national_olympiad_purchases": teacher_progress.get("olympiadPurchases").get("national"),
		})

	school.save(ignore_permissions=True)

	return


def _update_primary_contact(deal, first_name, last_name, email, mobile_no):
	primary_contact = next(
		(row for row in deal.contacts if row.is_primary and row.contact),
		None,
	)
	if not primary_contact:
		contact_name = create_contact({
			"first_name": first_name,
			"last_name": last_name,
			"email": email,
			"mobile_no": mobile_no,
			"organization_name": deal.organization_name,
		})
		deal.append("contacts", {"contact": contact_name, "is_primary": 1})
		primary_contact = deal.contacts[-1]
		contact_was_created = True
	else:
		contact_was_created = False

	contact = frappe.get_doc("Contact", primary_contact.contact)
	contact.first_name = first_name
	contact.last_name = last_name

	primary_email = next((row for row in contact.email_ids if row.is_primary), None)
	if primary_email:
		primary_email.email_id = email or ""
	elif email:
		contact.append("email_ids", {"email_id": email, "is_primary": 1})

	primary_mobile = next(
		(row for row in contact.phone_nos if row.is_primary_mobile_no),
		None,
	)
	if primary_mobile:
		primary_mobile.phone = mobile_no or ""
	elif mobile_no:
		contact.append(
			"phone_nos",
			{"phone": mobile_no, "is_primary_mobile_no": 1},
		)

	contact.save(ignore_permissions=True)
	contact.reload()

	_refresh_primary_contact_snapshot(deal, contact)
	return contact_was_created


def _refresh_primary_contact_snapshot(deal, contact=None):
	primary_contact = next(
		(row for row in deal.contacts if row.is_primary and row.contact),
		None,
	)
	if not primary_contact:
		return

	contact = contact or frappe.get_doc("Contact", primary_contact.contact)
	primary_contact.email = contact.email_id or ""
	primary_contact.mobile_no = contact.mobile_no or ""
	primary_contact.phone = contact.phone or ""


def validate(deal, _):
	if deal.status == "Onboarding":
		statuses = {
			row.status
			for row in (deal.custom_onboarding_status or [])
			if row.status
		}

		if "Finished" in statuses:
			if "Started" in statuses:
				deal.set(
					"custom_onboarding_status",
					[
						row
						for row in deal.custom_onboarding_status
						if row.status != "Started"
					]
				)
		elif "Started" not in statuses:
			deal.append("custom_onboarding_status", {
				"status": "Started"
			})

	elif deal.status not in ("Onboarding", "Onboarded"):
		deal.set("custom_onboarding_status", [])

def before_save(deal, _):
	teacher_count = cint(deal.custom_teacher_count or 0)
	teacher_strength = cint(deal.custom_teacher_strength or 0)

	student_count = cint(deal.custom_student_count or 0)
	student_strength = cint(deal.custom_student_strength or 0)

	teacher_percentage = _safe_percentage(teacher_count, teacher_strength)
	student_percentage = _safe_percentage(student_count, student_strength)

	deal.custom_teacher_percentage = teacher_percentage
	deal.custom_student_percentage = student_percentage

	deal.custom_teacher_active_percent = _safe_percentage(
		deal.custom_teacher_logged_in, teacher_count
	)
	deal.custom_student_active_percent = _safe_percentage(
		deal.custom_student_logged_in, student_count
	)

	if teacher_percentage is None or student_percentage is None:
		deal.custom_min_rq_met = "No"
	elif teacher_percentage < 70 or student_percentage < 70:
		deal.custom_min_rq_met = "No"
	else:
		deal.custom_min_rq_met = "Yes"



def _safe_percentage(numerator, denominator):
	numerator = cint(numerator)
	denominator = cint(denominator)

	if denominator <= 0:
		return None

	return min(100, (numerator / denominator) * 100)