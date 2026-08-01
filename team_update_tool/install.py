# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

ROLES = [
    {
        "role_name": "Team Update Admin",
        "desk_access": 1,
        "home_page": "/team_update_tool/dashboard",
    },
    {
        "role_name": "Team Update Team Leader",
        "desk_access": 1,
        "home_page": "/team_update_tool/dashboard",
    },
    {
        "role_name": "Team Update Team Member",
        "desk_access": 1,
        "home_page": "/team_update_tool/dashboard",
    },
    {
        "role_name": "Team Update Viewer",
        "desk_access": 1,
        "home_page": "/team_update_tool/dashboard",
    },
]


def after_install():
    """Run after the app is installed on a site.

    Creates the four required roles needed by the app,
    the Team Update Tool domain, and syncs the workspace.
    """
    create_roles()
    create_team_update_domain()
    _fix_module_def_case()
    _sync_workspace_from_module()
    print("✓ Team Update Tool installed successfully.")


def create_roles():
    """Create roles if they don't already exist."""
    for role_data in ROLES:
        role_name = role_data["role_name"]
        if not frappe.db.exists("Role", role_name):
            role = frappe.get_doc(
                {
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": role_data["desk_access"],
                    "home_page": role_data.get("home_page", ""),
                }
            )
            role.insert(ignore_permissions=True, ignore_if_duplicate=True)
            print(f"  Created Role: {role_name}")
        else:
            print(f"  Role already exists: {role_name}")

    frappe.db.commit()


def create_team_update_domain():
    """Create the Team Update Tool domain for restrict_to_domain usage."""
    if not frappe.db.exists("Domain", "Team Update Tool"):
        doc = frappe.get_doc({
            "doctype": "Domain",
            "domain": "Team Update Tool",
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("  Created Domain: Team Update Tool")


def _fix_module_def_case():
    """Rename lowercase Module Defs from prior installs to capitalized names.

    The app's modules.txt previously used lowercase names (masters, transactions,
    reports) but the DocType JSONs use capitalized names (Masters, Transactions,
    Reports). This mismatch caused Module Defs to be created with lowercase names,
    preventing DocTypes from being properly mapped.

    This function renames any remaining lowercase Module Defs to their correct
    capitalized form so DocTypes get linked correctly.
    """
    rename_map = {
        "masters": "Masters",
        "transactions": "Transactions",
        "reports": "Reports",
        "team_update_tool": "Team Update Tool",
    }
    for old_name, new_name in rename_map.items():
        if not frappe.db.exists("Module Def", old_name):
            continue

        if not frappe.db.exists("Module Def", new_name):
            # Only lowercase exists — rename to capitalized
            try:
                frappe.rename_doc("Module Def", old_name, new_name, force=True)
                print(f"  Renamed Module Def: {old_name} → {new_name}")
            except Exception as e:
                print(f"  Warning: Could not rename Module Def '{old_name}': {e}")
        else:
            # Both exist — update DocType/Report references, then delete old
            try:
                # Update DocTypes that reference the lowercase Module Def
                frappe.db.set_value(
                    "DocType",
                    {"module": old_name},
                    "module",
                    new_name
                )
                # Update Reports that reference the lowercase Module Def
                frappe.db.set_value(
                    "Report",
                    {"module": old_name},
                    "module",
                    new_name
                )
                # Now delete the stale lowercase Module Def
                frappe.delete_doc("Module Def", old_name, ignore_permissions=True, force=True)
                print(f"  Deleted stale Module Def: {old_name} (re-located references to {new_name})")
            except Exception as e:
                print(f"  Warning: Could not clean up Module Def '{old_name}': {e}")

    frappe.db.commit()


def force_sync_doctypes():
    """Force sync all Team Update Tool doctypes.

    Called from hooks.py as app_setup to ensure all
    doctype JSON files are synced into the database.

    Refreshes fixture DocTypes so the DB matches the JSON
    definitions after an app update.
    """
    from frappe.modules.utils import sync_customizations

    try:
        sync_customizations("team_update_tool")
        print("  Synced Team Update Tool customizations.")
    except Exception as e:
        print(f"  Warning: Could not sync customizations: {e}")

    frappe.clear_cache()


def _sync_workspace_from_module():
    """Sync the Team Update Tool workspace from its module JSON file.

    Reads the workspace JSON from masters/workspace/team_update_tool/team_update_tool.json
    and creates or updates the Workspace record in the database.
    This is necessary because sync_customizations() does not handle
    workspace fixtures.
    """
    import json
    import os

    workspace_file = frappe.get_app_path(
        "team_update_tool", "masters", "workspace",
        "team_update_tool", "team_update_tool.json"
    )

    if not os.path.exists(workspace_file):
        print("  Warning: Workspace JSON file not found at", workspace_file)
        return

    try:
        with open(workspace_file) as f:
            workspace_data = json.load(f)

        workspace_name = workspace_data.get("workspace_name") or workspace_data.get("name")
        if not workspace_name:
            print("  Warning: Workspace JSON has no name field")
            return

        if frappe.db.exists("Workspace", workspace_name):
            # Delete existing workspace first, then recreate from JSON
            # This ensures child table data (links) is correct even if the
            # existing workspace has stale/invalid data from a prior install
            frappe.delete_doc("Workspace", workspace_name, ignore_permissions=True, force=True)
            frappe.db.commit()
            # Now create fresh from JSON
            workspace_data["doctype"] = "Workspace"
            doc = frappe.get_doc(workspace_data)
            doc.insert(ignore_permissions=True, ignore_if_duplicate=True, ignore_links=True)
            print(f"  Recreated Workspace: {workspace_name}")
        else:
            # Create workspace from JSON
            # ignore_links=True bypasses Dynamic Link validation for link_to values
            # in the links child table (link_type + link_to pairs)
            workspace_data["doctype"] = "Workspace"
            doc = frappe.get_doc(workspace_data)
            doc.insert(ignore_permissions=True, ignore_if_duplicate=True, ignore_links=True)
            print(f"  Created Workspace: {workspace_name}")

    except Exception as e:
        frappe.log_error(
            f"Error syncing workspace from module: {str(e)}",
            "_sync_workspace_from_module",
        )
        print(f"  Warning: Could not sync workspace from module: {e}")


def sync_workspace_and_notifications():
    """Sync workspace and notifications after migration.

    Ensures that custom workspaces and notification records
    are properly synced after a migrate operation.
    """
    # Fix Module Def case if needed (for sites installed before the casing fix)
    _fix_module_def_case()


    # Sync workspace from module file if it exists on disk
    _sync_workspace_from_module()

    # Sync notification fixtures by reloading from disk
    notifications = [
        "New Project Uploaded",
        "Project Approved",
        "Project Status Updated",
    ]
    for notif_name in notifications:
        if frappe.db.exists("Notification", notif_name):
            try:
                # Reload the notification from its JSON fixture
                frappe.reload_doc("team_update_tool", "notification", notif_name.lower().replace(" ", "_"))
                print(f"  Synced Notification: {notif_name}")
            except Exception as e:
                print(f"  Warning: Could not sync notification '{notif_name}': {e}")

    frappe.db.commit()
    frappe.clear_cache()
    print("✓ Workspace and notifications synced successfully.")
