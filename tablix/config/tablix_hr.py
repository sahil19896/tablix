
import frappe
from frappe import _

def get_data():
	
	return [
		{
			"label": "Tablix HR",
			"items": [
				{
					"type": "doctype",
					"name": "Employee Pay Rate Rule",
					"description": "Working hours pay rule",
				}
			]
		}
	]
