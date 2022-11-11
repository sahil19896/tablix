
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt, now_datetime, getdate, nowdate
from frappe.model.mapper import get_mapped_doc
from erpnext.selling.doctype.quotation.quotation import _make_customer

@frappe.whitelist()
def make_contact(source_name, target_doc=None):
	target_doc = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Contact",
			"field_map": {
				"lead_name": "first_name",
				"email_id": "email_id",
				"contact_type": "type",
				"company_name": "organization_name"
			}
		}}, target_doc)

	return target_doc


@frappe.whitelist()
def make_quotation(source_name, target_name=None):
	
	return get_mapped_doc("BOQ Profile", source_name, {

			"BOQ Profile":{
				"doctype": "Quotation",
				"field_map":{
					"enquiry_from": "quotation_to",
					"customer": "customer",
					"lead": "lead",
					"name": "boq_profile"
				}
			}
		})




@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
        quotation = frappe.db.get_value("Quotation", source_name, ["transaction_date",\
				 "valid_till"], as_dict = 1)
        if quotation.valid_till and (quotation.valid_till < quotation.transaction_date or\
				 quotation.valid_till < getdate(nowdate())):
                frappe.throw(_("Validity period of this quotation has ended."))

        return _make_sales_order(source_name, target_doc)


def _make_sales_order(source_name, target_doc=None, ignore_permissions=True):
	customer = _make_customer(source_name, ignore_permissions)
	print("sahil saini \n\n\n")
	def set_missing_values(source, target):
		if customer:
			target.customer = customer.name
			target.customer_name = customer.customer_name
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)

	doclist = get_mapped_doc("Quotation", source_name, {
			"Quotation": {
				"doctype": "Sales Order",
				"validation": {
					"docstatus": ["=", 1]
				}
			},
			"Quotation Item": {
				"doctype": "Sales Order Item",
				"field_map": {
					"rate": "rate",
					"amount": "amount",
					"parent": "prevdoc_docname",
					"name": "quotation_item_detail",
				},
				"postprocess": update_item
			},
			"Sales Taxes and Charges": {
				"doctype": "Sales Taxes and Charges",
				"add_if_empty": True
			},
			"Sales Team": {
				"doctype": "Sales Team",
				"add_if_empty": True
			},
			"Quotation Site Costing Item": {
				"doctype": "Sales Order Site Costing Item"
			},
			"Payment Schedule": {
				"doctype": "Payment Schedule",
				"add_if_empty": True
			}
		}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	return doclist	



@frappe.whitelist()
def get_qt_cost(quotation=None):
	from tablix.tablix_crm.quotation_costing import get_quotation_cost
	return  get_quotation_cost(quotation)
