import frappe
from .client.admin import fetch_single_school
from .utils import normalize_mobile
from frappe.utils import cint

@frappe.whitelist()
def sync_school(school_id):
	if not school_id:
		frappe.throw("School ID is required.")

	school_data = fetch_single_school(school_id)

	if school_data.get("status") == "deactivated":
		return

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

	school = frappe.get_doc("CRM Deal", {"custom_school_id": school_id})

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
		"custom_school_dashboard_url": school_data.get("micrositeUrl"),
		"custom_teacher_registration_url": school_data.get("teacherRegistrationUrl"),
		"custom_student_registration_url": school_data.get("studentRegistrationUrl"),
		"custom_address": school_data.get("address"),
		"custom_city": school_data.get("city"),
		"custom_state": school_data.get("state"),
		"custom_pincode": school_data.get("pincode"),
	})

	school.save(ignore_permissions=True)
	return


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
    teacher_strength = cint(deal.custom_teacher_strength or 1)

    student_count = cint(deal.custom_student_count or 0)
    student_strength = cint(deal.custom_student_strength or 1)

    teacher_percentage = min(
        100,
        (teacher_count / teacher_strength) * 100
    )

    student_percentage = min(
        100,
        (student_count / student_strength) * 100
    )

    deal.custom_teacher_percentage = teacher_percentage
    deal.custom_student_percentage = student_percentage

    if teacher_percentage < 70 or student_percentage < 70:
        deal.custom_min_rq_met = "No"
    else:
        deal.custom_min_rq_met = "Yes"