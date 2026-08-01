# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
import json
import os


def execute():
    """Fix Workspace content field to prevent 'onboarding_list' AttributeError.

    The Frappe v15 Workspace.__init__() only sets self.onboarding_list when
    self.doc.content is truthy. If the content field is NULL or empty, the
    attribute is never created, causing get_onboardings() to raise:
        AttributeError: 'Workspace' object has no attribute 'onboarding_list'

    Uses frappe.db.set_value() to bypass all document-level validation
    (link validation, mandatory checks) that can fail during migration.
    """
    workspace_name = "Team Update Tool"

    if not frappe.db.exists("Workspace", workspace_name):
        print(f"Workspace '{workspace_name}' not found. Skipping.")
        return

    # Read the correct content from the fixture JSON
    app_path = frappe.get_app_path("team_update_tool")
    workspace_path = os.path.join(app_path, "masters/workspace/team_update_tool.json")

    if not os.path.exists(workspace_path):
        frappe.log_error(
            f"Workspace fixture not found at {workspace_path}",
            "fix_workspace_content",
        )
        print("Workspace fixture JSON not found. Skipping.")
        return

    with open(workspace_path, "r") as f:
        fixture_data = json.load(f)

    content = fixture_data.get("content")

    if not content:
        print("Workspace fixture has no content field. Skipping.")
        return

    # Use set_value to bypass all document-level validation
    frappe.db.set_value("Workspace", workspace_name, "content", content)
    frappe.db.commit()
    frappe.clear_cache()

    print(f"Updated Workspace '{workspace_name}' content field successfully.")
