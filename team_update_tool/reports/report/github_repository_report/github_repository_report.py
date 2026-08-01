# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Repository URL"), "fieldname": "repository_url", "fieldtype": "Data", "width": 250},
		{"label": _("Repository Name"), "fieldname": "repository_name", "fieldtype": "Data", "width": 150},
		{"label": _("Default Branch"), "fieldname": "default_branch", "fieldtype": "Data", "width": 100},
		{"label": _("Languages"), "fieldname": "languages", "fieldtype": "Data", "width": 200},
		{"label": _("Last Commit"), "fieldname": "commit_hash", "fieldtype": "Data", "width": 100},
	]

	data = frappe.db.sql("""
		SELECT repository_url, repository_name, default_branch, languages,
			LEFT(commit_hash, 8) as commit_hash
		FROM `tabGitHub Repository`
		ORDER BY modified DESC
	""", as_dict=1)
	return columns, data
