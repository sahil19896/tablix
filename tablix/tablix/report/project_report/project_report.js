// Copyright (c) 2016, Tablix and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Report"] = {
	"filters": [

		{fieldname: "project", fieldtype: "Link", options:"Project", label: "Project"},
		{fieldname: "sales_order", fieldtype: "Link", options: "Sales Order", label: "Sales Order"},
		{fieldname: "material_request", fieldtype:"Link", options: "Material Request", label: "Material Request"},
		{fieldname: "from_date", fieldtype: "Date", label: "From Date"},
		{fieldname: "to_date", fieldtype:"Date", label: "To Date"}

	],

	onload: function(frm){
	},
	refresh: function(frm){
		console.log(frm);
	},
	get_chart_data: function(columns, results){
		console.log(columns);
		console.log(results);
		return {}
	}
}
