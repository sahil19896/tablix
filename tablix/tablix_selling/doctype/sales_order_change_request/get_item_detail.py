
import frappe
from frappe.utils import cint, cstr, flt
from frappe import _, msgprint, throw

@frappe.whitelist()
def get_item_detail(item_code, sales_order):
	from erpnext.stock.get_item_details import get_item_details as get_details
	data =  {"item_code": item_code}
	so = frappe.get_doc("Sales Order", sales_order)
	data.update({
		"price_list": so.selling_price_list,
		"company": so.company, "customer": so.customer,
		"currency": so.currency, "conversion_rate":so.conversion_rate,
		"plc_conversion_rate": so.plc_conversion_rate, 
		"price_list_currency": so.price_list_currency,
		"order_type": "Sales", "doctype": "Sales Order",
	})
	return get_details(data)
