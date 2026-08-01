# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	context.title = _("My Projects")
	context.no_header = 1
	context.no_breadcrumbs = 1

	user = frappe.session.user
	if user == "Guest":
		frappe.local.flags.redirect_location = "/team_update_tool/login?redirect-to=/team_update_tool/my_projects"
		raise frappe.Redirect

	roles = frappe.get_roles(user)
	is_admin = "Team Update Admin" in roles or "Admin" in roles or "System Manager" in roles
	is_viewer = ("Team Update Viewer" in roles or "View-Only User" in roles) and not is_admin

	# For admin/team members: show owned projects
	# For view-only users: show all projects (since we removed status filtering)
	if is_viewer:
		# View-only users can see all projects (no status restriction)
		context.projects = frappe.get_all("Project",
			fields=["name", "project_title", "status", "team", "priority",
					"project_category", "creation", "completion_date", "owner"],
			order_by="modified desc"
		)
	else:
		# Admin and team members: show owned projects
		context.projects = frappe.get_all("Project",
			filters={"owner": user},
			fields=["name", "project_title", "status", "team", "priority",
					"project_category", "creation", "completion_date", "owner"],
			order_by="modified desc"
		)

	for p in context.projects:
		if p.status:
			s = frappe.get_cached_doc("Project Status", p.status)
			p.status_name = s.status_name
			p.status_color = s.color
		# Format creation date
		p.formatted_creation = frappe.format(p.creation, "Datetime") if p.creation else ""

	context.full_name = frappe.utils.get_fullname(user)
	context.is_admin = is_admin
	context.is_viewer = is_viewer
