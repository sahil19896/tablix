
import frappe
from frappe import _

def get_data():
	
	return [
			{
				"label": _("Setting"),
				"items": [
						{
						"type": "doctype",
						"name": "Metabase Setting",
						
					}
				]
		},
			{
				"label": _("Page"),
				"items": [
						{
						"type": "page",
						"name": "metabase"
					}
				]
		}
	]
