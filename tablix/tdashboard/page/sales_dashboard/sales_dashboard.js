frappe.pages['sales-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Sales Dashboard',
		single_column: true
	});

	filters = [
			{fieldtype: "Link", fieldname: "company", options:"Company", 
			label: "Company", default: frappe.boot.sysdefaults.company, reqd:1}, 
			{fieldtype: "Link", fieldname: "fiscal_year", options: "Fiscal Year", 
			label:"Fiscal Year", reqd:1, default: frappe.boot.sysdefaults.fiscal_year},
			{fieldtype: "Select", fieldname: "report_type", options:"Monthly\nQuarterly",
			default:"Monthly", label: "Report Type"},
			{fieldtype: "Select", fieldname: "bdm", options: frappe.boot.tablix.sales.bdms,
			label: "BDM"},
			{fieldtype: "Select", fieldname: "manager", label: "Account Manager",
			options: frappe.boot.tablix.sales.managers},
			{fieldtype: "Link", fieldname: "opportunity", options: "Opportunity", 
			label:"Opportunity"},
	]
	args = {
		wrapper: page,
		filters: filters,
		template: "sales_dashboard",
		method: "tablix.tdashboard.pages.sales_dashboard.sales_dashboard"
	}
	dashboard = new tablix.dashboard.SellingDashboard(args);
}


