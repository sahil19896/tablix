
import frappe
from frappe import _

def get_data():

	return [
			{
				"label": "Tablix CRM",
				"items": [
					{
						"type": "doctype",
						"name": "Stage",
						"description": _("Stage Detail")
					}
				]
			}
	]
