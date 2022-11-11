

'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''

import frappe, json
from frappe.utils import flt, cint, cstr
from frappe import _, msgprint, throw

'''
	Calculate Taxes and charges for every document
'''
def get_taxes_and_charges(doc, master_doctype, master_name):
	from erpnext.controllers.accounts_controller import  get_taxes_and_charges	
	setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	taxes = get_taxes_and_charges(master_doctype=master_doctype, master_name=master_name)
	if doc and isinstance(doc, str):
		doc = json.loads(doc)
	if setting.get("auto_calculate"):
		_taxes = []
		field = "base_"+cstr(setting.get("apply_on")) or "base_net_total"
		if doc.get(field):
			for item in taxes:
				_item = frappe._dict(item)
				if item.get("rate"):
					continue
				else:
					acc = frappe.db.get_value("Account", item.get("account_head"), fieldname="tax_rate", as_dict=True)
					if acc and acc.get("tax_rate"):
						_item["base_tax_amount"] = flt(doc.get(field))*flt(acc.get("tax_rate"))/100
						_item["base_total"] = flt(doc.get(field))+_item.get("base_tax_amount")
						_item["base_tax_amount_after_discount_amount"] =  _item.get("base_tax_amount")
						currency  = frappe.db.get_value("Company", doc.get("company"), "default_currency", as_dict=True)
						if currency and currency.get("default_currency") != doc.get("currency"):
							_item["tax_amount"] = _item.get("base_tax_amount")/doc.get("conversion_rate")
							_item["total"] = _item.get("base_total")/doc.get("conversion_rate")
							_item["amount_after_discount_amount"] = \
								_item.get("base_tax_amount_after_discount_amount")/doc.get("conversion_rate")
						else:
							_item["tax_amount"] = _item.get("base_tax_amount")
							_item["total"] = _item.get("base_total")	
							_item["amount_after_discount_amount"] = \
								_item.get("base_amount_after_discount_amount")

				_taxes.append(_item)
							
		return _taxes
	
			
	else:
		return taxes


class CurrencyExchange:
	
	def __init__(self, doc):
		if doc and isinstance(doc, str):
			doc = json.loads(doc)

		self._items = []
		self._site_costing = []
		self._vat_items = []
		self.doc = frappe._dict(doc)

	def calculate_items_rate(self):
			
		_items  = []
		company_currency = frappe.db.get_value("Company", self.doc.get("company"),\
					 fieldname="default_currency", as_dict=True)
		if company_currency and company_currency.get("default_currency") != self.doc.currency:
			if self.doc.get("conversion_rate") == flt(1):
				return self.doc.get("items")	
			conversion_rate = self.doc.get("conversion_rate")
			for item in self.doc.get("items"):
				_item  = frappe._dict(item)
				_item.price_list_rate = item.get("price_list_rate") / flt(conversion_rate)
				_item.rate =  item.get("base_rate")/flt(conversion_rate)
				_item.net_rate  = item.get("base_net_rate")/flt(conversion_rate)
				_item.amount = item.get("base_amount")/flt(conversion_rate)
				_item.net_amount  = item.get("base_net_amount")/flt(conversion_rate)

			



	
