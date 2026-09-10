# Copyright (c) 2026, Raghav Kaul and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hailm.hailm.client.admin import fetch_analytics,fetch_user,fetch_csv_export
import csv
import io

def convert_user(user):
	return frappe._dict({
		"name": user.get("_id") or user.get("id"),
		"id": user.get("_id"),
		"full_name": f"{user.get('firstName').strip()} {user.get('lastName').strip()}",
		"email": user.get("email"),
		"phone": user.get("phone"),
		"phone_verified": user.get("phoneVerified"),
		"email_verified": user.get("emailVerified"),
		"role": user.get("role").replace("_", " ").title(),
		"sub_role": user.get("subRole"),
		"status": user.get("status"),
		"username": user.get("username"),
		"class_label": user.get("classLabel"),
		"class_level": user.get("classLevel"),
		"class_levels": str(user.get("classLevels")),
		"roll_no": user.get("rollNo"),
		"creation_type": user.get("creationType").replace("_"," ").title(),
		"paid": user.get("paid"),
		"paid_amount": user.get("paidAmount"),
		"olympiad_exam_slots": user.get("olympiadExamSlots"),
		"state_exam_1": user.get("stateExam1"),
		"state_exam_2": user.get("stateExam2"),
		"national_exam": user.get("nationalExam"),
		"foundation_completion": user.get("foundationCompletion"),
		"intermediate_completion": user.get("intermediateCompletion"),
		"advanced_completion": user.get("advancedCompletion"),
		"course_count": user.get("courseCount"),
		"last_active_at": user.get("lastActiveAt"),
		"last_login_at": user.get("lastLoginAt"),
		"created_at": user.get("createdAt"),
		"school": user.get("tenantId"),
		"school_name": user.get("schoolName"),
		"city": user.get("city"),
		"state": user.get("state"),
		"school_type": user.get("schoolType"),
		"school_status": user.get("schoolStatus")
	})

