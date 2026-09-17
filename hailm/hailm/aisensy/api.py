import requests
import frappe

BASE_URL = "https://backend.aisensy.com/campaign/t1/api/v2"
logger = frappe.logger("aisensy_api", with_more_info=True)


def send_aisensy_message(campaign_name:str,destination:str,payment:dict,template_params:list):
    url = BASE_URL

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