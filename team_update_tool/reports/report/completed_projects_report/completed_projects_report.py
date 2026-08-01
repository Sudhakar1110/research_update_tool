# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Project"), "fieldname": "project_title", "fieldtype": "Data", "width": 200},
		{"label": _("Team"), "fieldname": "team", "fieldtype": "Link", "options": "Team", "width": 120},
		{"label": _("Category"), "fieldname": "project_category", "fieldtype": "Link", "options": "Project Category", "width": 120},
		{"label": _("Completed On"), "fieldname": "completion_date", "fieldtype": "Date", "width": 100},
		{"label": _("Approved By"), "fieldname": "approved_by", "fieldtype": "Link", "options": "User", "width": 120},
		{"label": _("GitHub"), "fieldname": "github_repository", "fieldtype": "Link", "options": "GitHub Repository", "width": 180},
	]

	approved_status = frappe.db.get_value("Project Status", {"status_name": "Approved"}, "name")

	conditions = []
	params = {}
	if filters:
		if filters.get("from_date"):
			conditions.append("completion_date >= %(from_date)s")
			params["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			conditions.append("completion_date <= %(to_date)s")
			params["to_date"] = filters["to_date"]

	where = " AND ".join(conditions) if conditions else "1=1"

	if approved_status:
		where += f" AND status = {frappe.db.escape(approved_status)}"

	data = frappe.db.sql(f"""
		SELECT project_title, team, project_category, completion_date, approved_by, github_repository
		FROM `tabProject`
		WHERE {where}
		ORDER BY completion_date DESC
	""", params, as_dict=1)
	return columns, data
