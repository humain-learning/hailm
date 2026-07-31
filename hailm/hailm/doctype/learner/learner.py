# Copyright (c) 2026, Raghav Kaul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Learner(Document):
	def before_save(self):
		self.full_name = f"{self.first_name or ''} {self.last_name or ''}"