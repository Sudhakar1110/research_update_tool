# Copyright (c) 2026, Team Update Tool Contributors
# For license information, please see license.txt

import frappe
from frappe.model.naming import make_autoname

# Mapping of doctypes and their naming series patterns
# Records whose names contain these literal patterns are considered "unresolved"
# and need to be renamed with a proper resolved name.
DOCTYPE_PATTERNS = {
    "GitHub Repository": {
        "prefix": "GR",
        "raw_pattern": "GR-.YYYY.-.#####",
        "naming_autoname": "GR-.YYYY.-.#####",
    },
    "Project Milestone": {
        "prefix": "MS",
        "raw_pattern": "MS-.YYYY.-.#####",
        "naming_autoname": "MS-.YYYY.-.#####",
    },
    "Project Time Log": {
        "prefix": "TL",
        "raw_pattern": "TL-.YYYY.-.#####",
        "naming_autoname": "TL-.YYYY.-.#####",
    },
}


def execute():
    """Fix existing records that have unresolved naming series names.

    When the naming series pattern format:XXX-.YYYY.-.##### failed to resolve,
    the raw pattern literal was used as the document name. This patch finds
    those records and renames them with properly generated names.
    """
    fixed_count = 0

    for doctype, config in DOCTYPE_PATTERNS.items():
        if not frappe.db.exists("DocType", doctype):
            print(f"  Skipping '{doctype}' - DocType does not exist.")
            continue

        count = _fix_doctype(doctype, config)
        fixed_count += count

    frappe.db.commit()
    frappe.clear_cache()

    if fixed_count:
        print(f"✓ Fixed {fixed_count} records with unresolved naming series names.")
    else:
        print("✓ No records with unresolved naming series names found.")


def _fix_doctype(doctype, config):
    """Find and rename records with unresolved names for a given doctype."""
    raw_pattern = config["raw_pattern"]
    naming_autoname = config["naming_autoname"]

    # Find records whose name is the raw unresolved pattern literal.
    # When the naming series failed to resolve, the raw pattern string
    # (e.g. 'GR-.YYYY.-.#####') was used as the document name.
    records = frappe.db.sql(
        f"""SELECT name FROM `tab{doctype}` WHERE name = %s""",
        raw_pattern,
        as_dict=1,
    )

    if not records:
        return 0

    fixed = 0
    for record in records:
        try:
            # Generate a proper resolved name
            new_name = make_autoname(naming_autoname)
        except Exception:
            # Fallback to hash-based unique name
            new_name = f"{config['prefix']}-{frappe.generate_hash(length=10)}"

        try:
            # Rename the document in the database directly
            # Use frappe.rename_doc to properly update all linked references
            frappe.rename_doc(
                doctype,
                record["name"],
                new_name,
                force=True,
                ignore_permissions=True,
                show_alert=False,
                merge=False,
            )
            fixed += 1
            print(f"  Renamed '{doctype}' {record['name']} → {new_name}")
        except Exception as e:
            frappe.log_error(
                f"Failed to rename {doctype} record {record['name']}: {e}",
                "fix_naming_series",
            )
            print(f"  Warning: Could not rename '{doctype}' {record['name']}: {e}")

    return fixed
