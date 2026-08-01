# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	context.title = _("Dashboard")
	context.no_header = 1
	context.no_breadcrumbs = 1

	user = frappe.session.user
	if user == "Guest":
		frappe.local.flags.redirect_location = "/team_update_tool/login?redirect-to=/team_update_tool/dashboard"
		raise frappe.Redirect

	roles = frappe.get_roles(user)
	is_admin = "Team Update Admin" in roles or "Admin" in roles or "System Manager" in roles
	is_manager = bool(
		"System Manager" in roles
		or "Team Update Admin" in roles
		or "Team Update Team Leader" in roles
		or "Admin" in roles
	)
	is_viewer = ("Team Update Viewer" in roles or "View-Only User" in roles) and not is_admin

	context.is_admin = is_admin
	context.is_viewer = is_viewer
	context.full_name = frappe.utils.get_fullname(user)

	# Build base filters
	base_filters = {}
	if is_viewer:
		approved = frappe.db.get_value("Project Status", {"status_name": "Approved"}, "name")
		if approved:
			base_filters["status"] = approved
	elif not is_manager:
		# Regular team members see only their own projects
		base_filters["owner"] = user

	# Stats
	context.total_projects = frappe.db.count("Project", filters=base_filters if base_filters else None)
	context.total_teams = frappe.db.count("Team", filters={"is_active": 1})
	context.my_projects = frappe.db.count("Project", filters={"owner": user})

	# Status counts
	context.status_counts = []
	statuses = frappe.get_all("Project Status", fields=["name", "status_name", "color"])
	for s in statuses:
		f = {**base_filters, "status": s.name}
		count = frappe.db.count("Project", filters=f)
		if count:
			context.status_counts.append({
				"name": s.status_name,
				"count": count,
				"color": s.color,
			})

	# Your recent projects
	context.recent_projects = frappe.get_all("Project",
		filters={"owner": user},
		fields=["name", "project_title", "status", "creation"],
		limit=5,
		order_by="modified desc"
	)
	for p in context.recent_projects:
		if p.status:
			s = frappe.get_cached_doc("Project Status", p.status)
			p.status_name = s.status_name
			p.status_color = s.color

	# All recent projects (for admin)
	if is_admin:
		context.all_recent = frappe.get_all("Project",
			fields=["name", "project_title", "status", "owner", "creation"],
			limit=5,
			order_by="modified desc"
		)
		for p in context.all_recent:
			if p.status:
				s = frappe.get_cached_doc("Project Status", p.status)
				p.status_name = s.status_name
				p.status_color = s.color

	# Get notifications for the dashboard
	context.notifications = get_user_notifications(user, is_admin)
	context.unread_count = len([n for n in context.notifications if not n.get("read")])


def get_user_notifications(user, is_admin=False):
	"""Get notifications for the dashboard display."""
	notifications = []
	
	try:
		# Get recent project submissions (for admin)
		if is_admin:
			recent_projects = frappe.get_all("Project",
				fields=["name", "project_title", "owner", "creation", "status"],
				limit=10,
				order_by="creation desc"
			)
			for p in recent_projects:
				status_name = ""
				if p.status:
					try:
						s = frappe.get_cached_doc("Project Status", p.status)
						status_name = s.status_name if hasattr(s, 'status_name') else p.status
					except:
						status_name = p.status
				
				notifications.append({
					"type": "new_project",
					"title": f"New Project: {p.project_title}",
					"message": f"Submitted by {p.owner}",
					"status": status_name,
					"date": str(p.creation) if p.creation else "",
					"project": p.name,
					"read": False,
					"icon": "fa-plus-circle",
					"color": "#22c55e"
				})
		
		# Get notification logs
		try:
			notification_logs = frappe.get_all("Notification Log",
				filters={"for_user": user},
				fields=["name", "subject", "message", "creation", "reference_doctype", "reference_name", "read"],
				limit=10,
				order_by="creation desc"
			)
			for log in notification_logs:
				notifications.append({
					"type": "notification_log",
					"title": log.subject or "Notification",
					"message": log.message or "",
					"date": str(log.creation) if log.creation else "",
					"project": log.reference_name,
					"read": log.read,
					"icon": "fa-bell",
					"color": "#3b82f6"
				})
		except Exception as e:
			frappe.log_error(f"Error fetching notification logs: {str(e)}", "Dashboard Notifications")
		
		# Sort by date (newest first)
		notifications.sort(key=lambda n: n.get("date", ""), reverse=True)
		
		# Limit to 10 most recent
		notifications = notifications[:10]
		
	except Exception as e:
		frappe.log_error(f"Error fetching dashboard notifications: {str(e)}", "Dashboard Notifications")
	
	return notifications
