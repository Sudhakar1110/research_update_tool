// Project - Client Script
frappe.ui.form.on("Project", {
	refresh: function(frm) {
		team_update_tool.show_viewer_banner(frm);
	}
});
