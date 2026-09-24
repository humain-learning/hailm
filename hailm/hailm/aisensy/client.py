import frappe
import requests
from frappe.utils.logger import set_log_level
from .api import _eklavvya_headers
set_log_level("DEBUG")
logger = frappe.logger("aisensy", with_more_info=True,)
EKLAVVYA_BASE_URL = frappe.conf.get("EKLAVVYA_BASE_URL")

def multipart_value(value):
	return (None, value) if value else (None,None)

def get_candidate_list_of_batch(batch_id):
	url = f"{EKLAVVYA_BASE_URL}/Candidate/GetCandidatesList"
	candidates = []
	page_size = 400
	page_index = 0
	while True:
		payload = {
			"BatchId": multipart_value(str(batch_id)),
			"PageSize": multipart_value(str(page_size)),
			"PageIndex": multipart_value(str(page_index))
		}
		print(payload)
		response = requests.post(url, headers=_eklavvya_headers(), files=payload)
		logger.debug(f"Status: {response.status_code}")
		logger.debug(f"Headers: {response.headers}")
		logger.debug(f"Content: {response.content!r}")
		logger.debug(f"URL: {response.url}")
		data = response.json()
		if len(data["Data"]["List"]) == page_size:
			candidates.extend(data["Data"]["List"])
			page_index += 1
		else:
			candidates.extend(data["Data"]["List"])
			break
	return candidates