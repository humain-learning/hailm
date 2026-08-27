import frappe
from .client.admin import fetch_school_list
from .overrides.whitelisted import create_deal
from .utils import normalize_mobile
from .deal_hooks import sync_school

logger = frappe.logger("hailmsync")


@frappe.whitelist()
def sync_registered_school_list(from_scheduler=True):
	from_scheduler = frappe.utils.cint(from_scheduler)
	if frappe.utils.now_datetime().hour == 0:
		if from_scheduler:
			return
		else:
			frappe.throw("Syncing of registered school list is not allowed between 12:00 AM and 1:00 AM. Please try again later.")
	
	schools = fetch_school_list()

	frappe.enqueue(
		method=insert_or_update_schools,
		schools=schools,
		queue="long",
		timeout=600,
		job_name="sync_registered_school_list",
	)
	return {"status": "ok"}
	

def insert_or_update_schools(schools):
	for school in schools:
		if school.get("status") == "deactivated":
			continue
		parts = (school.get("coordinatorName") or "").split(maxsplit=1)

		coordinator_first_name = parts[0] if parts else ""
		coordinator_last_name = parts[1] if len(parts) > 1 else ""
		# print("first name", coordinator_first_name, "last name", coordinator_last_name,"teachercount", teacher_count, "student count", student_count)
		mobile_no = normalize_mobile(school.get("coordinatorPhone") or "")
		student_strength = school.get("studentStrength") or 0
		teacher_strength = school.get("teacherStrength") or 0

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
		student_count = school.get("studentCount", 0)
		teacher_count = school.get("teacherCount", 0)
		if not frappe.db.exists("CRM Deal", {"custom_school_id": school.get("_id")}):
			# print(f"Creating new CRM Deal for school: {school.get('name')} (ID: {school.get('_id')})")
			try:
				
				deal_name = create_deal({
					"organization_name": school.get("name"),
					"custom_school_id": school.get("_id"),
					"first_name": coordinator_first_name,
					"last_name": coordinator_last_name,
					"email": school.get("coordinatorEmail"),
					"mobile_no": mobile_no,
					"custom_principal_name": school.get("principalName"),
					"custom_principal_email": school.get("principalEmail"),
					# "custom_principal_phone": school.get("principalPhone"),
					"custom_kyc_status": school.get("kyc").get("status"),
					"custom_school_type": school.get("schoolType"),
					"custom_interested_in_ai_club": 1 if school.get("interestedInAiClub") else 0,
					"custom_interested_in_ai_hub": 1 if school.get("interestedInAiHub") else 0,
					"custom_student_count": student_count,
					"custom_teacher_count": teacher_count,
					"custom_student_strength": student_strength,
					"custom_teacher_strength": teacher_strength,
					"custom_education_board": school.get("educationBoard")
				})
			except Exception as e:
				print(school.get("name"),":", str(e))
				continue
			
		else:
			
			name = frappe.db.get_value(
				"CRM Deal",
				{"custom_school_id": school["_id"]},
				"name",
			)
			# print(f"Updating existing CRM Deal for school: {school.get('name')} (ID: {school.get('_id')})")
			deal = frappe.get_doc("CRM Deal", name)
			deal.update({
				"organization_name": school.get("name"),
				# "custom_school_id": school.get("_id"),
				"first_name": coordinator_first_name,
				"last_name": coordinator_last_name,
				"email": school.get("coordinatorEmail"),
				"mobile_no": mobile_no,
				"custom_principal_name": school.get("principalName"),
				"custom_principal_email": school.get("principalEmail"),
				# "custom_principal_phone": school.get("principalPhone"),
				"custom_kyc_status": school.get("kyc").get("status"),
				"custom_school_type": school.get("schoolType"),
				"custom_interested_in_ai_club": 1 if school.get("interestedInAiClub") else 0,
				"custom_interested_in_ai_hub": 1 if school.get("interestedInAiHub") else 0,
				"custom_student_count": student_count,
				"custom_teacher_count": teacher_count,
				"custom_student_strength": student_strength,
				"custom_teacher_strength": teacher_strength,
				"custom_education_board": school.get("educationBoard")
			})
			deal.save(ignore_permissions=True)
	# print(sus_count, "suspended schools skipped during sync.")

@frappe.whitelist()
def sync_all_school_data():
	schools = frappe.get_all("CRM Deal", pluck="custom_school_id")

	frappe.enqueue(
		method=update_school_data,
		schools=schools,
		queue="long",
		timeout=600,
		job_name="sync_all_school_data",
	)
	return

def update_school_data(schools):
	for school in schools:
		sync_school(school)



