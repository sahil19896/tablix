
import frappe
from frappe import msgprint, throw, _
from frappe.utils import cint, flt, cstr


def get_dashboard_data(filters=None):
	
	return get_data(filters)

def get_data(filters=None):
	field, value = "", ""
	if not(filters.get("sales_order") or filters.get("project")):
		throw(_("Please select either <b>Project</b> or <b>Sales Order</b>."))
	value = filters.get("sales_order") if filters.get("sales_order") else filters.get("project")
	value = "name" if filters.get("sales_order") else "project"
	so = frappe.db.get_value("Sales Order", {field: value, "docstatus":1}, fielname=["name", "project"], as_dict=True)

	so_items = frappe.db.sql("""SELECT SOI.item_code, SOI.name, SOI.qty, SOI.base_cost_amount AS cost_amount, \
			SOI.base_selling_amount	AS selling_amount, SOI.parent AS sales_order FROM `tabSales Order Item` SOI
			WHERE parent=%(parent)s """, {"parent": so.get("name")}, as_dict=True)
	print(so_items)
	
	return {"name": "sahil"}


def get_all_tasks(so):

	tasks = frappe.db.sql(""" SELECT T.name, T.project, T.subject, T.priority, T.exp_start_date AS start_date, \
			T.exp_end_date AS end_date, T.parent_task FROM `tabTask` T WHERE project=%(project)s """,
			{"project": so.get("project")}, as_dict=True)

	for task in tasks:
		total = get_all_expenses(so, task)
		task.update({"total": total})


def get_all_expenses(so, task=None):
	total = 0.0
	filters =  so.copy()
	cond = " WHERE project=%(project)s AND docstatus=1 "
	if task:
		filters.update({"task": task.get("name")})
		cond += " AND task = %(task)s "
			
	expenses = frappe.db.sql("""SELECT E.name, E.project, E.total_claimed_amount AS total FROM `tabExpense Claim` E \
			 %s """%(cond), filters, as_dict=True)

	for expense in expenses:
		total += flt(expense.get("total"))

	return total	
