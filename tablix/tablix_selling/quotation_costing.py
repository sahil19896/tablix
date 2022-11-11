
'''
	Added  by Sahil
	Email sahil.saini@tablix.ae
'''
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt, now_datetime


def get_quotation_cost(quotation=None):
	data = {}
	if not quotation:
		return data

	doc = frappe.get_doc("Quotation", quotation)
	data.update({"quotation_detail": get_quotation_cost_detail(doc),
		     "purchase_detail": get_purchase_and_invoice_detail(doc.name, "Purchase Order Item", "cost"),
		     "invoice_detail": get_purchase_and_invoice_detail(doc.name, "Sales Invoice Item", "sale")
	})
	return data



def get_quotation_cost_detail(doc):

	costing = frappe._dict({"cost": doc.get("base_total_cost_amount"), "sale": doc.get("base_total")})	
	return costing


def get_purchase_and_invoice_detail(quotation, tablename, field):
	
	items = frappe.db.get_values(tablename, {"quotation_detail": quotation, "docstatus": ["!=", 2]},\
			["base_amount", "qty", "item_code"], as_dict=True)

	costing = frappe._dict({field: 0.0})
	for item in items:
		costing[field] += item.get("base_amount")
	return costing


