
import frappe
from frappe import _

def execute():
	migrate_po_status()
	migrate_so_status()	
	migrate_mr_status()	
	migrate_opp_status()	
	migrate_boq_status()	





def migrate_po_status():
	frappe.db.sql(""" UPDATE `tabPurchase Order` SET tablix_status=status """)

def migrate_so_status():
	frappe.db.sql(""" UPDATE `tabSales Order` SET tablix_status=status """)

def migrate_mr_status():
	frappe.db.sql(""" UPDATE `tabMaterial Request` SET tablix_status=status """)

def migrate_opp_status():
	frappe.db.sql(""" UPDATE `tabOpportunity` SET tablix_status=status """)

def migrate_boq_status():
	return False
	frappe.db.sql(""" UPDATE `tabBoq` SET tablix_status=status """)
