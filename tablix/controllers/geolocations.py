
'''
	Developer Varna 
'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr


@frappe.whitelist(allow_guest=True)
def send_location(*args, **kwargs):

	print(args)
	print(kwargs)
	return frappe.get_list("Workflow", fields="*")

