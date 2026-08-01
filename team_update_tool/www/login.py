# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
    redirect_to = frappe.local.request.args.get("redirect-to", "")

    if frappe.session.user != "Guest":
        if redirect_to:
            frappe.local.flags.redirect_location = redirect_to
        else:
            frappe.local.flags.redirect_location = "/team_update_tool/dashboard"
        raise frappe.Redirect

    context.no_header = True
    context.title = _("Login")
    context.redirect_to = redirect_to


@frappe.whitelist(allow_guest=True)
def login(usr=None, pwd=None):
    from frappe.auth import LoginManager

    if not usr or not pwd:
        frappe.throw(_("Please provide email and password"), frappe.AuthenticationError)

    login_manager = LoginManager()
    login_manager.authenticate(usr, pwd)
    login_manager.post_login()

    if frappe.response.get("message") != "No App":
        frappe.response["message"] = "Logged In"

    return "Logged In"
