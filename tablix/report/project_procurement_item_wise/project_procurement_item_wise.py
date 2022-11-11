# Copyright (c) 2013, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, cstr


def execute(filters=None):
	columns, data = [], []
	condition = get_condition(filters)
	columns = get_columns()
	results = get_data(filters, condition)
	for res in results:
		cost_diff=flt(res.get("sale_in_company_currency"))-flt(res.get("cost_in_company_currency"))
		data.append([
			res.get("sales_order"), res.get("project"),
			res.get("project_manager"), 
			res.get("project_site_name"), res.get("material_request"),
			res.get("mr_date"), res.get("eta_date"),
			res.get("material_request_status"), res.get("material_request_type"),
			res.get("purchase_order"), res.get("po_date"),
			res.get("purchase_order_status"),
			res.get("company_currency"), res.get("supplier_currency"),
			res.get("supplier_name"), res.get("selling_item_code"),
			res.get("buying_item_code"), res.get("item_name"),
			res.get("item_description"),
			res.get("substitute_item"),
			res.get("item_group"), res.get("buying_brand"),
			res.get("selling_unit"), res.get("buying_unit"),
			res.get("sale_in_company_currency"), res.get("sale_per_unit_in_company_currency"),
			res.get("cost_in_company_currency"), res.get("cost_per_unit_in_company_currency"),
			cost_diff,
			res.get("selling_qty"), res.get("requested_qty"), res.get("ordered_qty"),
			res.get("received_qty"),
			res.get("payment_term"),
		])

	return columns, data

def get_condition(filters):
	condition = ""
	if filters.get("sales_order"):
		condition += " AND sales_order=%(sales_order)s "
	if filters.get("item_code"):
		condition += " AND item_code=%(item_code)s "

	return condition

def get_columns():
	columns =  [
		_("Sales Order")+":Link/Sales Order:150", _("Project")+":Link/Project:200",
		_("Project Manager")+":Link/User:150",
		_("Project Location")+":Data:150", _("Material Request")+":Link/Material Request:150",
		_("Material Date")+":Date:150", _("ETA Date")+":Date:150",
		_("MR Status")+":Data:150",_("Type of MR")+":Data:150",
		_("Purchase Order")+":Link/Purchase Order:150", _("Purchase Date")+":Date:150",
		_("PO Status")+":Data:150",
		_("Supplier Currency")+":Link/Currency:100",
		_("Company Currency")+":Link/Currency:100",
		_("Supplier Name")+":Link/Supplier:150",
		_("Selling Item Code")+":Link/Item:200",
		_("Buying Item Code")+":Link/Item:200",
		_("Item Name") +":Data:150", _("Item Decription")+":Data:150",
		_("Substitute Item")+":Link/Item:200",
		_("Item Group")+":Link/Item Group:150",
		_("Item Brand") +":Link/Brand:150",
		_("Selling Unit")+":Link/UOM:100",
		_("Buying Unit")+":Link/UOM:100", _("Selling Cost Total")+":Currency:150",
		_("Selling Cost/Unit")+":Currency:100",_("Buying Cost Total") +":Currency:150",
		_("Buying Cost/Unit")+":Currency:150", _("Cost Diff")+":Currency:150",
		_("Selling Qty")+":Float:100",
		_("Requested Qty")+":Float:100", _("Order Qty") +":Float:100",
		_("Received Qty")+":Float:100",
		_("Payment Terms")+":Data:200", _("Mode of Payment")+":Data:200",
		_("Delivery Note") + ":Link/Delivery Note:150",
	]
	return columns


def get_data(filters, condition):
	data = []
	sales_order_items = get_sales_order_items(filters)
	for so_item in sales_order_items:
		for mr_item in get_material_request_items(so_item):
			update_data_items(so_item, mr_item, data)

	return data 

def get_sales_order_items(filters):
	condition = ""
	if filters.get("item_code"):
		condition += " AND item_code=%(item_code)s"
	if filters.get("sales_order"):
		condition += " AND parent=%(sales_order)s"

	return frappe.db.sql("""SELECT parent AS sales_order,  item_code AS selling_item_code, item_name,\
		description, qty, stock_uom, uom AS selling_unit, base_rate AS \
		sale_per_unit_in_company_currency, rate AS sale_per_unit_in_customer_currency, brand AS \
		selling_brand, base_amount AS sale_in_company_currency, amount AS sale_in_customer_currency,\
		prevdoc_docname AS quotation, opp_ref as opportunity, boq_ref AS boq, warehouse FROM \
		`tabSales Order Item` WHERE docstatus=1 %s """%(condition), filters, as_dict=True) 

def get_boq_items(filters):
	selling_items =  frappe.db.sql("""SELECT parent AS sales_order,  item_code AS selling_item_code, item_name,\
		description, qty, stock_uom, uom AS selling_unit, base_rate AS \
		sale_per_unit_in_company_currency, rate AS sale_per_unit_in_customer_currency, brand AS \
		selling_brand, base_amount AS sale_in_company_currency, amount AS sale_in_customer_currency,\
		prevdoc_docname AS quotation, opp_ref as opportunity, boq_ref AS boq, warehouse FROM \
		`tabSales Order Item` WHERE docstatus=1 %s """%(condition), filters, as_dict=True) 

        
