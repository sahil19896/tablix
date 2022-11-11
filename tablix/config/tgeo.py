
import frappe
from frappe import _

def get_data():
	
	return [
		{
			"label": _("Geo"),
			"items": [
				{
					"type": "doctype",
					"name":  "Location Log",
					"description": "User Phone location logs"
				},
				{
					"type": "doctype",
					"name": "Site Location",
					"description": "Site Location for projects"
				}
			]
		},
		{
			"label": _("Setting"),
			"items":[
				{
					"type": "doctype",
					"name": "Geo Setting",
					"description": "Setup google keys and Current location"
				}
			]
		}
	]
