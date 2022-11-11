'''
	Added by Sahil
	Developer Sahil
'''
import frappe
from frappe import _

def get_data():
	
	return [
			{
			"label": _("Scorecard"),
			"items":[
					{
					"label": _("View Scorecard"),
					"type": "doctype",
					"name": "Strategic Theme",
					"description": _("View Scorecard"),
					"route": "Tree/Strategic Theme"
					
				},
					{
					"type": "doctype",
					"name": "Strategic Theme",
					"description": _("Strategic Theme")
				},
					{
					"type": "doctype",
					"name": "Strategic Objective",
					"description": _("Strategic Objective")
				},
					{
					"type": "doctype",
					"name": "Indicator",
					"description": _("Indicator")
				},
			]
				
		},
			{
			"label": _("Reports"),
			"items": [
					{
					"label": _("Scorecard"),
					"type": "report",
					"is_script_report": True,
					"name": "Scorecard Report",
					"description": _("View Scorecard Report"),
				}	
			]
		}
	]
