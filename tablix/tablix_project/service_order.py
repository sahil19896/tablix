'''
	Added by Sahil
	Developer Navdpeep Saini
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe.utils import cint, flt, cstr
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_service_order(source_name, target_doc=None):

	doc = get_mapped_doc("Sales Order", source_name, {
		

		"Sales Order": {
			"doctype": "Purchase Order",
			"field_map": {
				"name": "customer_po",
				"boq": "boq",
				"project": "project"
			}
		},
		"Sales Order Item":{
			"doctype": "Purchase Order Item",
			"field_map":{
				"description": "item_description"
			},
			"condition": lambda item: item.item_group in ['Services', 'Professional Services']
		}
	})
	doc.vat = 0.0
	doc.duties = 0.0
	doc.other_charges = 0.0
	doc.tablix_rep = ""
	doc.is_service_order = 1
	doc.order_type = "Service"	
	return doc	
