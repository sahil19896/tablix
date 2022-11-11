frappe.pages['issue-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Issue Dashboard',
		single_column: true
	});

	var filters = [

		{fieldname: "project_site", label: __("Project Site"), fieldtype:"Link", options: "Maintenance Contract"},
		{fieldname: "status", label: __("Issue Status"), fieldtype:"Select", options: "\nOpen\nClosed", default:"Closed"},
		{fieldname: "report_type", label: __("Report Type"), fieldtype: "Select", options: "Yearly\n"},
		{fieldname: "fiscal_year", label: __("Fiscal Year"), fieldtype:"Link", options:"Fiscal Year", default:frappe.boot.sysdefaults.fiscal_year}
		
	];
	var args = {
		wrapper: page,
		template: "issue_dashboard",
		filters: filters,
		method: "tablix.tdashboard.pages.issue_dashboard.issue_dashboard"
	};
	new tablix.dashboard.IssueDashboard(args);
}
