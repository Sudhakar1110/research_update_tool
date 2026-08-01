# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	context.title = _("Sign In")
	context.no_header = 1
	context.no_breadcrumbs = 1

	redirect_to = frappe.local.request.args.get("redirect-to", "/team_update_tool/dashboard")

	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = redirect_to
		raise frappe.Redirect

	context.redirect_to = redirect_to
