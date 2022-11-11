
import frappe
from frappe import _

def get_data():
	
	return [
		{
			"label": _("Mobile Location Logs"),
			"icon": "",
			"items": [
				{
					"name": "Mobile Log",
					"type": "doctype",
					"description": "Mobile device logs"	
				}
			]
		}
	]
