frappe.pages['mobile-app-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Mobile App Dashboard',
		single_column: true
	});

	filters = [
		{fieldname: "employee", fieldtype: "Link", options: "Employee", label: "Employee"}
	];
	args = {
		template: "mobile_dashboard",
		wrapper: page,
		filters: filters
	};
	mobile_app = new tablix.dashboard.MobileAppDashboard(args);
}