def get_material_request_items(so_item):
	filters = {"sales_order": so_item.get("sales_order"), "item_code": so_item.get("selling_item_code")}
	condition = " AND customer_order=%(sales_order)s "
	
	material_requests = frappe.db.sql("""SELECT name, material_request_type, request_by, status\
		FROM `tabMaterial Request` WHERE docstatus < 2 %s"""%(condition), filters, as_dict=True)

	if not material_requests:
		return []

	filters.update({"material_request": tuple([item.get("name") for item in material_requests])})
	condition = " AND MRI.parent IN %(material_request)s AND MRI.item_code=%(item_code)s "

	material_request_items = frappe.db.sql("""SELECT MRI.parent AS material_request, MRI.qty AS \
				requested_qty, POI.parent AS purchase_order, MRI.substitute_item, POI.item_code AS \
				buying_item_code, POI.item_name, POI.qty AS ordered_qty, POI.brand AS buying_brand,\
				POI.uom AS buying_unit, POI.received_qty, POI.base_amount AS cost_in_company_currency, \
				POI.amount AS cost_in_supplier_currency, POI.rate cost_per_unit_in_supplier_currency, \
				POI.base_rate AS cost_per_unit_in_company_currency, POI.item_group, MRI.project, \
				POI.description AS item_description, MRI.eta_date
				FROM `tabMaterial Request Item` MRI \
				INNER JOIN `tabPurchase Order Item` POI ON MRI.item_code=POI.item_code AND MRI.parent=\
				POI.material_request WHERE MRI.docstatus < 2 AND POI.docstatus < 2 AND MRI.substitute_item \
				IS NULL %s """%(condition), filters, as_dict=True)

	update_substitute_items(material_request_items, condition, filters)
	return material_request_items

def update_substitute_items(mr_items, condition, filters):
	material_request_items = frappe.db.sql("""SELECT MRI.parent AS material_request, MRI.qty AS \
				requested_qty, POI.parent AS purchase_order, MRI.substitute_item, POI.item_code AS  \
				buying_item_code, POI.item_name, POI.qty AS ordered_qty, POI.brand AS buying_brand, \
				POI.uom AS buying_unit, POI.received_qty, POI.base_amount AS cost_in_company_currency, \
				POI.amount AS cost_in_supplier_currency, POI.rate cost_per_unit_in_supplier_currency, \
				POI.base_rate AS cost_per_unit_in_company_currency, POI.item_group, MRI.project, \
				POI.description AS item_description, MRI.eta_date FROM \
				`tabMaterial Request Item` MRI \
				INNER JOIN `tabPurchase Order Item` POI ON MRI.substitute_item=POI.item_code AND \
				MRI.parent=POI.material_request WHERE MRI.docstatus < 2 AND POI.docstatus < 2 AND \
				MRI.substitute_item IS NOT NULL %s """%(condition), filters, as_dict=True)

	mr_items.extend(material_request_items)

        
def update_data_items(so_item, mr_item, data):
	mr = frappe.db.get_value("Material Request", mr_item.get("material_request"), 
			fieldname=["material_request_type", "request_by", "status"],
			as_dict=True)
	po = frappe.db.get_value("Purchase Order", mr_item.get("purchase_order"),
			fieldname=["term", "supplier", "rep_name", "currency", "tablix_status",\
			"transaction_date"], as_dict=True)
	item = frappe._dict({
			"item_code": so_item.get("item_code"),
			"cost_in_supplier_currency": mr_item.get("cost_in_customer_currency"),
			"cost_in_company_currency": mr_item.get("cost_in_supplier_currency"),
			"cost_per_unit_in_supplier_currency": mr_item.get("cost_per_unit_in_supplier_currency"),
			"cost_per_unit_in_company_currency": mr_item.get("cost_per_unit_in_supplier_currency"),
			"sale_in_company_currency": so_item.get("sale_in_company_currency"),
			"sale_in_customer_currency": so_item.get("sale_in_customer_currency"),
			"sale_per_unit_in_company_currency": so_item.get("sale_per_unit_in_company_currency"),
			"sale_per_unit_in_customer_currency": so_item.get("sale_per_unit_in_company_currency"),
			"sales_order": so_item.get("sales_order"),
			"material_request": mr_item.get("material_request"),
			"requested_qty": mr_item.get("requested_qty"),
			"ordered_qty": mr_item.get("ordered_qty"),
			"received_qty": mr_item.get("received_qty"),
			"boq": so_item.get("boq"),
			"payment_term": po.get("term"),
			"selling_qty": so_item.get("qty"),
			"company_currency": "AED",
			"customer_currency": "AED",
			"buying_item_name": mr_item.get("item_name"),
			"selling_item_code": so_item.get("selling_item_code"),
			"buying_item_code": mr_item.get("buying_item_code"),
			"selling_brand": mr_item.get("selling_brand"),
			"buying_brand": mr_item.get("buying_brand"),
			"item_group": mr_item.get("item_group"),
			"substitute_item": mr_item.get("substitute_item"),
			"mr_date": mr_item.get("schedule_date"),
			"po_date": po.get("transaction_date"),
			"eta_date": mr_item.get("eta_date"),
			"supplier_name": po.get("supplier"),
			"supplier_currency": po.get("currency"),
			"quotation": so_item.get("quotation"),
			"opportunity": so_item.get("opportunity"),
			"item_name": mr_item.get("item_name"),
			"item_description": mr_item.get("item_description"),
			"project": mr_item.get("project"),
			"project_location": so_item.get("project_site_name"),
			"material_request_type": mr.get("material_request_type"),
			"purchase_order_status": po.get("tablix_status"),
			"material_request_status": mr.get("status"),
			"buying_unit": mr_item.get("buying_unit"),
			"selling_unit": so_item.get("selling_unit"),
			"purchase_order": mr_item.get("purchase_order")
	})  

	data.append(item);
