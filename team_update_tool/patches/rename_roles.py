# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe


def execute():
    """Rename old role names to new SOP-aligned role names.

    This patch handles migration from the legacy role naming scheme
    (Admin, Team Member, View-Only User) to the new scheme
    (Team Update Admin, Team Update Team Leader, Team Update Team Member, Team Update Viewer).

    For each old role:
      1. Create the new role if it doesn't already exist
      2. Copy all DocType permission records from old role → new role
      3. Update Notification Log recipient references
      4. Delete the old role
    """
    role_mapping = {
        "Admin": "Team Update Admin",
        "Team Member": "Team Update Team Member",
        "View-Only User": "Team Update Viewer",
    }

    # Also create Team Update Team Leader if it doesn't exist
    _ensure_role_exists("Team Update Team Leader", desk_access=1)

    for old_role, new_role in role_mapping.items():
        if not frappe.db.exists("Role", old_role):
            print(f"  Skipping '{old_role}' — does not exist.")
            continue

        print(f"  Migrating role: '{old_role}' → '{new_role}'")

        # 1. Ensure new role exists
        _ensure_role_exists(new_role)

        # 2. Copy DocType permissions from old role to new role
        _copy_permissions(old_role, new_role)

        # 3. Update Notification recipient roles
        _update_notification_recipients(old_role, new_role)

        # 4. Update Notification Log references
        _update_notification_logs(old_role, new_role)

        # 5. Update Has Role records (user assignments)
        _transfer_user_assignments(old_role, new_role)

        # 6. Delete old role
        try:
            frappe.delete_doc("Role", old_role, force=True)
            print(f"    Deleted old role: '{old_role}'")
        except Exception as e:
            print(f"    Warning: Could not delete '{old_role}': {e}")

    frappe.db.commit()
    frappe.clear_cache()
    print("✓ Roles migrated successfully.")


def _ensure_role_exists(role_name, desk_access=1):
    """Create a role if it doesn't exist."""
    if not frappe.db.exists("Role", role_name):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name,
            "desk_access": desk_access,
        })
        role.insert(ignore_permissions=True)
        print(f"    Created role: '{role_name}'")


def _copy_permissions(old_role, new_role):
    """Copy DocType permission records from old role to new role."""
    perms = frappe.get_all(
        "DocPerm",
        filters={"role": old_role},
        fields=["*"],
    )
    if not perms:
        print(f"    No DocPerm records found for '{old_role}'")
        return

    # Check if these permissions already exist for the new role
    existing_perms = frappe.get_all(
        "DocPerm",
        filters={"role": new_role},
        fields=["parent", "parenttype", "permlevel", "read", "write", "create", "delete",
                "submit", "cancel", "amend", "report", "export", "import", "print", "email",
                "share"],
    )

    existing_keys = {
        (p["parent"], p.get("permlevel", 0))
        for p in existing_perms
    }

    copied = 0
    skipped = 0
    for perm in perms:
        key = (perm["parent"], perm.get("permlevel", 0))
        if key in existing_keys:
            skipped += 1
            continue

        new_perm = frappe.get_doc({
            "doctype": "DocPerm",
            "parent": perm["parent"],
            "parenttype": perm.get("parenttype", "DocType"),
            "parentfield": perm.get("parentfield", "permissions"),
            "role": new_role,
            "permlevel": perm.get("permlevel", 0),
            "read": perm.get("read", 0),
            "write": perm.get("write", 0),
            "create": perm.get("create", 0),
            "delete": perm.get("delete", 0),
            "submit": perm.get("submit", 0),
            "cancel": perm.get("cancel", 0),
            "amend": perm.get("amend", 0),
            "report": perm.get("report", 0),
            "export": perm.get("export", 0),
            "import": perm.get("import", 0),
            "print": perm.get("print", 0),
            "email": perm.get("email", 0),
            "share": perm.get("share", 0),
        })
        new_perm.insert(ignore_permissions=True, ignore_links=True)
        copied += 1

    print(f"    Copied {copied} permissions (skipped {skipped} duplicates)")


def _update_notification_recipients(old_role, new_role):
    """Update Notification recipient records referencing old role."""
    try:
        frappe.db.sql("""
            UPDATE `tabNotification Recipient`
            SET receiver_by_role = %s
            WHERE receiver_by_role = %s
        """, (new_role, old_role))
        print(f"    Updated Notification Recipients: '{old_role}' → '{new_role}'")
    except Exception as e:
        print(f"    Warning updating notification recipients: {e}")


def _update_notification_logs(old_role, new_role):
    """Update Notification Log references."""
    try:
        frappe.db.sql("""
            UPDATE `tabNotification Log`
            SET `type` = %s
            WHERE `type` = %s
        """, (new_role, old_role))
    except Exception:
        pass  # Non-critical


def _transfer_user_assignments(old_role, new_role):
    """Transfer user role assignments from old role to new role."""
    users = frappe.get_all(
        "Has Role",
        filters={"role": old_role},
        fields=["parent", "parenttype", "parentfield"],
    )

    if not users:
        print(f"    No users assigned to '{old_role}'")
        return

    transferred = 0
    for user_ref in users:
        # Check if user already has the new role
        if frappe.db.exists("Has Role", {
            "role": new_role,
            "parent": user_ref["parent"],
        }):
            continue

        new_has_role = frappe.get_doc({
            "doctype": "Has Role",
            "parent": user_ref["parent"],
            "parenttype": user_ref.get("parenttype", "User"),
            "parentfield": user_ref.get("parentfield", "roles"),
            "role": new_role,
        })
        new_has_role.insert(ignore_permissions=True, ignore_links=True)
        transferred += 1

        # Remove old role assignment
        try:
            frappe.db.delete("Has Role", {
                "role": old_role,
                "parent": user_ref["parent"],
            })
        except Exception:
            pass

    print(f"    Transferred {transferred} user(s) to '{new_role}'")
