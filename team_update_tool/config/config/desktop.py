from frappe import _


def get_data():
	return [
		{
			"module_name": "Team Update Tool",
			"category": "Modules",
			"label": _("Team Update Tool"),
			"color": "#2E8B57",
			"icon": "octicon octicon-repo",
			"type": "module",
			"description": "Track completed team projects, GitHub links, screenshots, and documentation.",
		}
	]
