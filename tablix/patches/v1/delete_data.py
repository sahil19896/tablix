

import frappe

def execute():
	return False	
	frappe.db.sql("""DELETE FROM `tabBoq Checklist` """)


