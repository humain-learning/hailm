import requests
import frappe
from frappe.utils.logger import set_log_level
AISENSY_BASE_URL = "https://backend.aisensy.com/campaign/t1/api/v2"
EKLAVVYA_BASE_URL = "https://api-v2.eklavvya.com"

set_log_level("DEBUG")
logger = frappe.logger("aisensy", with_more_info=True,)

class EklavvyaExistingCandidateError(Exception):
    def __init__(self, data):
        self.data = data
        super().__init__(data)

class EklavvyaAssignToBatchError(Exception):
    pass

def send_aisensy_message(campaign_name:str,destination:str,username:str,template_params:list):
	url = AISENSY_BASE_URL

	payload = {
		"apiKey": frappe.conf.get("AISENSY_API_KEY"),
		"campaignName": campaign_name,
		"destination": destination,
		"userName": username,

		# Must match your WhatsApp template variables in order.
		"templateParams": template_params
	}

	response = requests.post(
		url,
		json=payload,
		headers={"Content-Type": "application/json"},
		timeout=30,
	)

	# logger.info(
	# 	"AiSensy response: campaign=%s status=%s support_reference=%s body=%s",
	# 	campaign_name,
	# 	response.status_code,
	# 	payment.get("supportReference"),
	# 	response.text[:1000],
	# )
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
	# response.raise_for_status()
	logger.warning(
		"Eklavvya login response: status=%s content_type=%s url=%s body=%s",
		response.status_code,
		response.headers.get("Content-Type"),
		response.url,
		response.text[:2000],
	)	
	data = response.json()
	token = data["Data"]["Token"]
	frappe.cache.set_value("eklavvya_token", token,expires_in_sec=18000)
	return token


def _eklavvya_headers():
	token = frappe.cache.get_value(key="eklavvya_token",generator=_refresh_eklavvya_token)

	return {
		"Authorization": f"Bearer {token}",
	}

def create_new_candidate(payload):
	url = f"{EKLAVVYA_BASE_URL}/Candidate/CreateNewCandidate"
	headers = _eklavvya_headers()
	response = requests.post(url, files=payload, headers=headers)
	logger.warning(
		"Eklavvya response: status=%s content_type=%s url=%s body=%s",
		response.status_code,
		response.headers.get("Content-Type"),
		response.url,
		response.text[:2000],
	)
	data=response.json()

	if data.get("Data", {}).get("Message") is None:		
		raise EklavvyaExistingCandidateError(data)
	return data

def assign_to_batch(payload):
	url = f"{EKLAVVYA_BASE_URL}/Candidate/AssignToBatch"
	headers = _eklavvya_headers()
	response = requests.post(url, files=payload, headers=headers)
	logger.warning(
		"Eklavvya login response: status=%s content_type=%s url=%s body=%s",
		response.status_code,
		response.headers.get("Content-Type"),
		response.url,
		response.text[:2000],
	)
	data = response.json()
	return data

def update_user_password(user, password, batch_id):
	print(f"Created {user['userData'].get('name')} to batch {batch_id} with new password: {password}")