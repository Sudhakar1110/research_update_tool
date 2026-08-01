# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_current_user():
    """Return information about the currently logged-in user.

    Called by the dashboard JS (team_update_tool.api.auth.get_current_user).
    Returns a dict with:
      - guest: whether the user is a guest
      - full_name: the user's full name
      - email: the user's email
      - is_admin: whether the user has admin-level access
    """
    user = frappe.session.user
    if user == "Guest":
        return {
            "guest": True,
            "full_name": "Guest",
            "email": "",
            "is_admin": False,
        }

    roles = frappe.get_roles(user)
    full_name = frappe.utils.get_fullname(user)

    return {
        "guest": False,
        "full_name": full_name,
        "email": user,
        "is_admin": "System Manager" in roles or "Team Update Admin" in roles,
    }
