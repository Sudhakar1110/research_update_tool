# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	"""Home page context with public data."""
	context.title = _("Team Update Tool")
	context.no_header = 1
	context.no_breadcrumbs = 1

	# Get public stats
	approved = frappe.db.get_value("Project Status", {"status_name": "Approved"}, "name")
	filters = {}
	if approved:
		filters["status"] = approved

	context.total_projects = frappe.db.count("Project", filters=filters)
	context.total_teams = frappe.db.count("Team", filters={"is_active": 1})
	context.total_technologies = frappe.db.count("Technology")

	# Featured projects
	context.featured_projects = frappe.get_all("Project",
		filters=filters,
		fields=["name", "project_title", "status", "team", "project_category", "creation"],
		limit=6,
		order_by="creation desc"
	)

	# Enrich with names
	for p in context.featured_projects:
		if p.status:
			s = frappe.get_cached_doc("Project Status", p.status)
			p.status_name = s.status_name
			p.status_color = s.color

	# Categories and technologies
	context.categories = frappe.get_all("Project Category",
		fields=["name", "category_name", "description"]
	)
	context.technologies_list = frappe.get_all("Technology",
		fields=["name", "technology_name", "description"]
	)

	# User info
	user = frappe.session.user
	context.is_logged_in = user != "Guest"
	if context.is_logged_in:
		roles = frappe.get_roles(user)
		context.is_admin = "Team Update Admin" in roles or "Admin" in roles or "System Manager" in roles
		context.is_viewer = ("Team Update Viewer" in roles or "View-Only User" in roles) and not ("Team Update Admin" in roles or "Admin" in roles or "System Manager" in roles)
		context.full_name = frappe.utils.get_fullname(user)
