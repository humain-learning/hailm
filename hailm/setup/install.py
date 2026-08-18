import frappe


def ensure_onboarding_statuses():
	onboarding_statuses = ["Started","Teacher Comms Sent","Student Comms Sent","Students Uploaded","Teachers Uploaded","Finished"]
	for status in onboarding_statuses:
		if not frappe.db.exists("Onboarding Status", status):
			frappe.get_doc({
				"doctype": "Onboarding Status",
				"name": status,
				"enabled": 1
			}).insert(ignore_permissions=True)

def after_install():
	ensure_onboarding_statuses()