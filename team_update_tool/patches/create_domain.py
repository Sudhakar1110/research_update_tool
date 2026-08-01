# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Create Team Update Tool domain for restrict_to_domain usage."""
	if not frappe.db.exists("Domain", "Team Update Tool"):
		doc = frappe.get_doc({
			"doctype": "Domain",
			"domain": "Team Update Tool",
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		print("Created Domain: Team Update Tool")
