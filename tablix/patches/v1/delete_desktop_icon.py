
import frappe

def execute():
	frappe.db.sql(""" DELETE FROM `tabDesktop Icon` """)
