
import frappe
from frappe import _

def get_data():
	
	return [
			{
			"label": _("Dashboards"),
			"items": [
					{
					"type": "page",
					"name": "dashboard",
					"label":  _("Aggregated Dashboard")
				},
					{
					"type": "page",
					"name": "account-dashboard",
					"label": _("Account Dashboard")
				},
					{
					"type": "page",
					"name": "sales-dashboard",
					"label": _("Sales Dashboard")
				},
					{
					"type": "page",
					"name": "buying-dashboard",
					"label": _("Buying Dashboard")
				},
					{
					"type": "page",
					"name": "project-dashboard",
					"label": _("Project Dashboard")
				},
					{
					"type": "page",
					"name": "timesheet-dashboard",
					"label": _("Timesheet Dashboard")
				},
			]
		},
			{
			"label": _("Setting"),
			"items": [
					{
					"type": "doctype",
					"name": "TDashboard Setting",
					"label": _("Dashboard Setting")
				}
			]
		}
	]
