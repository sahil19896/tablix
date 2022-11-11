
import frappe
from frappe  import _


def execute():
	return False	
	frappe.db.sql(""" UPDATE `tabQuotation` SET opportunity_quotation="opportunity" """)
	frappe.db.sql(""" DELETE FROM `tabCustom Field` WHERE fieldname="opportunity" AND dt="Quotation" """)
