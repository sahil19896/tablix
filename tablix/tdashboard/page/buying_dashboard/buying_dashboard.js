frappe.pages['buying-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Buying Dashboard',
		single_column: true
	});
	filters = [
		{fieldname: "purchase_order", fieldtype: "Link", options: "Purchase Order", label: "Purchase Order"}
	]
	
	args = {
		template: "buying_dashboard",
		wrapper: page,
		filters: filters
	};
	buying = new tablix.dashboard.BuyingDashboard(args);
}
