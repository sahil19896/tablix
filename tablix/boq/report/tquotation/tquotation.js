// Copyright (c) 2016, Tablix and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["TQuotation"] = {
	"filters": [
		{
			"fieldname": "customer",
			"fieldtype": "Link",
			"options":"Customer",
			"label": __("Customer"),
		},
		{
			"fieldname": "lead",
			"fieldtype": "Link",
			"options": "Lead",
			"label": __("Lead"),
		},
	]
}
