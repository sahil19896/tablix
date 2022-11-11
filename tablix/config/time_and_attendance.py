
import frappe
from frappe import _
def get_data():
	
	return [
			{
			"label":  "Time and Attendance",
			"items": [
				{
					"type": "doctype",
					"name": "Break Rule",
					"description": _("Break rule for employee")
				}
		
			]
		},
			{
			"label": "Setting",
			"items": [
					{
					"type": "doctype",
					"name": "Time and Attendance Setting",
					"description": _("Setup time and attendance")
				}
			]
		},
			{
			"label": "Reports",
			"items": [
					{
					"type": "report",
					"doctype": "Break Rule",
					"name": "Break Rule"
				}
			]
		}
	]
