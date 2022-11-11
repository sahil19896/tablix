frappe.pages['timesheet-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Timesheet Dashboard',
		single_column: true
	});
	
	filters = [
		{fieldname: "timesheet", fieldtype: "Link", options: "Timesheet", label: "Timesheet"},
		{fieldname: "employee", fieldtype: "Link", options: "Employee", label: "Employee"}, 
	];

	args = {
		template: "timesheet_dashboard",
		wrapper: page,
		filters: filters
	};
	timesheet = new tablix.dashboard.TimesheetDashboard(args);
}
