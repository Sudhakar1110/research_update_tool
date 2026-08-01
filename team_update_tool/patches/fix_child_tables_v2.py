# Copyright (c) 2026, Team Update Tool Contributors
# For license information, please see license.txt

import frappe

# Child tables that were originally created without istable=1, so their DB
# tables are missing the standard child-table columns (parent/parenttype/
# parentfield/idx). Loading any parent that has one of these as a Table field
# then fails with:
#   pymysql.err.OperationalError: (1054, "Unknown column 'parent' in 'WHERE'")
#
# v2: registered under a NEW patch name because the original
# `fix_child_tables` patch was recorded in the Patch Log on sites even though
# it failed, so plain `bench migrate` will never re-run it.
CHILD_TABLES = [
    "Team Member",
    "Project Technology",
    "Project Files",
    "Project Screenshots",
    "Project Update",
]


def execute():
    """Add parent/parenttype/parentfield/idx columns to child tables that were
    created without istable=1 (fixes 'Unknown column parent' errors)."""
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
    """Add parent/parenttype/parentfield/idx to a single child table if missing.

    NOTE: frappe.db.table_exists() and frappe.db.has_column() expect the
    DOCTYPE name (e.g. "Team Member"), NOT the raw table name (e.g.
    "tabTeam Member"). Passing the raw table name makes get_table_columns()
    raise TableMissingError(('DocType', 'tabTeam Member')).
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
    # sql_ddl() commits first so the ALTER can never trip v15's
    # ImplicitCommitError (DDL while a transaction has pending writes).
    db_table = f"tab{table_name}"
    for col_def in columns_to_add:
        sql = f"ALTER TABLE `{db_table}` ADD COLUMN {col_def}"
        frappe.db.sql_ddl(sql)
    frappe.db.commit()

    added = ", ".join(c.split()[0] for c in columns_to_add)
    print(f"  ✓ {table_name}: Added columns ({added})")

    # Invalidate Frappe's table-metadata cache so it sees the new columns.
    # v15 caches table columns in a redis hash keyed by the TABLE name.
    try:
        frappe.cache.hdel("table_columns", db_table)
    except Exception:
        pass
    try:
        frappe.cache.delete_value(f"table_columns::{db_table}")
    except Exception:
        pass
    try:
        frappe.clear_cache(doctype=table_name)
    except Exception:
        pass

    # Keep the DocType's istable flag in sync so Frappe treats it as a child table.
    if frappe.db.exists("DocType", table_name):
        frappe.db.set_value("DocType", table_name, "istable", 1)
        frappe.db.commit()
