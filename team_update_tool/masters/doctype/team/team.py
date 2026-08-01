# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Team(Document):
	def validate(self):
		if self.team_lead and not frappe.db.exists("User", self.team_lead):
			frappe.throw("Team Lead must be a valid User.")
