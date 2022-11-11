// Copyright (c) 2016, Tablix and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Procurement Item Wise"] = {
	"filters": [

		{fieldname: "sales_order", fieldtype: "Link", options: "Sales Order", label:"Sales Order"},
		{fieldname: "item_code", fieldtype: "Link", options: "Item", label:"Item Code"},

	],
	onload: function(frm){
	},
	get_report_data: function(col, res){

			console.log(col);
			console.log(res);
			return {};
	}
}
