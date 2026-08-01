# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Project"), "fieldname": "project_title", "fieldtype": "Data", "width": 200},
		{"label": _("Team"), "fieldname": "team", "fieldtype": "Link", "options": "Team", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Link", "options": "Project Status", "width": 100},
		{"label": _("Priority"), "fieldname": "priority", "fieldtype": "Data", "width": 80},
		{"label": _("Category"), "fieldname": "project_category", "fieldtype": "Link", "options": "Project Category", "width": 120},
		{"label": _("GitHub"), "fieldname": "github_repository", "fieldtype": "Link", "options": "GitHub Repository", "width": 180},
		{"label": _("Completion Date"), "fieldname": "completion_date", "fieldtype": "Date", "width": 100},
	]
	data = frappe.db.sql("""
		SELECT project_title, team, status, priority, project_category,
			github_repository, completion_date
		FROM `tabProject`
		ORDER BY modified DESC
	""", as_dict=1)
	return columns, data
