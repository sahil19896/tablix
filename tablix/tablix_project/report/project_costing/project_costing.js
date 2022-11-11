// Copyright (c) 2016, Tablix and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Costing"] = {
	"filters": [
			{
			"fieldname": "project", "fieldtype": "Link", "options": "Project",  "label": __("Project")
		},
			{
			"fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order",  "label": __("Sales Order")
		},
	]
}
