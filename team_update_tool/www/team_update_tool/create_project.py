# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	context.title = _("Create Project")
	context.no_header = 1
	context.no_breadcrumbs = 1

	user = frappe.session.user
	if user == "Guest":
		frappe.local.flags.redirect_location = "/team_update_tool/login?redirect-to=/team_update_tool/create_project"
		raise frappe.Redirect

	roles = frappe.get_roles(user)
	is_viewer = "Team Update Viewer" in roles or "View-Only User" in roles
	is_viewer = is_viewer and ("Team Update Admin" not in roles and "Admin" not in roles and "Team Update Team Member" not in roles and "Team Member" not in roles and "System Manager" not in roles)
	if is_viewer:
		frappe.local.flags.redirect_location = "/team_update_tool/dashboard"
		raise frappe.Redirect

	context.is_admin = "Team Update Admin" in roles or "Admin" in roles or "System Manager" in roles
	context.is_team_member = "Team Update Team Member" in roles or "Team Member" in roles
	context.full_name = frappe.utils.get_fullname(user)

	# Get lookup data for forms
	context.teams = frappe.get_all("Team",
		filters={"is_active": 1},
		fields=["name", "team_name"]
	)
	context.categories = frappe.get_all("Project Category",
		fields=["name", "category_name"]
	)
	context.statuses = frappe.get_all("Project Status",
		fields=["name", "status_name", "color"]
	)
	context.technologies = frappe.get_all("Technology",
		fields=["name", "technology_name"]
	)

	# Default to create mode
	context.edit_project = None
	context.edit_technologies = []

	# If editing existing project
	edit_name = frappe.form_dict.get("edit")
	if edit_name:
		try:
			project = frappe.get_doc("Project", edit_name)
			if project.owner != user and not context.is_admin:
				frappe.local.flags.redirect_location = "/team_update_tool/dashboard"
				raise frappe.Redirect
			context.edit_project = project
			context.edit_technologies = [t.technology for t in project.technologies or []]
			context.title = _("Edit Project")
		except frappe.DoesNotExistError:
			pass
