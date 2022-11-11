frappe.pages['project-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Project Dashboard',
		single_column: true
	});

	filters = [
		{fieldname: "project", fieldtype: "Link", options:"Project", label: "Project"},
		{fieldname: "sales_order", fieldtype: "Link", options: "Sales Order", label: "Sales Order"}
	]
	args = {
		template: "project_dashboard",
		wrapper: page,
		filters: filters
	}
	project = new tablix.dashboard.ProjectDashboard(args);
}
