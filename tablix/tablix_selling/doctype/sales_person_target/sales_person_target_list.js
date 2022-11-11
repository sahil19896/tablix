frappe.listview_settings["Sales Person Target"] = {
	right_column: "total_target",
	add_fields: ["employee", "employee_name", "fiscal_year", "total_target", "is_group"],
	hide_name_column: true,
	colwidths: {
		indicator: 1
	},
	refresh: function(page){
	},
}
