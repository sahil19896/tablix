'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt
import json

@frappe.whitelist()
def get_tree_nodes(is_root=None, parent=None, **kwargs):
	
	filters = {}
	cond = ""
	if parent:
		cond += " AND parent_solution_system_type=%(parent)s "
		filters.update({"parent": parent})
	if is_root:
		cond +=  " AND is_group = 1 "

	results = frappe.db.sql(""" SELECT name, is_group AS expandable, parent_solution_system_type
			FROM `tabSolution System Type` WHERE is_root=0 %s """%(cond), filters, as_dict=True)
	return results


@frappe.whitelist()
def add_tree_node(frm):
	if frm and isinstance(frm, str):
		frm = json.loads(frm)

	doc = frappe.get_doc({
			"doctype": "Solution System Type", "is_group": frm.get("is_group"), 
			"system_type": frm.get("system_type"),
			"abbreviation_of_system": frm.get("abbreviation_of_system"),
			"parent_solution_system_type": frm.get("parent_system_type"),
			"system_overview": frm.get("system_overview"), "description": frm.get("description"),
			
		})
	try:
		doc.save()
		frappe.db.commit()
	except Exception as e:
		frappe.msgprint(e.message)
		frappe.db.rollback()


