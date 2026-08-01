# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe

no_cache = 1


def get_context(context):
	context.no_header = 1
	context.no_breadcrumbs = 1
	context.title = "Sign Out"

	if frappe.session.user != "Guest":
		frappe.local.login_manager.logout()
		frappe.db.commit()
		context.logged_out = True
	else:
		context.logged_out = True
		context.already_guest = True
