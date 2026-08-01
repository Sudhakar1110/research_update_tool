app_name = "team_update_tool"
app_title = "Team Update Tool"
app_publisher = "Team Update Tool Contributors"
app_description = "Team Update Tool - Track completed team projects with GitHub integration and role-based access control for ERPNext v15+"
app_email = "balaji-001-gif@users.noreply.github.com"
app_license = "MIT"
app_icon = "octicon octicon-repo"
app_color = "#2E8B57"

required_apps = ["erpnext"]

app_include_css = "/assets/team_update_tool/css/team_update_tool.css"
website_include_js = "/assets/team_update_tool/js/team_update_tool.js"

after_install = "team_update_tool.install.after_install"
app_setup = "team_update_tool.install.force_sync_doctypes"
after_migrate = "team_update_tool.install.sync_workspace_and_notifications"

website_route_rules = [
	# Dynamic route for project detail page (path-based URL)
	{"from_route": "/team_update_tool/project/<name>", "to_route": "team_update_tool/project"},
]

fixtures = [
	{"dt": "Role", "filters": [["role_name", "in", ["Team Update Admin", "Team Update Team Leader", "Team Update Team Member", "Team Update Viewer"]]]},
	{"dt": "DocType", "filters": [["module", "in", ["Masters", "Transactions", "Reports"]]]},
	{"dt": "Workspace", "filters": [["name", "in", ["team_update_tool"]]]},
	{"dt": "Notification", "filters": [["name", "in", ["New Project Uploaded", "Project Approved", "Project Status Updated"]]]},
]

doc_events = {
	"Project": {
		"on_update": "team_update_tool.transactions.doctype.project.project.on_project_update",
		"after_insert": "team_update_tool.transactions.doctype.project.project.send_new_project_notification",
	}
}

