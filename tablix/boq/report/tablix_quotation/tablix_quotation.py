# Copyright (c) 2013, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
def execute(filters=None):
	columns, data = [], []

	columns = get_field()
	condition = get_condition(filters)
	results =  frappe.db.sql("""SELECT name, grand_total, is_boq, tablix_rep, project_site_name, customer_name, lead, transaction_date \
				 FROM `tabQuotation` WHERE docstatus=1 AND transaction_date > '2017-01-01' %s """%(condition),{"bdm":filters.get("bdm_name")}, as_dict=True)
	for item in results:
		data.append([item.get("name"), item.get("tablix_rep"), item.get("customer_name"), item.get("lead"),\
				 item.get("project_site_name"), item.get("is_boq"), item.get("grand_total"), item.get("transaction_date")])
		
	return columns, data





def get_condition(filters):
	
	condition = ""
	if filters.get("bdm_name"):
		condition += " AND tablix_rep= %(bdm)s "

	return condition

def get_field():

	return [
		_("Quotation Name")+":Link/Quotation:150", _("Tablix Rep")+":Link/User:150", _("Customer Name")+":Link/Customer:150", \
		_("Lead")+":Link/Lead:150", _("Project Site Name")+":Data:150", _("IS BoQ")+":Check:50", _("Grand Total")+":Currency:150",
		_("Date")+":Date:150"
	]
