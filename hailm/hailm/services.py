import frappe
from .client.admin import fetch_learners, fetch_school_list
# import random
from .overrides.whitelisted import create_deal
from .utils import normalize_mobile



@frappe.whitelist()
def sync_registered_school_list():
	schools = fetch_school_list()
	# frappe.enqueue(
	# 	method=insert_or_update_schools,
	# 	schools=schools,
	# 	queue="long",
	# 	timeout=600,
	# 	job_name="sync_registered_school_list",
	# )
	insert_or_update_schools(schools)

# def create_school_deal(school):



def insert_or_update_schools(schools):
	for school in schools:
		if not school.get("coordinatorName"):
			print(f"Skipping school {school.get('name')} due to missing coordinator name.")
			continue

		parts = (school.get("coordinatorName") or "").split(maxsplit=1)

		coordinator_first_name = parts[0] if parts else ""
		coordinator_last_name = parts[1] if len(parts) > 1 else ""
		# print("first name", coordinator_first_name, "last name", coordinator_last_name,"teachercount", teacher_count, "student count", student_count)
		mobile_no = normalize_mobile(school.get("coordinatorPhone") or "")

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
					"custom_student_strength": school.get("studentCount"),
					"custom_teacher_strength": school.get("teacherCount"),
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
			print(f"Updating existing CRM Deal for school: {school.get('name')} (ID: {school.get('_id')})")
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
				"custom_student_strength": school.get("studentCount"),
				"custom_teacher_strength": school.get("teacherCount"),
				"custom_education_board": school.get("educationBoard")
			})
			deal.save(ignore_permissions=True)


































































# def split_learners_by_role(users):
# 	students = []
# 	teachers = []

# 	for user in users:
# 		role = user.get("role")
# 		if role == "student":
# 			students.append(user)
# 		elif role == "teacher":
# 			teachers.append(user)
# 		else:
# 			pass

# 	return students, teachers 
