
import frappe

def execute():
	
	frappe.db.sql("DELETE FROM `tabCustom Field` WHERE fieldname IN ('total', 'check', 'check_all', 'delete_all', 'opportunity', 'uom', 'country_of_origin', 'cost_center')")
	frappe.db.sql("DELETE from `tabCustom Field` WHERE dt='Boq'")
	remove_boq_item_custom_fields()



def remove_boq_item_custom_fields():
	
	frappe.db.sql(""" DELETE FROM `tabCustom Field` WHERE dt="Boq Item" """)
