# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Set restrict_to_domain on child table DocTypes to hide them from module sidebar."""
	child_tables = [
		"Team Member",
		"Project Update",
		"Project Files",
		"Project Screenshots",
		"Project Technology",
	]

	for dt_name in child_tables:
		if frappe.db.exists("DocType", dt_name):
			frappe.db.set_value("DocType", dt_name, "restrict_to_domain", "Team Update Tool")
			print(f"Set restrict_to_domain on {dt_name}")

	frappe.db.commit()
	frappe.clear_cache()
