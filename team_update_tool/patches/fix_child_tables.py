# Copyright (c) 2026, Team Update Tool Contributors
# For license information, please see license.txt

import frappe
from frappe import _

# Child tables that were missing istable=1 when initially created
# These tables need parent/parenttype/parentfield/idx columns added
CHILD_TABLES = [
    "Team Member",
    "Project Technology",
    "Project Files",
    "Project Screenshots",
    "Project Update",
]


def execute():
    """Add parent/parenttype/parentfield/idx columns to child tables that were
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
    """Add parent/parenttype/parentfield/idx columns to a single child table if missing.

    NOTE: frappe.db.table_exists(), frappe.db.has_column() and
    frappe.db.get_table_columns() expect the DOCTYPE name (e.g. "Team Member"),
    NOT the raw table name (e.g. "tabTeam Member").
    """
    if not frappe.db.table_exists(table_name):
        print(f"  ! {table_name}: table does not exist, skipping")
        return

    columns_to_add = []
    if not frappe.db.has_column(table_name, "parent"):
        columns_to_add.append("parent varchar(140)")
    if not frappe.db.has_column(table_name, "parenttype"):
        columns_to_add.append("parenttype varchar(140)")
    if not frappe.db.has_column(table_name, "parentfield"):
        columns_to_add.append("parentfield varchar(140)")
    if not frappe.db.has_column(table_name, "idx"):
        columns_to_add.append("idx int default 0")

    if not columns_to_add:
        print(f"  ✓ {table_name}: child table columns already exist")
        return

    # Each col_def is a complete column definition (varchar columns default to
    # NULL naturally; idx carries its own default). Do NOT append "DEFAULT NULL"
    # here - it would produce invalid SQL for "idx int default 0".
    db_table = f"tab{table_name}"
    for col_def in columns_to_add:
        sql = f"ALTER TABLE `{db_table}` ADD COLUMN {col_def}"
        frappe.db.sql(sql)
    frappe.db.commit()

    added = ", ".join(c.split()[0] for c in columns_to_add)
    print(f"  ✓ {table_name}: Added columns ({added})")

    # Clear Frappe's table metadata cache so it sees the new columns
    try:
        frappe.cache().delete_value(f"table_columns::{table_name}")
        frappe.cache().delete_value(f"table_columns::{db_table}")
    except Exception:
        pass
    try:
        frappe.clear_cache(doctype=table_name)
    except Exception:
        pass

    # Also update the DocType's istable flag in tabDocType
    if frappe.db.exists("DocType", table_name):
        frappe.db.set_value("DocType", table_name, "istable", 1)
        frappe.db.commit()
