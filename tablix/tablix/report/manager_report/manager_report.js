// Copyright (c) 2016, Tablix and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Manager Report"] = {
	"filters": [
		{
			"fieldname": "account_manager",
			"fieldtype": "Link",
			"label": __("Account Manager"),
			"options": "Account Manager",
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": __("Form Date"),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": __("To Date"),
			"reqd": 1
		}
	]
};
