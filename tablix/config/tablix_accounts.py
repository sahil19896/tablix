
import frappe
from frappe import _

def get_data():

	return [
			{
			"label": _("Tablix Account"),
			"items": [
			]
		},
			{
			"label": _("Setting"),
			"items": [
					{
					"type": "doctype",
					"name": "Purchase Taxes and Charges Template",
					"label": _("Taxes, Vat and Other Charges(Purchase)")
				},
					{
					"type": "doctype",
					"name": "Sales Taxes and Charges Template",
					"label": _("Taxes, Vat and Other Charges(Sales)")
				}
			]
		}
	]
