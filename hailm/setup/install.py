import json

import frappe


def ensure_calls_chart_on_dashboard():
	from crm.fcrm.doctype.crm_dashboard.crm_dashboard import create_default_manager_dashboard

	create_default_manager_dashboard()
	dashboard = frappe.get_doc("CRM Dashboard", "Manager Dashboard")
	layout = json.loads(dashboard.layout or "[]")
	if any(item.get("name") == "calls_by_day" for item in layout):
		return

	layout.append(
		{
			"name": "calls_by_day",
			"type": "axis_chart",
			"layout": {"x": 0, "y": 34, "w": 20, "h": 9, "i": "calls_by_day"},
		}
	)
	dashboard.db_set("layout", json.dumps(layout), update_modified=False)


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
	ensure_calls_chart_on_dashboard()


def after_migrate():
	ensure_calls_chart_on_dashboard()