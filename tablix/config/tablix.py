
import frappe
from frappe import _

def get_data():
	
	return [
		{
	
			"label": _("Tablix"),
			"icon": '',
			"items": [
				{
					"type": "doctype",
					"name": "Escalation Notification",
					"description": _("Escalation Notification")
				},
				{
					"type": "doctype",
					"name": "Escalation Logs",
					"description": _("Escalation Logs")
				}
				
			],
		},
			{
				"label":_("Time and Attendance"),
				"color": "#2E86C1",
				"items": [
						{
						"type": "doctype",
						"name": "Break Rule"
					},
						{
						"type": "doctype",
						"name": "Shift Rule",
					
					},
				]
		},
			{
				"label": _("Geo"),
				"color": "#17A589",
				"items": [
						{
						"type": "doctype",
						"name": "Location Log"
					},
						{
						"type": "doctype",
						"name": "Site Location"
					}
				]
		},
			{
				"label": _("Dashboard and Charting"),
				"color": "#CA6F1E",
				"items": [
				]
		},
			{
				"label": _("BOQ"),
				"color": "#784212",
				"items": [
						{
						"type": "doctype",
						"name": "Boq",
						"label": "BOQ",
					},
						{
						"type": "doctype",
						"name": "Payment Terms",
						"label": "Payments Terms for BOQ"
					},
						{
						"type": "doctype",
						"name": "Boq Checklist",
						"label": _("BOQ Checklist"),
					},
				]
		},
			{
				"label": _("Mobile"),
				"color": "#CD6155",
				"items": [
						{
						"type": "doctype",
						"name": "Mobile Log",
						"label": "Mobile Apps User Logs",
					}
				]
		},
			{
				"label": _("Tablix CRM"),
				"color": "#7D3C98",
				"items": [
						{
						"type": "doctype",
						"name": "Stage",
						"label": "Setup Stage",
					}
				]
		},
			{
				"label": _("Tablix HR"),
				"color": "#B03A2E",
				"items": [
						{
						"type": "doctype",
						"name": "Employee Pay Rate Rule",
						"label": "Hourly Payment rule for employee"
					},
						{
						"type": "doctype",
						"name":  "Vehicle Detail",
						"label": "Vechicle detail of employee",
					}
				]
		},
			{
				"label": _("Tablix Accounts"),
				"color": "#17202A",
				"items": [
						{
						"type": "doctype",
						"doctype": "Assets Registry",
						"label": _("Assets Registry"),
					}
				]
		},
			{
				"label": _("Setting"),
				"color": "#145A32",
				"items": [
						{
						"type": "doctype",
						"name": "Tablix Setting"
					},
						{
						"type": "doctype",
						"name": "Geo Setting"
					},
						{
						"type": "doctype",
						"name": "Time and Attendance Setting"
					}
				]
		},
			{
				"label": _("Tablix Support"),
				"color": "#D35400",
				"items": [
						{
						"type": "doctype",
						"name": "Maintenance Contract",
					}
				]
		},
		{
			"label": _("Reports"),
			"color": "#9A7D0A",
			"items": [
					{
					"type": "report",
					"is_query_report": True,
					"doctype": "Payments Term Types",
					"name": "Payment Term Types"
				
				},
					{
					"type": "report",
					"is_query_report": True,
					"doctype": "Escalation Notification",
					"name": "Escalation Notification"
				
				},
					{
					"type": "report",
					"name": "Tablix Quotation"
				},
					{
					"type": "report",
					"name": "Project Procurement Item Wise",
				},
					{
					"type": "report",
					"name": "Project Report",
				}
			
			]
		}
	]
