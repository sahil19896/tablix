from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("D&E Transactions"),
			"items": [
			{
				"type": "doctype",
				"name": "Opportunity",
				"description": _("Record Opportunities"),
				"label":"Approved Opportunities For BoQ"
				},
			{
				"type": "doctype",
				"name": "Task",
				"description": _("Assign Tasks"),
				}
			]
		},
		{
			"label": _("D&E Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "BoQ Report",
					"doctype": "Boq"
				}
		
			]		
		}
		
	]
