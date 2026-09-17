import frappe
import requests

BASE_URL = "https://api.ailiteracymission.org/api/v1"

@frappe.whitelist()
def fetch_and_save_token():
	creds = frappe.get_single("HAILM Credentials")
	if not creds:
		frappe.log_error(title= "Error Fetching HAILM Token", message = "No Credentials Found")
		return

	url = f"{BASE_URL}/auth/login"
	payload = {
		"identifier" : creds.identifier,
		"password" : creds.get_password("password")
	}

	try:
		response = requests.post(url, json=payload, timeout=30)

		response.raise_for_status()
		data = response.json().get("data")
		data = frappe.parse_json(data)

		token_doc = frappe.get_single("HAILM Token")
		token_doc.access_token = data.accessToken
		token_doc.refresh_token = data.refreshToken
		token_doc.last_refresh_at = frappe.utils.now()
		token_doc.save(ignore_permissions=True)
		return

	except requests.exceptions.HTTPError as e:
		frappe.log_error(message = f"Error Fetching HAILM Token:\n {e}\nResponse: {response.text}", title = "HAILM Token Fetch Error")
		raise
	except requests.exceptions.RequestException as e:
		frappe.log_error(message = f"Error Fetching HAILM Token:\n {e}\n\n\n {frappe.get_traceback()}", title ="HAILM Token Fetch Error")
		raise


def _headers():
	token_doc = frappe.get_single("HAILM Token")
	return {
		"Authorization": f"Bearer {token_doc.get_password('access_token')}",
	}

@frappe.whitelist()
def fetch_learners(school_id):
	url = f"{BASE_URL}/users"
	headers = _headers()
	page = 1
	limit = 100
	users = []
	while True:
		params = {
			"tenantId": school_id,
			"page": page,
			"limit": limit
		}

		response = requests.get(url, headers=headers, params=params, timeout=30)
		response.raise_for_status()

		data = response.json()
		items = data.get("data").get("items")

		if len(items) < limit:
			users.extend(items)
			print("Received ",len(items), " items in this page, breaking loop at page=", page)
			break

		users.extend(items)
		print("Received ",len(items), " items in this page")
		page += 1
	print("Fetched ", len(users), " users in total")
	return users

def fetch_school_list():
	url = f"{BASE_URL}/tenants"
	headers = _headers()
	page = 1
	limit = 100
	schools = []
	while True:
		params = {
			"page": page,
			"limit": limit
		}

		response = requests.get(url, headers=headers, params=params, timeout=30)
		
		if response.status_code != 200:
			frappe.log_error(message = f"Error Fetching HAILM Schools:\n Response: {response.text}", title = "HAILM Schools Fetch Error")
			response.raise_for_status()
			return
		
		data = response.json()
		items = data.get("data").get("items")

		if len(items) < limit:
			schools.extend(items)
			print("Received ",len(items), " items in this page, breaking loop at page=", page)
			break

		schools.extend(items)
		print("Received ",len(items), " items in this page")
		page += 1
	print("Fetched ", len(schools), " schools in total")
	return schools


def fetch_single_school(school_id):
	url = f"{BASE_URL}/tenants/{school_id}"

	try:
		response = requests.get(url, headers=_headers(), timeout=30)
		response.raise_for_status()
	except requests.exceptions.RequestException:
		frappe.log_error(
			message=frappe.get_traceback(),
			title="HAILM Schools Fetch Error",
		)
		raise
	# print(response.json().get("data"))
	return response.json().get("data")

def fetch_school_progress(school_id):
	url = f"{BASE_URL}/tenants/{school_id}/progress-summary"

	try:
		response = requests.get(url=url, headers=_headers(), timeout=30)
		response.raise_for_status()
	except requests.exceptions.RequestException:
		frappe.log_error(
			message=frappe.get_traceback(),
			title="HAILM School Progress Fetch Error"
		)
		raise

	return response.json().get("data")



def fetch_analytics(params:dict):
	url = f"{BASE_URL}/school-dashboard/admin/user-analytics"
	headers = _headers()
	response = requests.get(url=url, headers = headers, params=params)
	# print(response.json().get("data",{}))
	return response.json().get("data",{})




def fetch_csv_export(params:dict):
	url = f"{BASE_URL}/school-dashboard/admin/user-analytics/export"
	headers = _headers()
	response = requests.get(url=url, headers=headers, params=params)
	return response.content

def fetch_user(user_id):
	url = f"{BASE_URL}/users/{user_id}"
	headers = _headers()
	response = requests.get(url=url, headers=headers)
	return response.json().get("data",{})

def fetch_payments(from_date, to_date,status=None):
	url = f"{BASE_URL}/payments"
	headers = _headers()

	params = {
		"from": from_date if from_date else None,
		"to": to_date if to_date else None,
		"status": status
	}
	page=1
	limit=100
	payments = []
	while True:
		params["page"] = page
		params["limit"] = limit

		response = requests.get(url=url, headers=headers, params=params)
		if response.status_code != 200:
			frappe.log_error(message = f"Error Fetching HAILM Schools:\n Response: {response.text}", title = "HAILM Schools Fetch Error")
			response.raise_for_status()
			return

		data = response.json()
		items = data.get("items")
		payments.extend(items)

		if len(items) < limit:
			print("Received ",len(items), " items in this page, breaking loop at page=", page)
			break
		else:
			page+=1
	# print(payments)
	return payments


