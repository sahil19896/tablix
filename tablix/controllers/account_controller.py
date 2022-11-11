'''
	Developer Sahil
'''

import frappe
from frappe.utils import cint, flt, money_in_words
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt, datetime, now_datetime
import re
from tablix.controllers import base_controller
from erpnext.accounts.utils import get_fiscal_year

ACCOUNTS_DOC = [
		'Purchase Invoice', 'Sales Invoice'
	]

class AccountController(base_controller.BaseController):
	
	def validate_account(self):
		super(AccountController, self).validate()

		self.update_taxes_and_charges()
		if not self.dt in ACCOUNTS_DOC:
			return
		elif self.dt == "Sales Invoice":
			self.validate_sales_invoice()


	def validate_account_submit(self):
		super(AccountController, self).validate_submit()
		
	
	def validate_account_cancel(self):
		super(AccountController, self).validate_cancel()

	def update_taxes_and_charges(self):
		if self.dt not in ['Purchase Invoice', 'Purchase Order', 'Delivery Note',\
			'Sales Invoice', 'Purchase Receipt', 'Quotation']:
			return 
		if not hasattr(self.doc, "taxes"):
			return
		self.doc.vat = 0.0
		self.doc.duties = 0.0
		self.doc.other_charges = 0.0
	
		for tax in self.doc.get("taxes"):
			if not tax.get("select_tax_type"):
				frappe.throw(_("Set Tax option to one of these options: \
					[VAT, Duties, Other Charges] in TAX ITEM row."))

			if tax.get("select_tax_type") == "VAT":
				self.doc.vat = tax.get("tax_amount")
			if tax.get("select_tax_type") == "Duties":
				self.doc.duties = tax.get("tax_amount")
			if tax.get("select_tax_type") == "Other Charges":
				self.doc.other_charges = tax.get("tax_amount")


	def validate_sales_invoice(self):
		self.doc.in_words = money_in_words(self.doc.outstanding_amount, self.doc.currency)


class PaymentController(object):
		
	def __init__(self, doc, doctype, method):
		self.doc = doc
		self.doctype = doctype
		self.method = method


	def validate_payment(self):
		if self.doctype == "Journal Entry":
			self.validate_journal_entry()
		elif self.doctype == "Payment Entry":
			self.validate_payment_entry()
		elif self.doctype == "Expense Claim":
			self.validate_expense_claim()

	def validate_journal_entry(self):
		self.discard_currency_label()
		
	def discard_currency_label(self):
		com = re.compile(r'AED|,|AND')
		
		company_currency = frappe.db.get_value("Company", filters={"name":self.doc.company}, 
					fieldname=["default_currency"], as_dict=True)
		in_words = money_in_words(self.doc.total_credit, company_currency.get("default_currency") or "AED")
		self.doc.amt_words =  com.sub("", in_words)

	def validate_payment_entry(self):
		pass


	def validate_expense_claim(self):
		pass


