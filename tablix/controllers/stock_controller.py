'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe.utils import cint, flt, money_in_words
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt, datetime, now_datetime
from tablix.controllers import account_controller



AGAINST_VOUCHER = ['Purchase Order', 'Sales Order', 'Delivery Note', "Purchase Invoice",
		'Sales Invoice', 'Material Request', 'Purchase Receipt'
	]

class StockController(account_controller.AccountController):
	
	def validate_stock(self):
		super(StockController, self).validate()
		if self.dt == "Material Request":
			self.validate_material_request()
			self.send_notification()

		if self.dt == "Delivery Note":
			self.validate_delivery_note()


	def validate_stock_submit(self):
		super(StockController, self).validate_submit()

	def validate_stock_cancel(self):
		super(StockController, self).validate_cancel()

	def validate_delivery_note(self):
		pass


	def validate_material_request(self):
		pass
