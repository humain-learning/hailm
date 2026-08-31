# Copyright (c) 2026, Raghav Kaul and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hailm.hailm.client.admin import _headers,fetch_analytics

def convert_user(user):
	return frappe._dict({
		"name": user["id"],
		"full_name": f"{user.get('firstName').strip()} {user.get('lastName').strip()}",
		"email": user.get("email"),
		"phone": user.get("phone"),
		"phone_verified": user.get("phoneVerified"),
		"email_verified": user.get("emailVerified"),
		"role": user.get("role"),
		"sub_role": user.get("subRole"),
		"status": user.get("status"),
		"username": user.get("username"),
		"class_label": user.get("classLabel"),
		"class_level": user.get("classLevel"),
		"class_levels": user.get("classLevels"),
		"roll_no": user.get("rollNo"),
		"creation_type": user.get("creationType"),
		"paid": user.get("paid"),
		"paid_amount": user.get("paidAmount"),
		"olympiad_exam_slots": user.get("olympiadExamSlots"),
		"state_exam_1": user.get("stateExam1"),
		"state_exam_2": user.get("stateExam2"),
		"national_exam": user.get("nationalExam"),
		"foundation_completion": user.get("foundationCompletion"),
		"course_count": user.get("courseCount"),
		"last_active_at": user.get("lastActiveAt"),
		"created_at": user.get("createdAt"),
		"tenant_id": user.get("tenantId"),
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
		raise NotImplementedError

	def db_update(self, *args, **kwargs):
		raise NotImplementedError

	def delete(self, *args, **kwargs):
		raise NotImplementedError

	@staticmethod
	def get_list(filters=None, page_length=20, **kwargs):
		filters = filters or {}
		print(filters)
		print(page_length)
		print(kwargs.get("start"))

		page = (kwargs.get("start", 0)//page_length) + 1
		params = {
			"scope": "school",	
			"role": "all",
			"status": "all",
			"payment": "all",
			"olympiad": "all",
			"sortBy": "createdAt",
			"sortDir": "desc",
			"page": page,
			"limit": page_length
		}
		data = fetch_analytics(params=params)
		users = [convert_user(user) for user in data.get("items",[])]
		# print(users)
		return users
	
	@staticmethod
	def get_count(filters=None, **kwargs):
		filters = filters or {}
		params = {
			"scope": "school",	
			"role": "all",
			"status": "all",
			"payment": "all",
			"olympiad": "all",
			"sortBy": "createdAt",
			"sortDir": "desc",
			"page": 1,
			"limit": 1
		}
		data = fetch_analytics(params=params)
		count = data.get("total")
		return count

	@staticmethod
	def get_stats(**kwargs):
		pass


BASE_URL="https://api.ailiteracymission.org/api/v1/school-dashboard/admin/user-analytics"


def normalize_filters(filters:list[list]):
	
	defaults={
		"role": "all",
		"status": "all",
		"payment": "all",
		"olympiad": "all",
		"sortBy": "createdAt",
		"sortDir": "desc",
		"page": 1,
		"limit": 25
	}

	params = {
		key: filters.get(key) or default
		for key,default in defaults.items()
	}

	params["scope"] = "school"
	params["tenantId"] = filters.get("schoolId")

	return params

def extract_users(data):
	return data.get("items")

@frappe.whitelist()
def get_user_analytics(filters:dict|None=None):
	filters = filters or {}

	filters = normalize_filters(filters)

	data = fetch_analytics(filters=filters)
	
	users = extract_users(data)

	return users