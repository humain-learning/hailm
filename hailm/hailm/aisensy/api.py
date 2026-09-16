import requests
import frappe

BASE_URL = "https://backend.aisensy.com/campaign/t1/api/v2"



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

    print(response.json())
    # return response.json()