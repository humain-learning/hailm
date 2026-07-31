import frappe
from .client.admin import fetch_single_school
from .utils import normalize_mobile


@frappe.whitelist()
def sync_school(school_id):
	if not school_id:
		frappe.throw("School ID is required.")

	school_data = fetch_single_school(school_id)

	parts = (school_data.get("coordinatorName") or "").split(maxsplit=1)

	coordinator_first_name = parts[0] if parts else ""
	coordinator_last_name = parts[1] if len(parts) > 1 else ""
	student_strength = school_data.get("studentCount")
	teacher_strength = school_data.get("teacherCount")

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
		# "custom_principal_phone": school_data.get("principalPhone"),
		"custom_kyc_status": (school_data.get("kyc") or {}).get("status"),		
		"custom_school_type": school_data.get("schoolType"),
		"custom_interested_in_ai_club": 1 if school_data.get("interestedInAiClub") else 0,
		"custom_interested_in_ai_hub": 1 if school_data.get("interestedInAiHub") else 0,
		"custom_student_strength": student_strength,
		"custom_teacher_strength": teacher_strength,
		"custom_education_board": school_data.get("educationBoard"),
		"custom_school_dashboard_url": school_data.get("micrositeUrl"),
		"custom_teacher_registration_url": school_data.get("teacherRegistrationUrl"),
		"custom_student_registration_url": school_data.get("studentRegistrationUrl"),
	})
	school.save(ignore_permissions=True)
	frappe.msgprint("School data synced successfully.")
