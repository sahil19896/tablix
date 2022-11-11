# Copyright (c) 2013, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict
from frappe import msgprint

def execute(filters=None):
	columns, data = [], []

	if not filters: return

	columns = get_columns()

	opty = get_data(filters)
	if(opty):
		data.append([opty[0].account_manager, opty[0].count])

	status = ["Designing", "Submitted", "Ordered", "Cancelled", "KAM Approval", "KAM Approved", "KAM Rejected", "DOS Approved", "DOS Rejected", "COO Approved", "COO Rejected", "Sales Complete"]
	quote = get_quote(filters)
	for q in status:
		data.append([q, quote[0][q]])
	
	return columns, data

def get_columns():
	columns = [
		_("Account Manager") + ":Link/Account Manager:150", _("OPTY Count") + ":Data:100", _("") + ":Data:100", 
		_("") + ":Data:100"
	]

	return columns

def get_condition(filters):
	condition = ""
	if filters.get("account_manager"): condition += " account_manager = %(account_manager)s"
	if filters.get("from_date") and filters.get("to_date"): condition += " And transaction_date between %(from_date)s AND %(to_date)s"
	return condition

def get_data(filters):
	condition = get_condition(filters)
	return frappe.db.sql("""select count(name) as count, account_manager from `tabOpportunity` where %s """%condition, filters, as_dict=True)

def get_quote(filters):
	condition = get_condition(filters)
	quote = frappe.db.sql("""select name, tablix_status, status from `tabQuotation` where %s """%condition, filters, as_dict=True)
	order = frappe.db.sql("""select count(name) as count from `tabSales Order` where %s"""%condition, filters, as_dict=True)

	t_status = ["Open", "Designing", "Submitted", "Cancelled", "KAM Approval", "KAM Approved", "KAM Rejected", "DOS Approved", "DOS Rejected", "COO Approved", "COO Rejected", "Sales Complete", "Ordered", "Boq Complete"]

	data = []

	open_ = design = submit = order_ = cancel = kam = kam_a = kam_r = dos_a = dos_r = coo_a = coo_r = sales_c = 0
	for q in quote:
		if("Submitted" == q.tablix_status and "Open" == q.status):
			submit += 1
		if("Open" == q.tablix_status or "Designing" == q.tablix_status):
			open_ += 1
		if("Submitted" == q.tablix_status and "Ordered" == q.status):
			order_ += 1
		if("Cancelled" == q.tablix_status):
			cancel += 1
		if("KAM Approval" == q.tablix_status):
			kam += 1
		if("KAM Approved" == q.tablix_status):
			kam_a += 1
		if("KAM Rejected" == q.tablix_status):
			kam_r += 1
		if("DOS Approved" == q.tablix_status):
			dos_a += 1
		if("DOS Rejected" == q.tablix_status):
			dos_r += 1
		if("COO Approved" == q.tablix_status):
			coo_a += 1
		if("COO Rejected" == q.tablix_status):
			coo_r += 1
		if("Sales Complete" == q.tablix_status):
			sales_c += 1
	data.append({"Designing": open_, "Submitted": submit, "Ordered": order[0].count, "Cancelled": cancel, "KAM Approval": kam, "KAM Approved": kam_a, "KAM Rejected": kam_r, "DOS Approved": dos_a, "DOS Rejected": dos_r, "COO Approved": coo_a, "COO Rejected": coo_r, "Sales Complete": sales_c})
	return data
