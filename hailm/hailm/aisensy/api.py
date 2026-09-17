import requests
import frappe

AISENSY_BASE_URL = "https://backend.aisensy.com/campaign/t1/api/v2"
EKLAVVYA_BASE_URL = "https://api-v2.eklavvya.com"


logger = frappe.logger("aisensy", with_more_info=True)


def send_aisensy_message(campaign_name:str,destination:str,payment:dict,template_params:list):
	url = AISENSY_BASE_URL

	payload = {
		"apiKey": frappe.conf.get("AISENSY_API_KEY"),
		"campaignName": campaign_name,
		"destination": destination,
		"userName": payment.get("beneficiary").get("name"),

		# Must match your WhatsApp template variables in order.
		"templateParams": template_params
	}

	response = requests.post(
		url,
		json=payload,
		headers={"Content-Type": "application/json"},
		timeout=30,
	)

	logger.info(
		"AiSensy response: campaign=%s status=%s support_reference=%s body=%s",
		campaign_name,
		response.status_code,
		payment.get("supportReference"),
		response.text[:1000],
	)
	response.raise_for_status()
	return response.text

def _refresh_eklavvya_token():
	url = f"{EKLAVVYA_BASE_URL}/Institute/Login"
	payload = {
		"UserName": (None, frappe.conf.get("eklavvya_username")),
		"Password": (None, frappe.conf.get("eklavvya_password")),
		"Role": (None, "1")
	}
	response = requests.post(url, files=payload)
	print(response.status_code)
	response.raise_for_status()
	data = response.json()
	token = data["Data"]["Token"]
	frappe.cache.set("eklavvya_token", token)
	return token


def _eklavvya_headers():
	token = frappe.cache.get("eklavvya_token")

	if not token:
		token = _refresh_eklavvya_token()

	return {
		"Authorization": f"Bearer {token}",
	}

def create_new_candidate(payload):
	url = f"{EKLAVVYA_BASE_URL}/Candidate/CreateNewCandidate"
	headers = _eklavvya_headers()
	response = requests.post(url, files=payload, headers=headers)
	response.raise_for_status()
	return response.json()