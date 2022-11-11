'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''

import frappe, json
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr, datetime
from tablix.utils import get_datetime
from frappe.utils import cint, flt, money_in_words
from tablix.notifications.notification_controller import NotificationController
import sys


SELLING_DOCTYPE = ["Quotation", "Sales Order"]
STOCK_DOCTYPE = ['Delivery Note', 'Purchase Receipt', "Material Request"]
BUYING_DOCTYPE = ['Purchase Order']
CRM = ['Lead', 'Opportunity']
ACCOUNT_DOCTYPE = ['Sales Invoice', 'Purchase Invoice']
PAYMENTS = ['Journal Entry', 'Payment Entry']
HR = ['Expense Claim', 'Leave Application']
SUPPORT = ['Issue', "Maintenance Contract"]
MASTER = ['Supplier']

def validate_controller(doc, method):
	doctype = doc.meta.get("name")
	controller = None
	try:
		# Execute Master Controller to validate the Master data information
		if doctype in MASTER:
			from tablix.controllers.master_controller import MasterController		
			MasterController(doc, doctype, method).validate()

		#Execute Selling Controller to validate the information
		if doctype in SELLING_DOCTYPE:
			from tablix.controllers.selling_controller import SellingController
			if method == "validate":
				SellingController(doc, doctype, method).validate_selling()
			elif method == "on_submit":
				SellingController(doc, doctype, method).validate_selling_submit()
			elif method == "on_cancel":
				SellingController(doc, doctype, method).validate_selling_cancel()

		#Execute Buying Controller to validate the information
		elif doctype in BUYING_DOCTYPE:
			from tablix.controllers.buying_controller import BuyingController
			if method == "validate":
				BuyingController(doc, doctype, method).validate_buying()
			elif method == "on_submit":
				BuyingController(doc, doctype, method).validate_buying_submit()
			elif method  == "on_cancel":
				BuyingController(doc, doctype, method).validate_buying_cancel()
		
		#Execute Account Controller to validate the information
		elif doctype in ACCOUNT_DOCTYPE:
			from tablix.controllers.account_controller import AccountController
			if method == "validate":
				AccountController(doc, doctype, method).validate_account()
			elif method == "on_submit":
				AccountController(doc, doctype, method).validate_account_submit()
			elif method == "on_cancel":
				AccountController(doc, doctype, method).validate_account_cancel()
		
		#Execute Stock Controller to validate the information		
		elif doctype in STOCK_DOCTYPE:
			from tablix.controllers.stock_controller import StockController
			if method == "validate":
				StockController(doc, doctype, method).validate_stock()
			elif method == "on_submit":
				StockController(doc, doctype, method).validate_stock_submit()
			elif method == "on_cancel":
				StockController(doc, doctype, method).validate_stock_cancel()
	
		#Execute Payment Controller to validate the information		
		elif doctype in PAYMENTS:
			from tablix.controllers.account_controller import PaymentController
			PaymentController(doc, doctype, method).validate_payment()

		#Execute HR Controller to validate the information
		elif doctype in HR:
			from tablix.controllers.hr_controller import HRController
			if method == "validate":
				HRController(doc, doctype, method).validate()
			if method == "on_submit":
				HRController(doc, doctype, method).validate_submit()
			if method == "on_cancel":
				HRController(doc, doctype, method).validate_cancel()

		#Execute Suport controller to validate the information
		elif doctype in SUPPORT:
			from tablix.controllers.support_controller import SupportController
			if method == "validate":
				SupportController(doc, doctype, method).validate()
			elif method == "on_sumit":
				SupportController(doc, doctype, method).validate_support_submit()
			elif method == "on_cancel":
				SupportController(doc, doctype, method).validate_support_cancel()
		elif doctype in CRM:
			from tablix.controllers.crm_controller import CRMController
			CRMController(doc, doctype, method).validate_crm()


	except Exception as e:
		print("----"*10)
		print(frappe.get_traceback())
		print("----"*10)
		#frappe.throw(e.message)


