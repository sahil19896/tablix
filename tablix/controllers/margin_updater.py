'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe.utils import cint, flt, money_in_words
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt
import math
'''
	Update Margin for Quotation and Sales Order
'''
class MarginUpdater:

	def __init__(self, doc, dt):
		self.doc = doc
		self.dt = dt
		self.boq_profile = frappe._dict()
		if dt == "Quotation":
			self.boq_profile = frappe.get_doc("BOQ Profile", self.doc.get("boq_profile"))
		
		self.site_total = frappe._dict()
		self.reset_totals()
	
	def reset_totals(self):
		# RESET TOTAL COST
		self.doc.total_cost_amount = 0.0
		self.doc.total_margin_amount = 0.0
		self.doc.base_total_cost_amount = 0.0
		self.doc.base_total_margin_amount = 0.0
		# RESET BOQ COST
		self.doc.boq_selling_amount = 0.0
		self.doc.boq_selling_amount_after_discount  = 0.0
		self.doc.boq_cost_amount = 0.0
		self.doc.boq_margin_amount = 0.0
		self.doc.boq_margin_percentage = 0.0
		# RESET AMC COST
		self.doc.amc_selling_amount = 0.0
		self.doc.amc_selling_amount_after_discount = 0.0
		self.doc.amc_cost_amount = 0.0
		self.doc.amc_margin_amount = 0.0
		self.doc.amc_margin_percentage = 0.0
		# RESET SPARE PART COST
		self.doc.spare_part_cost_amount = 0.0
		self.doc.spare_part_selling_amount = 0.0
		# RESET SITE TOTAL COST
		self.reset_site_total()

	def reset_site_total(self):
		if self.doc.get("site_costing_items"):
			temp_list = [site for site in self.doc.get("site_costing_items")]
			for idx, site in enumerate(temp_list):
				self.doc.remove(site)	

		
	def update_site_costing(self):
		idx = 1
		for key, val in self.site_total.items():
			self.doc.append("site_costing_items", {"total_sale": val.get("total_sale"),
					"total_cost": val.get("total_cost"),
					"idx": idx, "site": key})	
			idx += 1
		
	def validate_margin(self):
		self.calculate_cost_and_margin()
		self.calculate_discount()
		self.doc.validate()
		self.update_site_costing()
		self.calculate_total_costing()
		self.calculate_optional_items_total()

	def calculate_cost_and_margin(self):
		items = self.doc.get("items")
		site_name = ""
		for item in items:
			item.discount_percentage = 0.0
			if item.idx == 1 and not item.site:
				frappe.throw(_("Please enter site name in first item"))
			elif item.site:
				site_name = item.site
			item.site = site_name
			item_detail = frappe.db.get_value("Item", item.get("item_code"), ["is_stock_item"], as_dict=True)
			if (item.get("is_amc_item") and item_detail.get("is_stock_item")) \
				or (item.get("is_service_item") and item.get("is_stock_item")):
				frappe.magprint(_("AMC/Service Item must be <b>Non Stock Item</b>."))
	
			if not item.get("select_margin_type"):
				frappe.throw(_("Select Margin Type"))
			if item.get("is_amc_item"):
				self.calculate_amc_item_cost(item)
			elif not(item.get("is_amc_item") and item.get("is_spare_part_item")):
				self.doc.is_spare_part_inlcuded = True
				self.calculate_boq_item_cost(item)

			if item.get("is_spare_part_item"):
				self.doc.is_spare_part_included = True
				self.calculate_spare_part_item_cost(item)

			self.calculate_site_wise_total(item)	
			self.update_price_list_rate(item)
			self.update_base_currency_prices(item)
	
	def calculate_margin_values(self, item):
		margin_type = item.get("select_margin_type")
		margin_percent = 1-(flt(self.doc.get("margin_percent"))/100.0) \
				if self.doc.get("margin_percent") else 0.0
		if item.get("cost_amount") and margin_type == "Percentage" and margin_percent:
			item.selling_amount = flt(item.get("cost_amount"))/margin_percent

		elif item.get("cost_amount") and margin_type == "Amount":
			if not item.get("selling_amount"):
				item.selling_amount = flt(item.get("cost_amount"))
		else:
			item.selling_amount = flt(item.get("cost_amount"))
		self.add_fractional_value(item, "selling_amount")

		if item.get("selling_amount"):
			
			item.margin_amount = item.get("selling_amount") - flt(item.get("cost_amount"))
			if item.margin_amount:
				item.margin_percent = item.margin_amount/item.selling_amount*100.0
			else:
				item.margin_percent = 0.0
				
		item.total_cost_amount   = flt(item.get("cost_amount")) * flt(item.get("qty"))
	
	def add_fractional_value(self, item, field):
                if item.get(field):
                        frac, whole = math.modf(item.get(field))
                        if frac > 0:
                                item.update({field: whole + 1})

		#frappe.msgprint(item.get("selling_amount"))

	def update_price_list_rate(self, item):
		item.margin_type="Amount"
		selling_amount = flt(item.get("selling_amount"))
		item.rate = selling_amount
		item.amount = selling_amount * item.get("qty")
		if item.get("price_list_rate") and item.get("cost_amount") and item.get("selling_amount"):
			margin = item.get("selling_amount") - flt(item.get("price_list_rate"))
			if margin:
				item.margin_rate_or_amount = margin

	# SPARE PARTS COST
	def calculate_spare_part_item_cost(self, item):
		self.doc.spare_part_selling_amount += flt(item.get("amount"))
		self.doc.spare_part_cost_amount += flt(item.get("total_cost_amount"))

	# BOQ ITEM COSTING		
	def calculate_boq_item_cost(self, item):
		self.doc.boq_selling_amount += flt(item.get("amount"))
		self.doc.boq_cost_amount += flt(item.get("total_cost_amount"))	

	# AMC ITEM COSTING
	def calculate_amc_item_cost(self, item):
		self.doc.amc_selling_amount += flt(item.get("amount"))
		self.doc.amc_cost_amount += flt(item.get("total_cost_amount"))

	# UPDATE AMC BASE CURRENCY COSTING
	def update_base_currency_prices(self, item):
		currency  = frappe.db.get_value("Company", self.doc.company, ["default_currency"], as_dict=True)
		if currency.get("default_currency") != self.doc.get("currency"):
			c_rate = self.doc.get("conversion_rate")
			item.base_cost_amount = item.cost_amount * c_rate
			item.base_selling_amount = item.cost_amount * c_rate
			item.base_total_cost_amount = item.cost_amount * c_rate
			item.base_margin_amount = item.margin_amount * c_rate			
		else:
			item.base_cost_amount = item.cost_amount
			item.base_selling_amount = item.cost_amount
			item.base_total_cost_amount = item.cost_amount
			item.base_margin_amount = item.margin_amount

	# CALCULATE SITE WISE COSTING
	def calculate_site_wise_total(self, item):
		if item.get("is_spare_part_item"):
			return
		if not item.get("is_amc_item") and not item.get("site"):
			frappe.throw(_("Please enter <b>Site Name</b> for item {0}".format(item.get("item_code"))))
		if not self.site_total.get(item.get("site")):
			self.site_total[item.get("site")] = frappe._dict({"total_sale":0.0, "total_cost": 0.0})
		site = self.site_total[item.get("site")]
		site.total_sale += item.get("selling_amount")
		site.total_cost += item.get("cost_amount")

	def calculate_discount(self):
		self.doc.discount_amount = flt(self.doc.get("boq_discount"))  + flt(self.doc.get("amc_discount"))
	
	def calculate_total_costing(self):
		# AMC TOTAL COSTING
		if self.doc.get("amc_selling_amount"):
			discount = 0.0
			if self.doc.get("amc_discount"):	
				discount = self.doc.get("amc_discount")
			self.doc.amc_selling_amount_after_discount = self.doc.get("amc_selling_amount") - discount
			if self.doc.get("amc_selling_amount_after_discount"):
				self.doc.amc_margin_amount = self.doc.amc_selling_amount_after_discount - self.doc.amc_cost_amount
			if self.doc.amc_margin_amount:
				self.doc.amc_margin_percentage = self.doc.amc_margin_amount/self.doc.amc_selling_amount*100.0

		# BOQ TOTAL COSTING
		if self.doc.get("boq_selling_amount"):
			discount = 0.0
			if self.doc.get("boq_discount"):	
				discount = self.doc.get("boq_discount")
			self.doc.boq_selling_amount_after_discount = self.doc.get("boq_selling_amount") - discount
			self.doc.boq_costing_amount_after_discount = self.doc.get("boq_cost_amount") - discount
			if self.doc.get("boq_selling_amount_after_discount"):
				self.doc.boq_margin_amount = self.doc.boq_selling_amount_after_discount - self.doc.boq_costing_amount_after_discount
			if self.doc.boq_margin_amount:
				self.doc.boq_margin_percentage = self.doc.boq_margin_amount/self.doc.boq_selling_amount*100.0

		# CALCULATING GRAND TOTAL COSTING		
		self.doc.total_cost_amount = self.doc.boq_cost_amount + self.doc.amc_cost_amount
		self.doc.total_margin_amount = flt(self.doc.boq_margin_amount) + flt(self.doc.amc_margin_amount)
		self.doc.base_total_cost_amount = self.doc.total_cost_amount * self.doc.conversion_rate or 1.0
		self.doc.base_total_margin_amount = self.doc.total_margin_amount * self.doc.conversion_rate or 1.0
		if self.doc.total_margin_amount:
			self.doc.total_margin_percent = self.doc.total_margin_amount/self.doc.total*100.0

	def calculate_optional_items_total(self):
		self.doc.optional_item_margin_amount = 0.0
		self.doc.optional_item_margin_percentage = 0.0
		self.doc.optional_item_selling_amount = 0.0
		self.doc.optional_item_cost_amount = 0.0
		if self.doc.get("optional_items"):
			margin_percentage = 1.0-self.doc.get("margin_percent")/100.0
			for item in self.doc.get("optional_items"):
				if not item.get("select_margin_type"):
					frappe.throw(_("Please select <b>Margin Type</b> for item {0} in \
						row no. {1}".format(item.get("item_code"), item.get("idx"))))

				self.calculate_margin_values(item)
				self.update_base_currency_prices(item)
				item.total_selling_amount = item.selling_amount * item.qty
				item.base_total_selling_amount = item.base_selling_amount * item.qty or 1
				self.doc.optional_item_selling_amount += cint(item.selling_amount) * cint(item.qty)
				self.doc.optional_item_cost_amount += cint(item.cost_amount) * cint(item.qty)
			
			self.doc.optional_item_margin_amount = self.doc.optional_item_selling_amount-self.doc.optional_item_cost_amount
			if self.doc.optional_item_margin_amount:
				self.doc.optional_item_margin_percentage = self.doc.optional_item_margin_amount/ \
							self.doc.optional_item_selling_amount*100.0

