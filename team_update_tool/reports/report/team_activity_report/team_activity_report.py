# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Team"), "fieldname": "team", "fieldtype": "Link", "options": "Team", "width": 150},
		{"label": _("Project"), "fieldname": "project_title", "fieldtype": "Data", "width": 200},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Link", "options": "Project Status", "width": 100},
		{"label": _("Priority"), "fieldname": "priority", "fieldtype": "Data", "width": 80},
		{"label": _("Completion Date"), "fieldname": "completion_date", "fieldtype": "Date", "width": 100},
	]

	conditions = []
	params = {}
	if filters:
		if filters.get("team"):
			conditions.append("team = %(team)s")
			params["team"] = filters["team"]
		if filters.get("from_date"):
			conditions.append("completion_date >= %(from_date)s")
			params["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			conditions.append("completion_date <= %(to_date)s")
			params["to_date"] = filters["to_date"]

	where = " AND ".join(conditions) if conditions else "1=1"

	data = frappe.db.sql(f"""
		SELECT team, project_title, status, priority, completion_date
		FROM `tabProject`
		WHERE {where}
		ORDER BY team, modified DESC
	""", params, as_dict=1)
	return columns, data
