# Copyright (c) 2013, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate

def execute(filters=None):
	columns, data = [], []
	
	columns = get_columns(filters)
	
	_data = get_data(filters)

	for d in _data:
		order = ('', 0.00, '')
		order_item = frappe.db.get_value("Sales Order Item", {"prevdoc_docname": d.name}, "parent")

		if(order_item):
			order = frappe.db.get_value("Sales Order", {"name": order_item}, ["name", "grand_total", "transaction_date"])

		if(d.opportunity):
			opp = frappe.get_doc("Opportunity", d.opportunity)

			data.append([d.party_name, d.opportunity, d.name, d.order_type, d.bdm_name, opp.source, opp.opportunity_from, d.area, d.currency, d.engineer, d.boq_cost_amount, d.boq_selling_amount_after_discount, d.amc_cost_amount, d.amc_selling_amount_after_discount, d.grand_total, d.company, d.transaction_date, d.status, order[0], order[1], order[2]])
		else:
			data.append([d.party_name, d.opportunity, d.name, d.order_type, d.bdm_name, "", "", d.area, d.currency, d.engineer, d.boq_cost_amount, d.boq_selling_amount_after_discount, d.amc_cost_amount, d.amc_selling_amount_after_discount, d.grand_total, d.company, d.transaction_date, d.status, order[0], order[1], order[2]])

	return columns, data


def get_columns(filters):
	columns = [_("Customer") + ":Link/Customer:150"] + [_("Opportunity") + ":Link/Opportunity:150"] + [_("QTN Name") + ":Link/Quotation:150"] + [_("Order Type") + ":Data:150"] + [_("BDM Name") + ":Data:100"] + [_("Source") + ":Data:100"] + [_("Opportunity From") + ":Data:100"] + [_("Site") + ":Data:150"] + [_("Currency") + ":Data:150"] + [_("Design Engineer") + ":Data:150"] + [_("BOQ Cost Amount") + ":Currency:150"] + [_("BOQ Selling Amount After Discount") + ":Currency:150"] + [_("AMC Cost Amount") + ":Currency:150"] + [_("AMC Selling Amount After Discount") + ":Currency:150"] + [_("Grand Total") + ":Currency:150"] + [_("Company") + ":Link/Company:150"] + [_("Date") + ":Date:150"] + [_("Status") + ":Data:150"] + [_("SO No.") + ":Link/Sales Order:150"] + [_("SO Value") + ":Currency:150"] + [_("SO Date") + ":Date:150"]

	return columns


def get_conditions(filters):
	conditions = []
	if filters.get("from_data") and filters.get("to_date"):
		condition = "transaction_date between "+filters.get("from_data")+ " and "+filters.get("to_data")
		frappe.msgprint(_("{0}").format(condition))
		#conditions.append(condition)

	#return conditions
def get_data(filters):

	data = frappe.db.sql(""" select party_name, opportunity, name, order_type, bdm_name, area, engineer, boq_cost_amount, boq_selling_amount_after_discount, amc_cost_amount, amc_selling_amount_after_discount, grand_total, company, transaction_date, status, currency from `tabQuotation` where transaction_date >= %s and transaction_date <= %s """,(filters.get("from_date"), filters.get("to_date")), as_dict=True)

	return data
