# Copyright (c) 2013, Tablix and contributors
# For license information, please see license.txt

'''
    Added by Sahil
    Email sahil.saini@tablix.ae
'''

from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, datetime, flt, cint, cstr
from frappe import _, msgprint, throw
from tablix.utils import get_date, get_datetime, format_datetime, format_date

DATE_FORMAT = "%Y-%m-%d"

def execute(filters=None):
	columns, data = [], []
	temp_filters, condition = get_so_filters_and_condition(filters)
	validate_filters(filters)
	columns = get_columns()
	chart_data = []
	try:
		selling_map, buying_data_map = get_data(temp_filters, condition)
		for key, val in selling_map.items():
			if not len(val):
				continue
			data.append([key])
			total_cost = 0.0
			temp = {}
			for item in val:
				temp = item
				total_cost += item.get("buying_cost")
				data.append([None, 
						item.get("project_name"),
						item.get("boq"),
						item.get("quotation"),
						item.get("material_request_date"),
						item.get("material_request"),
						item.get("purchase_order"),
						item.get("supplier_name"),
						item.get("purchase_order_date"),
						item.get("delivery_note"),
						None,
						item.get("buying_cost"),
				])
			selling_cost = temp.get("selling_cost")
			diff = selling_cost - total_cost
			data.append(["", "","", "", "", "", "", "", "", "",selling_cost, total_cost, diff, temp])

	except Exception as e:
		frappe.msgprint("{0}".format(frappe.get_traceback()))

	return columns, data


def get_columns():
	return [
		_("SO No.") + ":Link/Sales Order:200",
		_("Project Name") +":Link/Project:200", _("Boq")+":Link/Boq:200",
		_("Quotation") + ":Link/Quotation:200",
		_("Date Of MR") + ":Date/Project:200", _("MR No.") + ":Link/Material Request:200",
		_("PO No") + ":Link/Purchase Order:200", _("Supplier Name")+ ":Link/Supplier:100",
		_("PO Date") + ":Date:100", _("DN No.") + ":Link/Delivery Note:100",
		_("Selling Price(BOQ)") + ":Float:200",
		_("Cost Price(PO)") + ":Float:200", _("Cost Diff") + ":Float:200"
	]

def validate_filters(filters):
	now_date = get_date(nowdate(), DATE_FORMAT, is_date=True)
	if filters.get("to_date") and filters.get("from_date"):
		from_date = get_date(filters.get("from_date"), DATE_FORMAT, is_date=True)
		to_date = get_date(filters.get("to_date"), DATE_FORMAT, is_date=True)
		if from_date > now_date:
			throw(_("<b>From Date</b> Can't be greater than <b>Today Date</b>"))
		if from_date > to_date:
			throw(_("<b>From Date</b> Can't be greater than <b> To Date</b>"))

	elif filters.get("from_date") and not filters.get("to_date"):
		from_date = get_date(filters.get("from_date"), DATE_FORMAT, is_date=True)
		if from_date > now_date:
			throw(_("<b> From Date </b> can't be greater than to date"))

	elif filters.get("to_date") and not filters.get("from_date"):
		to_date = get_date(filters.get("to_date"), DATE_FORMAT, is_date=True)


def get_so_filters_and_condition(filters):
	condition = ""
	temp = {}
	if filters.get("sales_order"):
		temp["sales_order"]  = filters.get("sales_order")
		condition += " AND SO.name = %(sales_order)s "
	if filters.get("boq"):
		temp["boq_ref"] = filters.get("boq")
		condition += " AND SO.boq_ref=%(boq_ref)s "
	if filters.get("opportunity"):
		temp["opp_ref"] = filters.get("boq")
		condition += " AND SO.opp_ref = %(opp_ref)s "
	if filters.get("from_date"):
		temp["from_date"] = filters.get("from_date")
		condition += " AND SO.creation > %(from_date)s"
	if filters.get("to_date"):
		temp["to_date"] = filters.get("to_date")
		condition += " AND SO.creation < %(to_date)s "
	return temp, condition

def get_data(filters, condition):
	#Buying Data Items Map
	data_map = frappe._dict()
	#Selling Data Items Map
	selling_map = frappe._dict()
	selling_items = get_selling_items(filters, condition)
	for selling_item in selling_items:
		update_selling_buying_map(selling_item, data_map, selling_map)

	return selling_map, data_map


def get_selling_items(filters, condition):
	sales_orders = frappe.db.sql("""SELECT SO.vat, SO.duties, SO.other_charges, SO.base_grand_total, \
				SO.name AS sales_order, SO.base_total_taxes_and_charges FROM `tabSales Order` SO \
				WHERE SO.docstatus=1 %s """%(condition),filters, as_dict=True)
	return sales_orders


def update_selling_buying_map(sales_order, data_map, selling_map):
	condition = ""
	filters = {}
	for material_request in frappe.db.sql(""" SELECT name AS material_request, boq, quotation_ref AS quotation, \
		schedule_date, modified AS material_request_date,project FROM `tabMaterial Request` WHERE docstatus=1 AND \
		customer_order=%(sales_order)s """, {"sales_order": sales_order.get("sales_order")}, \
		as_dict=True):

			condition = " AND material_request=%(material_request)s "
			filters = {"material_request": material_request.get("material_request")}

			for purchase_order in frappe.db.sql(""" SELECT name AS purchase_order, base_grand_total,
				vat, duties, other_charges, base_total_taxes_and_charges, supplier_name, modified AS purchase_order_date
				FROM `tabPurchase Order` WHERE docstatus=1 %s"""%(condition), 
				filters, as_dict=True):
					update_buying_map(purchase_order, material_request, sales_order, data_map, selling_map)



def update_buying_map(purchase_order, material_request, sales_order, data_map, selling_map):
	key = tuple([
		sales_order.get("sales_order"),
		material_request.get("material_request"),
		purchase_order.get("purchase_order"),
	])
	if not data_map.has_key(key):
		data_map[key] = frappe._dict({
			"sales_order": sales_order.get("sales_order"),
			"material_request": material_request.get("material_request"),
			"purchase_order": purchase_order.get("purchase_order"),
			"opportunity": material_request.get("quotation"),
			"quotation": material_request.get("quotation"),
			"boq": material_request.get("boq"),
			"buying_cost": purchase_order.get("base_grand_total"),
			"selling_cost": sales_order.get("base_grand_total"),
			"eta_date": "",
			"price_diff": 0,
			"material_request_date": material_request.get("material_request_date"),
			"supplier_name": purchase_order.get("supplier_name"),
			"purchase_order_date": purchase_order.get("purchase_order_date"),
			"project_name": material_request.get("project")
		})
		item = data_map.get(key)
		update_selling_map(item, selling_map)

def update_selling_map(item, data_selling_map):
	if not data_selling_map.has_key(item.get("sales_order")):
		data_selling_map[item.get("sales_order")] = []
		data_selling_map[item.get("sales_order")].append(item)
