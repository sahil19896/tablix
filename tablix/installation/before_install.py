
import frappe
from frappe import _, throw
from frappe.utils import flt, cint, cstr


def before_install():
	
	print("Before Tablix App installation")




def delete_default_welcome_page():
	frappe.db.sql(""" DELETE FROM `tabPage` WHERE name='welcome-to-erpnext' """)