class UserAnalytics(Document):
	
	def db_insert(self, *args, **kwargs):
		raise NotImplementedError

	def load_from_db(self, *args, **kwargs):
		user = fetch_user(self.name)
		self.update(convert_user(user))
		return self

	def db_update(self, *args, **kwargs):
		raise NotImplementedError

	def delete(self, *args, **kwargs):
		raise NotImplementedError

	@staticmethod
	def get_list(filters=None, page_length=20, **kwargs):
		MAX = 100
		print(filters)
		start = kwargs.get("start")
		if start is None:
			start = kwargs.get("limit_start")
		start = int(start or 0)
		page_length = int(page_length or 20)

		base = {
			**normalize_filters(filters),
			**normalize_sorting(kwargs.get("order_by")),
		}

		if 10 <= page_length <= MAX and start % page_length == 0:
			# window lines up with a page boundary — fetch it exactly
			pages = [start // page_length + 1]
			limit = page_length
			offset = 0
		else:
			limit = MAX
			first_page = start // MAX + 1
			last_page = (start + page_length - 1) // MAX + 1
			pages = list(range(first_page, last_page + 1))
			offset = start - (first_page - 1) * MAX

		items = []
		for page in pages:
			data = fetch_analytics(params={**base, "page": page, "limit": limit})
			page_items = data.get("items") or []
			items.extend(page_items)
			if len(page_items) < limit:
				break
		# print(items[0])
		window = items[offset:offset + page_length]
		return [convert_user(user) for user in window]
	
	@staticmethod
	def get_count(filters=None, **kwargs):

		params = {
			**normalize_filters(filters),
			"page": 1,
			"limit": 10
		}
		data = fetch_analytics(params=params)
		count = data.get("total")
		return count

	@staticmethod
	def get_stats(**kwargs):
		pass
	
DEFAULTS={
	"scope": "school",
	"tenantId": None,
	"role": "all",
	"status": "all",
	"payment": None,
	"phone": None,
	"olympiad": "all",
	"classLevel": None,
	"state": None,
}

ALLOWED_OPERATORS = {
	"role": ["="],
	"status": ["="],
	"payment_filter": ["="],
	"phone": ["=", "like"],
	"olympiad_filter": ["="],
	"class_filter": ["="],
	"state": ["="],
	"school": ["="],
}

FIELD_MAP = {
	"role": "role",
	"status": "status",
	"payment_filter": "payment",
	"phone": "phone",
	"olympiad_filter": "olympiad",
	"class_filter": "classLevel",
	"state": "state",
	"school": "tenantId"
}

def normalize_filters(filters:list[list]):

	params = DEFAULTS.copy()
	if not filters:
		return params
	for _, field, operator, value in filters:
		if operator not in ["=", "like"]:
			frappe.throw(f"{operator} not supported for {field} filter")
		if operator not in ALLOWED_OPERATORS.get(field, []):
			frappe.throw(f"{operator} not supported for {field} filter")

		if field == "role":
			params[FIELD_MAP[field]] = value.lower().replace(" ", "_")
		elif field == "phone":
			params[FIELD_MAP[field]] = value.replace("%","")
		elif field == "class_filter":
			params[FIELD_MAP[field]] = value.removeprefix("Class ") if value != "Other" else 0
		elif field == "olympiad_filter":
			params[FIELD_MAP[field]] = value.lower().replace(" ", "_")
		elif field == "payment_filter":
			params[FIELD_MAP[field]] = value.lower() if value else None
		else:
			params[FIELD_MAP[field]] = value
		
	return params

SORT_MAP = {
	"full_name": "firstName",
	"email": "email",
	"phone": "phone",
	"role": "role",
	"status": "status",
	"class_level": "classLevel",
	"class_label": "classLevel",
	"created_at": "createdAt",
	"last_active_at": "lastActiveAt",
}

DEFAULT_SORT = {"sortBy": "createdAt", "sortDir": "desc"}
SORT_ALIASES = {
	"modified": "createdAt",
	"creation": "createdAt",
	"name": "createdAt",
}
def normalize_sorting(order_by=None):


	if not order_by:
		return DEFAULT_SORT.copy()

	clause = order_by.split(",")[0].strip()
	tokens = clause.split()

	if len(tokens) > 1 and tokens[-1].lower() in ("asc", "desc"):
		direction = tokens[-1].lower()
		field = " ".join(tokens[:-1])
	else:
		direction = "desc"
		field = clause

	field = field.replace("`", "").split(".")[-1]

	if field in SORT_ALIASES:
		return {"sortBy": SORT_ALIASES[field], "sortDir": direction}

	api_field = SORT_MAP.get(field)
	if not api_field:
		frappe.throw(
			f"Sorting by {frappe.bold(field)} is not supported. "
			f"Sortable fields: {', '.join(sorted(SORT_MAP))}",
			title="Unsupported Sort",
		)

	return {"sortBy": api_field, "sortDir": direction}

@frappe.whitelist()
def export_users(phone_verified=True, **kwargs):
	frappe.only_for(["System Manager"])

	params = {
		**normalize_filters(frappe.parse_json(frappe.form_dict.filters or "[]")),
		**normalize_sorting(None),
	}

	raw = fetch_csv_export(params=params)

	reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig", errors="replace")))
	if not reader.fieldnames:
		frappe.throw("Export returned no data.")
	if "Phone Verified" not in reader.fieldnames:
		frappe.throw(
			f"Export has no {frappe.bold('Phone Verified')} column. "
			f"Columns: {', '.join(reader.fieldnames)}",
			title="Cannot Filter",
		)

	out = io.StringIO()
	writer = csv.DictWriter(out, fieldnames=reader.fieldnames, extrasaction="ignore")
	writer.writeheader()

	kept = 0
	for row in reader:
		if (row.get("Phone Verified") or "").strip().casefold() == "yes":
			writer.writerow(row)
			kept += 1

	if not kept:
		frappe.throw("No users with verified phones matched these filters.")

	frappe.local.response.filename = f"verified-phones-{frappe.utils.today()}.csv"
	frappe.local.response.filecontent = out.getvalue().encode("utf-8-sig")
	frappe.local.response.type = "download"


