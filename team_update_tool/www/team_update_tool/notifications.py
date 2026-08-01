# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	context.title = _("Notifications")
	context.no_header = 1
	context.no_breadcrumbs = 1

	user = frappe.session.user
	if user == "Guest":
		frappe.local.flags.redirect_location = "/team_update_tool/login?redirect-to=/team_update_tool/notifications"
		raise frappe.Redirect

	context.full_name = frappe.utils.get_fullname(user)
	roles = frappe.get_roles(user)
	context.is_admin = "Team Update Admin" in roles or "Admin" in roles or "System Manager" in roles

	context.notifications = []

	# Get project updates for user's projects — query child table directly
	my_projects = frappe.get_all("Project",
		filters={"owner": user},
		pluck="name"
	)

	if my_projects:
		updates = frappe.db.get_all("Project Update",
			filters={"parent": ["in", my_projects]},
			fields=["name", "parent", "update_title", "update_description",
					"update_date", "updated_by"],
			order_by="update_date desc",
			limit=10
		)
		for u in updates:
			project_title = frappe.db.get_value("Project", u.parent, "project_title")
			context.notifications.append({
				"type": "update",
				"title": f"Update on \"{project_title}\": {u.update_title}",
				"description": u.update_description or "",
				"date": u.update_date,
				"project": u.parent,
			})

	# For admin, show recent project submissions
	if context.is_admin:
		recent_projects = frappe.get_all("Project",
			fields=["name", "project_title", "owner", "creation"],
			limit=10,
			order_by="creation desc"
		)
		for p in recent_projects:
			context.notifications.append({
				"type": "submission",
				"title": f"New project submitted: \"{p.project_title}\" by {p.owner}",
				"description": "",
				"date": str(p.creation),
				"project": p.name,
			})

	# Sort by date (most recent first) and limit to latest 20
	context.notifications.sort(key=lambda n: str(n.get("date", "")), reverse=True)
	context.notifications = context.notifications[:20]
	context.total = len(context.notifications)
