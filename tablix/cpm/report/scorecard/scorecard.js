// Copyright (c) 2016, Tablix and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Scorecard"] = {
	"filters": [
			{
			fieldname: "company", fieldtype: "Link", options:"Company", label:"Company"
		},
			{
			fieldname: "fiscal_year", fieldtype: "Link", options:"Fiscal Year", label: "Fiscal Year"
		}
		
	]
}