'''
	Base controller for validation purpose
'''
SO_VALIDATION_DOC = ['Purchase Order', 'Material Request', 'Purchase Receipt', 'Purchase Invoice']

class BaseController(NotificationController):
	
	def __init__(self, doc, doctype, method):
		quotation = ""
		self.dt = doctype
		self.doc = doc
		self.method = method
		self.setting = frappe.get_doc("Tablix Setting", "Tablix Setting")

	def validate(self):
		self.validate_prev_links()
		self.update_taxes_and_charges()
		self.send_notification()

	
	def validate_submit(self):
		self.validate_prev_links()
		if(self.dt in ["Sales Order", "Quotation"]):
			self.validate_cost_and_sale_amount()


	def validate_cancel(self):
		pass


	def validate_prev_links(self):
		if(self.dt=="Quotation" or self.dt=="Sales Order"):
			return False
		self.quotation = None
		fields_map = child_items_map[self.dt]
		items = self.doc.get(fields_map.get("table_field"))
		temp = None
		for item in items:
			if not(item.get(fields_map.get("source_dt")) and item.get(fields_map.get("source_item_dt"))):
				pass#frappe.msgprint(_("Are you following correct workflow to create document,\
				#	{item_code} doesn't exits in Quotation".format(item_code=item.get("item_code"))), raise_exception=1)
			temp = item
			self.update_prevdoc_docname(item)
		self.quotation = temp.get("prevdoc_docname") or temp.get("quotation_detail")

	def update_prevdoc_docname(self, item):
		if self.dt == "Sales Order":
			if not item.get("quotation_detail") and item.get("prevdoc_docname"):
				item.quotation_detail = item.get("prevdoc_docname")
			elif not item.get("quotation_detail") and not item.get("prevdoc_docname"):
				frappe.throw(_("You can't add manual items in <b>Sales Order</b>"))

	
	def get_project_name(self):
		project_name = ""
		if(self.dt=="Quotation"):
			project_name = self.doc.get("customer")
		if(self.dt=="Sales Order"):
			project_name = self.doc.get("customer")
		
		if(self.dt in ['Material Request', 'Purchase Order']):
			for item in self.doc.get("items"):
				if item.get("project") not in project_name:
					project_name += " {project}".format(project=item.get("project"))

	
		return project_name	
		
	def validate_cost_and_sale_amount(self):
	
		for item in self.doc.get("items"):
			if(not item.get("selling_amount") or not item.get("cost_amount")):
				frappe.throw(_("You can't leave <b>Cost and Sale Amount</b> blank in Items."))

		
child_items_map = {
	"Sales Order": {
		"source_dt": "quotation_item_detail",
		"source_item_dt": "prevdoc_docname",
		"table_field": "items"
	},
	"Material Request":{
		"source_dt": "sales_order",
		"source_item_dt": "sales_order_item",
		"table_field": "items"
	},
	"Purchase Order":{
		"source_dt": "sales_order",
		"source_item_dt": "sales_order_item",
		"table_field": "items"
	},
	"Purchase Invoice":{
		"source_dt": "purchase_order",
		"source_item_dt": "po_detail",	
		"table_field": "items"
	},
	"Sales Invoice":{
		"source_dt": "sales_order",
		"source_item_dt": "so_detail",
		"source_dt1": "delivery_note",
		"source_item_dt1": "dn_detail",
		"table_field": "items"
	},
	"Delivery Note":{
		"source_dt": "against_sales_order",
		"source_item_dt": "so_detail",
		"source_dt1": "against_sales_invoice",
		"source_item_dt1": "si_detail",
		"table_field": "items"
	},
	"Purchase Receipt": {
		"source_dt": "purchase_order",
		"source_item_dt": "purchase_order_item",
		"table_field": "items"
	}
}

