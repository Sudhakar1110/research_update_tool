# Copyright (c) 2026, Team Update Tool Contributors
# For license information, please see license.txt

import frappe
from frappe import _

# Child tables that were missing istable=1 when initially created
# These tables need parent/parenttype/parentfield columns added
CHILD_TABLES = [
    "Team Member",
    "Project Technology",
    "Project Files",
    "Project Screenshots",
    "Project Update",
]


def execute():
    """Add parent/parenttype/parentfield columns to child tables that were
    originally created without istable=1, causing 'Unknown column parent' errors."""
    
    for table_name in CHILD_TABLES:
        try:
            _ensure_child_table_columns(table_name)
        except Exception as e:
            frappe.log_error(
                f"Failed to add parent columns to {table_name}: {e}",
                "Team Update Tool Patch",
            )
            print(f"  Warning: Could not add parent columns to {table_name}: {e}")


def _ensure_child_table_columns(table_name):
    """Add parent/parenttype/parentfield columns to a single child table if missing."""
    db_table = f"tab{table_name}"
    
    # Check which columns are missing
    # frappe.db.get_table_columns() returns lowercase column names
    existing_columns = frappe.db.get_table_columns(db_table)
    
    columns_to_add = []
    if "parent" not in existing_columns:
        columns_to_add.append("parent varchar(255)")
    if "parenttype" not in existing_columns:
        columns_to_add.append("parenttype varchar(255)")
    if "parentfield" not in existing_columns:
        columns_to_add.append("parentfield varchar(255)")
    
    if not columns_to_add:
        print(f"  ✓ {table_name}: parent columns already exist")
        return
    
    # Add missing columns
    for col_def in columns_to_add:
        sql = f"ALTER TABLE `{db_table}` ADD COLUMN {col_def} DEFAULT NULL"
        frappe.db.sql(sql)
    
    added = ", ".join(c.split()[0] for c in columns_to_add)
    print(f"  ✓ {table_name}: Added columns ({added})")
    
    # Clear Frappe's table metadata cache so it sees the new columns
    frappe.cache().delete_value(f"table_columns::{db_table}")
    frappe.clear_cache(doctype=table_name)
    
    # Also update the DocType's istable flag in tabDocType
    if frappe.db.exists("DocType", table_name):
        frappe.db.set_value("DocType", table_name, "istable", 1)
