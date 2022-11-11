// Copyright (c) 2016, Tablix and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Issue Report BOQ"] = {
	"filters": [
		{fieldname: "project_site", label: __("Project Site"), fieldtype:"Link", options: "Maintenance Contract"},
		{fieldname: "status", label: __("Issue Status"), fieldtype:"Select", options: "\nOpen\nClosed", default:"Closed"},
		{fieldname: "report_type", label: __("Report Type"), fieldtype: "Select", options: "Yearly\n"},
		{fieldname: "fiscal_year", label: __("Fiscal Year"), fieldtype:"Link", options:"Fiscal Year", default:frappe.boot.sysdefaults.fiscal_year}
		
	]
}
