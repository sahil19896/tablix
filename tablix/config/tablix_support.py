
import frappe
from frappe import _

def get_data():
		
	return [
			{
				"label": _("Tablix Support"),
				"items": [
						{
						"type": "doctype",
						"name": "Maintenance Contract",
						"label": "Maintenance Contract"
					}
				]
		}
	]
