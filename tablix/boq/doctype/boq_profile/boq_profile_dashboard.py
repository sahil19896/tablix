
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt

def get_data():
	
	return {
		"fieldname": "boq_profile",
		"non_standard_fieldnames":{
			"Quotation": "boq_profile"	
		},
		"internal_links": {
			"Opportunity": ["name"],
			"Quotation": ["boq_profile"]
		},
	}
