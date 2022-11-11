# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint

class SalesOrderSummary(Document):
	pass

@frappe.whitelist()
def get_so_data(name):
	if(name):
		data = frappe.db.sql("""select s.name, s.title, s.account_manager, s.bdm, s.area, s.customer, s.transaction_date,
				s.delivery_date, s.manager_service_delivery, s.po_no, s.total_cost_amount,
				s.total_margin_amount, s.total_margin_percent, s.currency, s.conversion_rate, si.quotation_detail 
				from `tabSales Order` s inner join `tabSales Order Item` si on s.name = si.parent 
				where s.name = %s LIMIT 1 """,name, as_dict=True)

		if(data):
			for d in data:
				frappe.msgprint(_("{0}").format(d))	
