frappe.pages['account-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Account Dashboard',
		single_column: true
	});
	
	filters = [
		{fieldname: "account", fieldtype: "Link", options: "Account", label: "Account"}
	];
	
	args = {
		template: "account_dashboard",	
		filters: filters,
		wrapper: page
	};
	account = new tablix.dashboard.AccountDashboard(args);
}
