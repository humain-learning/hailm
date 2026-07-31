import frappe
import requests

BASE_URL = "https://api.ailiteracymission.org/api/v1"


def _headers():
	token_doc = frappe.get_single("HAILM Token")
	return {
		"Authorization": f"Bearer {token_doc.get_password('access_token')}",
	}


@frappe.whitelist()
def fetch_schools_as_deals(page):
	url = f"{BASE_URL}/tenants"
	headers = _headers()

	params = {
		"page" : page,
		"limit" : 1
	}

	response = requests.get(url, headers=headers, params=params, timeout=30)
	response.raise_for_status()
	data = response.json()
	items = data.get("data").get("items")
	print(items)
	deal = frappe.get_doc({
		"doctype" : "CRM Deal",
		"organization_name": items[0].get("name"),
		"custom_school_id": items[0].get("_id"),
		"first_name": items[0].get("coordinatorName").split(" ")[0],
		"last_name": items[0].get("coordinatorName").split(" ")[1] or "",
		"email": items[0].get("coordinatorEmail"),
		"mobile_no": f'+91{items[0].get("coordinatorPhone")}',
		"custom_principal_name": items[0].get("principalName"),
		"custom_principal_email": items[0].get("principalEmail"),
		# "custom_principal_phone": items[0].get("principalPhone"),
		"custom_kyc_status": items[0].get("kyc").get("status"),
		"custom_school_type": items[0].get("schoolType"),
		"custom_interested_in_ai_club": 1 if items[0].get("interestedInAiClub") else 0,
		"custom_interested_in_ai_hub": 1 if items[0].get("interestedInAiHub") else 0,
		"custom_student_strength": items[0].get("studentCount"),
		"custom_teacher_strength": items[0].get("teacherCount"),
		"custom_education_board": items[0].get("educationBoard"),
	})
	print(deal.as_dict())
	# deal.insert(ignore_permissions=True)
	# deal.reload()
	print("fetched email", items[0].get("coordinatorPhone"))
	print("deal email", deal.mobile_no)
