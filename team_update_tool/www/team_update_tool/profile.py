# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	context.title = _("Profile")
	context.no_header = 1
	context.no_breadcrumbs = 1

	user = frappe.session.user
	if user == "Guest":
		frappe.local.flags.redirect_location = "/team_update_tool/login?redirect-to=/team_update_tool/profile"
		raise frappe.Redirect

	# Get user details
	user_doc = frappe.get_doc("User", user)
	context.user_doc = user_doc
	context.full_name = frappe.utils.get_fullname(user)
	context.email = user
	context.is_admin = "Team Update Admin" in frappe.get_roles(user) or "Admin" in frappe.get_roles(user) or "System Manager" in frappe.get_roles(user)
