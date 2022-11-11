
'''
	Developer Sahil
	Email sahil.saini@tablix.ae

'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr
import os

def verify_user_location(*args, **kwargs):

	if kwargs.get("login_manager"):
		login_manager = kwargs.get("login_manager")




@frappe.whitelist(allow_guest=True)
def validate_app(*args, **kwargs):
	print(args)
	print(kwargs)
