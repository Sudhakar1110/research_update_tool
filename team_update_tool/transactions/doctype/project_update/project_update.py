# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class ProjectUpdate(Document):
	def before_insert(self):
		if not self.updated_by:
			import frappe
			self.updated_by = frappe.session.user


def get_permission_query_conditions(user):
	"""View-Only Users can only see updates for approved projects."""
	if not user:
		return ""
	import frappe
	roles = frappe.get_roles(user)
	if "Team Update Viewer" in roles or "View-Only User" in roles and "Team Update Admin" not in roles and "Admin" not in roles:
		approved_status = frappe.db.get_value("Project Status", {"status_name": "Approved"}, "name")
		if approved_status:
			return "`tabProject Update`.`status` = " + frappe.db.escape(approved_status)
	return ""
