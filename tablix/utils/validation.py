

import frappe
from frappe import msgprint, throw, _
from frappe.utils import cint, cstr, flt



def has_substitute_item(doc):
	
	flag = False 
	if doc.get("items"):
		for item in doc.get("items"):
			if item.get("substitute_item"):
				flag = True
				break

	return flag
