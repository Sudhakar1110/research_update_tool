# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe


def execute():
    """Fix Project Update table to have child table columns."""
    if frappe.db.table_exists("Project Update"):
        columns_to_add = [
            ("parent", "VARCHAR(140)"),
            ("parentfield", "VARCHAR(140)"),
            ("parenttype", "VARCHAR(140)"),
            ("idx", "INT DEFAULT 0"),
        ]
        
        for col_name, col_type in columns_to_add:
            if not frappe.db.has_column("Project Update", col_name):
                frappe.db.sql(f"""
                    ALTER TABLE `tabProject Update` 
                    ADD COLUMN `{col_name}` {col_type}
                """)
        
        frappe.db.commit()
        
        # Reload the doctype to sync with schema
        frappe.reload_doc("team_update_tool", "doctype", "project_update")
