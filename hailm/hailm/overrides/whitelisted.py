import frappe
from frappe import _
from frappe.model.document import Document

from crm.fcrm.doctype.crm_deal.crm_deal import create_contact


def create_school_organization(doc) -> str:
	if not doc.get("custom_school_id"):
		frappe.throw(_("School ID is required to create an organization."))
	existing_organization = frappe.db.exists(
		"CRM Organization",
		{"custom_school_id": doc.get("custom_school_id")},
	)

	if existing_organization:
		return existing_organization

	organization = frappe.new_doc("CRM Organization")

	organization.update(
		{
			"organization_name": doc.get("organization")
			or doc.get("organization_name"),
			"custom_school_id": doc.get("custom_school_id"),
			"website": doc.get("website"),
			"territory": doc.get("territory"),
			"industry": doc.get("industry"),
			"annual_revenue": doc.get("annual_revenue"),
		}
	)

	organization.insert(ignore_permissions=True)

	return organization.name


@frappe.whitelist()
def create_deal(doc: dict):
	frappe.log_error("Custom create_deal called", "HAILM Override")
	deal = frappe.new_doc("CRM Deal")

	contact = doc.get("contact")

	if not contact and (
		doc.get("first_name")
		or doc.get("last_name")
		or doc.get("email")
		or doc.get("mobile_no")
	):
		contact = create_contact(doc)

	deal.update(
		{
			"organization": doc.get("organization")
			or create_school_organization(doc),
			"contacts": [{"contact": contact, "is_primary": 1}]
			if contact
			else [],
		}
	)

	doc.pop("organization", None)

	deal.update(doc)

	deal.insert(ignore_permissions=True)

	return deal.name


@frappe.whitelist()
def convert_to_deal(
	lead: str,
	doc: Document | None = None,
	deal: str | dict | None = None,
	existing_contact: str | None = None,
	existing_organization: str | None = None,
):
	frappe.log_error("Custom convert_to_deal called", "HAILM Override")
	if not (doc and doc.flags.get("ignore_permissions")) and not frappe.has_permission(
		"CRM Lead", "write", lead
	):
		frappe.throw(_("Not allowed to convert Lead to Deal"), frappe.PermissionError)

	lead = frappe.get_cached_doc("CRM Lead", lead)

	if frappe.db.exists("CRM Lead Status", "Qualified"):
		lead.db_set("status", "Qualified")

	lead.db_set("converted", 1)

	if lead.sla and frappe.db.exists("CRM Communication Status", "Replied"):
		lead.db_set("communication_status", "Replied")

	contact = lead.create_contact(existing_contact, False)

	organization = existing_organization or create_school_organization(lead)

	deal_name = lead.create_deal(contact, organization, deal)

	return deal_name

















































# import frappe
# from crm.fcrm.doctype.crm_deal.crm_deal import create_contact

# def create_school_organization(doc: dict) -> str:
# 	existing_organization = frappe.db.exists(
# 		"CRM Organization",
# 		{"custom_school_id": doc.get("custom_school_id")},
# 	)

# 	if existing_organization:
# 		return existing_organization

# 	organization = frappe.new_doc("CRM Organization")

# 	organization.update(
# 		{
# 			"organization_name": doc.get("organization_name"),
# 			"custom_school_id": doc.get("custom_school_id"),
# 			"website": doc.get("website"),
# 			"territory": doc.get("territory"),
# 			"industry": doc.get("industry"),
# 			"annual_revenue": doc.get("annual_revenue"),
# 		}
# 	)

# 	organization.insert(ignore_permissions=True)

# 	return organization.name


# def create_deal(doc: dict):
# 	deal = frappe.new_doc("CRM Deal")

# 	contact = doc.get("contact")

# 	if not contact and (
# 		doc.get("first_name")
# 		or doc.get("last_name")
# 		or doc.get("email")
# 		or doc.get("mobile_no")
# 	):
# 		contact = create_contact(doc)

# 	deal.update(
# 		{
# 			"organization": doc.get("organization")
# 			or create_school_organization(doc),
# 			"contacts": [{"contact": contact, "is_primary": 1}]
# 			if contact
# 			else [],
# 		}
# 	)

# 	doc.pop("organization", None)

# 	deal.update(doc)

# 	deal.insert(ignore_permissions=True)

# 	return deal.name


# def convert_to_deal(doc)