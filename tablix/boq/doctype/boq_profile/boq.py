# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _, throw
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, flt, cstr, round_based_on_smallest_currency_fraction, get_link_to_form, money_in_words, today
from frappe.desk.form import assign_to
from erpnext.accounts.party import get_party_account_currency
import datetime
from tablix.utils.checklist import update_checklist
import math
from tablix.controllers.base import BaseController

form_grid_templates = {
	"items": "templates/form_grid/boq_grid.html"
}
date = "2016-01-01"

MARGIN_STATUS  = ['Site Survey', 'Designing', 'Manager Approval', 'Boq Complete']
FIELD_MAP = ['parent', 'parenttype', 'parentfield', 'modified', 'owner', 'doctype', 'name', 'docstatus', 'creation']

class Boq(Document, BaseController):

	def validate(self):
		super(Boq, self).validate(self, "Boq")
		self.validate_project("project_site_name")
		self.validate_attachments()
		self.temp_tablix_status = self.tablix_status
		self.calculate_totals()
		self.update_defaults()
		self.validate_proposal()
		
		self.send_notification()
	
	'''
		Update defaults values
	'''

	def on_submit(self):
		self.method = "on_submit"
		self.validate_margin()
		self.doctype = "Boq",
		self.doc = self
		self.clear_previous_assignment()
	
	def update_defaults(self):
	
	
		if self.get("is_amc"):
			if self.comprehensive:
				self.amc_type = "Comprehensive"
			if self.non_comprehensive:
				self.amc_type = "Non Comprehensive"

		if self.expected_date < date:
			self.expected_date = today()
		if self.opp_owner == "" or self.opp_owner is None:
			self.opp_owner = frappe.db.get_value("Opportunity", self.opportunity, "owner")
			
		if self.boq:
			self.proposed_project_completion_time_ = self.proposed_project_completion_time + self.material_delivery_period
			
			
		if self.tablix_status in ["BDM Verified", 'Sales Complete']:
			if self.docstatus == 2:
				return 
			self.validate_payment_terms_total()
			
		for data in self.get('payment_term_table'):
			data.opp_ref = self.opportunity
		
		doc = frappe.get_doc("Opportunity", self.opportunity)
		if doc.tablix_status != 'Boq':
			doc.tablix_status = 'Boq'

		if((self.boq and self.is_proposal) or self.is_amc):
			self.update_checklist()			

	'''
		Validate Attachments
	'''
	def validate_attachments(self):
		if not self.tablix_status == "Designing":
			return
		if self.technical_docs or self.compliance_statement:
			if not frappe.db.sql("select name from `tabFile` where \
						attached_to_name = %s", self.name):
				self.raise_exception(_("No documents attached"))


	'''
		Calculate Total Pricing
	'''	
	def calculate_totals(self):
		self.calculate_project_total()
		self.calculate_amc_total()
		self.calculate_total_discount()
		self.calculate_total_cost()
		self.calculate_grand_total()
	
	'''
		Validate Project Item pricing
	'''
	def validate_project_item(self, item):
		if not item.get("current_cost"):
			self.raise_exception(_("Please enter <b>Cost Price</b> for row {0}".format(item.get("idx"))))	
		if self.get("tablix_status") not in MARGIN_STATUS:
			if (not self.get("boq_desired_margin") and  not item.get("margin_percent")):
				self.raise_exception(_("""Please Enter Margin Either in <b>Item {0} in row {1}</b> or\
					 in <b>Main Form</b>""".format(item.get("item_code"), item.get("idx"))))
			if item.get("margin_type") == "Amount" and not (item.get("current_cost") and item.get("selling_price")):
				self.raise_exception(_("Please enter <b>Cost Price</b>and<b>Selling Price</b> if you want apply manual margin"))

	'''
		Calculate Total if Type is BOQ
	'''	
	def calculate_project_total(self):
		self.site_costing = []
		if not self.get("boq"):
			self.items = []
			self.site_costing = []
		site_wise_total = frappe._dict()
		self.service_cost = 0.0
		self.total_sale = 0.0
		self.total_cost = 0.0
		main_margin = self.get("boq_desired_margin")
		last_site_name = ""
		margin  = self.get("boq_desired_margin")
		for item in self.get("items"):
			if item.get("site"):
				last_site_name = item.get("site")
			item.opp_ref = self.get("opportunity")	
			self.validate_project_item(item)
			if item.item_group in ["Services","Professional Services"] :
					self.service_cost += flt(item.cost_amount)
			

			if item.get("margin_type") == "Percentage" and margin:
				item.selling_price = item.get("current_cost")/(1-flt(margin)/100.0)
				self.add_fraction_value(item, "selling_price")
				item.margin = item.get("selling_price") - item.get("current_cost")
				item.margin_percent = item.get("margin")/item.get("selling_price")*100.0

			elif item.get("margin_type") == "Amount":
				_margin = item.get("selling_price")-item.get("current_cost")
				item.margin_percent = flt(_margin)/item.get("selling_price")*100.0
				item.margin = item.get("selling_price")-item.get("current_cost")
				
			item.sale_amount = flt(item.get("qty")) * flt(item.get("selling_price"))
			item.cost_amount = flt(item.get("qty")) * flt(item.get("current_cost"))
		
			self.add_fraction_value(item, "sale_amount")
			self.add_fraction_value(item, "cost_amount")
			self.update_site_wise_total(item, site_wise_total, last_site_name)
			self.total_cost += item.cost_amount
			self.total_sale += item.sale_amount

		# Update Material Cost
		self.material_cost = self.total_cost - self.service_cost
		# Update Site Costing
		for key, val in site_wise_total.items():
			self.append("site_costing", val)
		

	
	'''
		Update Site Wise total, Only for Project Items
	'''
	def update_site_wise_total(self, item, site_wise_total, site):
		if not site_wise_total.has_key(site):
				site_wise_total[site] = frappe._dict({
						"total_sale":0.0,
						"total_cost": 0.0,
						"site": site
				})

		_temp = site_wise_total.get(site)
		_temp.total_sale += item.get("sale_amount")
		_temp.total_cost += item.get("cost_amount")
		
	
	'''
		Calculate AMC Total
	'''	
	def calculate_amc_total(self):
		if not self.get("is_amc"):
			self.amc_items = []
			self.amc_preventive = []
			self.amc_reactive = []
			self.amc_service_items = []
		if not self.get("comprehensive"):
			self.amc_spare_parts = []
			
		self.calculate_total_preventive_cost()
		self.calculate_total_reactive_cost()
		self.calculate_spare_parts_cost()
		self.calculate_total_amc_cost()
	
	'''
		Total Cost for preventive items

	'''			
	def calculate_total_preventive_cost(self):
		total_cost = 0.0
		day_uom = self.get_day_uom(self.get("amc_preventive") or [])
		for item in self.get("amc_preventive"):
			item.preventive_opportunity = self.get("opportunity")
			if item.get("uom") != day_uom.get("uom"):
				if item.get("uom") == "rate/day":
					total_cost += flt(item.get("total")) * flt(day_uom.get("total"))
				else:
					total_cost += flt(item.get("total"))
		self.cost_for_ppm = total_cost
		if self.one_year_maintenance:
			self.total_cost_preventive_maintenance = flt(self.cost_for_ppm) * flt(self.one_year_maintenance)

	'''
		Total Cost for reactive Items
	'''	
	def calculate_total_reactive_cost(self):
		total_cost = 0.0
		for item in self.get("amc_reactive"):
			item.reactive_opportunity = self.get("opportunity")
			total_cost += flt(item.get("total"))		
	
		self.cost_for_rm = total_cost
		if self.no_of_calls:
                                self.total_cost_reactive_maintenance = self.cost_for_rm * self.no_of_calls
	
	
	'''
		Total Cost for Spareparts
	'''	
	def calculate_spare_parts_cost(self):
		total_cost = 0.0
		for item in self.get("amc_spare_parts"):
			total_cost += item.get("amount")  or 0.0
			item.sp_opportunity = self.get("opportunity")
	
		self.total_cost_for_spare_parts = total_cost
		total_cost = 0.0
		for item in self.get("amc_extended_warranty"):
			item.ew_opportunity  = self.get("opportunity")
			total_cost = item.get("amount") or 0.0	
		self.extended_warranty_cost = total_cost

			
		
	'''
		Total Cost for Spare AMC
	'''

	def calculate_total_amc_cost(self):
		months = 0
		self.amc_total_sale_  = 0.0
		self.amc_total_cost = 0.0
		self.total_cost_amt = 0.0
		for item in self.get("amc_yearly"):
			item.update(amc_item_code_map.get(item.get("select_year")))
			extended  = self.get_extended_cost(item)
			item.amc_opportunity = self.get("opportunity")
			item.preventive_cost = self.total_cost_preventive_maintenance
			item.reactive_cost = self.total_cost_reactive_maintenance
			item.spare_part_cost = self.total_cost_for_spare_parts
			item.extended_warranty_cost = 0.0
			if extended.get("amount"):
				item.extended_warranty_cost  = extended.get("amount")
			item.amc_yearly_total = item.preventive_cost + item.reactive_cost + item.spare_part_cost + item.extended_warranty_cost
			if item.get("percentage"):
				percentage = item.get("percentage")
				item.am_preventive_cost = item.preventive_cost /(1-(flt(percentage)/100))
				item.am_reactive_cost = item.reactive_cost /(1-(flt(percentage)/100))
				item.am_spare_part_cost = item.spare_part_cost/(1-(flt(percentage)/100))
				item.am_extended_warranty_cost =  item.extended_warranty_cost /(1-(flt(percentage)/100))
			else:			
				item.am_preventive_cost = item.preventive_cost
				item.am_reactive_cost = item.reactive_cost
				item.am_spare_part_cost = item.spare_part_cost
				item.am_extended_warranty_cost =  item.extended_warranty_cost
			
			item.am_amc_yearly_total = item.am_preventive_cost + item.am_reactive_cost + item.am_spare_part_cost + item.am_extended_warranty_cost
			item.margin_value_amc_yearly = item.am_amc_yearly_total  - item.amc_yearly_total
			item.adm_amc_yearly_total = item.am_amc_yearly_total
			if self.get("amc_desired_margin"):
				item.adm_amc_yearly_total = item.am_amc_yearly_total/(1-(flt(self.get("amc_desired_margin"))/100))
			self.add_fraction_value(item, "adm_amc_yearly_total")
			self.amc_total_sale_ += item.adm_amc_yearly_total
			self.amc_total_cost +=  item.am_amc_yearly_total	
			months += 1
		self.total_charges_of_maintenance = self.total_cost_preventive_maintenance + self.total_cost_reactive_maintenance + \
							self.total_cost_for_spare_parts + self.extended_warranty_cost
		self.total_cost_amt = self.amc_total_cost
	
		self.total_amc_months = months * 12	

	'''
		Calculate Total Discount
	'''	
	def calculate_total_discount(self):
	
		self.boq_total_discount = 0.0
		self.amc_total_discount = 0.0
		self.net_discount = 0.0
		for discount in self.get("boq_discount_item"):
			discount.discount_opportunity = self.get("opportunity")
			discount.boq_total_discount  = discount.boq_discount + discount.boq_special_discount + \
						discount.boq_project_discount + discount.boq_special_project_discount
			if discount.get("discount_type") == "AMC":
				self.amc_total_discount += discount.boq_total_discount
			else:
				self.boq_total_discount += discount.boq_total_discount
		self.net_discount = self.boq_total_discount + self.amc_total_discount

	'''
		Calculate discount before margin
	'''
	def update_cost_and_discount(self):
		pass
		'''	
		if self.get("boq_total_discount"):
			self.total_cost  += flt(self.get("boq_total_discount"))
		if self.get("amc_total_discount"):
			self.amc_total_cost += flt(self.get("amc_total_discount"))
		'''

	'''
		Calculate Total AMC and Total Project
	'''
	def calculate_total_cost(self):
		
		self.update_cost_and_discount()
		# AMC Margin
		self.amc_margin_percent = 0.0
		self.amc_margin  = 0.0
		# BOQ Margin
		self.total_margin = 0.0
		
		self.margin_percent  = 0.0
		
		if self.is_amc and self.get("amc_total_sale_"):
			self.amc_margin = self.amc_total_sale_ - self.amc_total_cost
			if self.get("amc_margin"):
				self.amc_margin_percent = (flt(self.amc_margin)/ flt(self.amc_total_sale_))*100
		if self.boq and self.get("total_sale"):
			self.total_margin = self.total_sale - self.total_cost
			if self.get("total_margin"):
				self.margin_percent = (flt(self.total_margin)/ flt(self.total_sale))*100 if self.get("total_margin") else 0.0

		
	def calculate_grand_total(self):
		self.total_cost_amt = self.total_cost + self.amc_total_cost
		self.total_amt = self.total_sale + self.amc_total_sale_
		self.after_discount_sale_amount  = self.total_amt
		if self.get("net_discount"):
			self.after_discount_sale_amount = self.get("total_amt") - self.get("net_discount")
		self.grand_margin_total = self.after_discount_sale_amount - self.total_cost_amt
		self.amount_in_words = money_in_words(self.after_discount_sale_amount, self.currency)
		if not self.grand_margin_total:
			return 	
		self.grand_margin_percent = flt(self.grand_margin_total)/flt(self.total_amt)*100
			
	def on_submit(self):
		self.validate_boq()
		self.validate_amc()	

	'''
		Validate BOQ
	'''	
	def validate_boq(self):

		if self.get("boq"):
			if not self.get("total_sale"):
				self.raise_exception(_("Please update <b>Sales Price</b> for project"))
			if not self.get("total_margin"):
				self.raise_exception(_("Please update total margin for Project"))


	'''
		Validate AMC
	'''
	def validate_amc(self):
	
		if self.get("is_amc"):
			if not self.get("amc_total_sale_"):
				self.raise_exception(_("Please update <b>Sales Price</b> for AMC"))
			if not self.get("amc_yearly"):
				self.raise_exception(_("Please enter value in <b>AMC Yearly Item</b> table"))
			if len(self.get("amc_yearly")) != cint(self.get("maintenance_required_for")):
				self.raise_exception(_("Your AMC Yearly Item table should match the exact \
						number of <b>Maintenance Duration in years</b>"))
			if self.get("amc") and not self.get("amc_margin"):
				self.raise_exception(_("Please update total margin for AMC"))
		
	
	'''
		Add fraction value to 1
	'''	
	def add_fraction_value(self, item, field):
		
		if item.get(field):
			frac, whole = math.modf(item.get(field))
			if frac > 0:
				item.update({field: whole + 1})
	
	'''
		Get Extended Cost
	'''
	
	def get_extended_cost(self, amc_yearly_item):
	
		_temp = {}
		if not self.get("amc_extended_warranty"):
			return _temp
		gen = (item for item in self.get("amc_extended_warranty") if item.get("select_year") == amc_yearly_item.get("select_year"))
		try:
			_temp = gen.next()
		except Exception as e:
			print(frappe.get_traceback())
		return _temp

	'''
		Get Day UOM
	'''	
	def get_day_uom(self, items):
		
		temp = {}
		gen = (item for item in items if item.uom=="Days")
		try:
			temp = gen.next()
		except Exception as e:
			print(frappe.get_traceback())

		return temp	

	'''
		New Addition Varna
	'''
	def validate_payment_terms_total(self):
		total = 0.00
		for data in self.get('payment_term_table'):
			if not data.value:
				self.raise_exception(_("Please enter Percentage value in Payment terms"))

			val = data.value.replace("%", "")
			total += float(val)
		if total != 100.00:
			self.raise_exception("Payment Terms total not equal to 100%")
			

	def update_checklist(self):
		#msgprint("test")
		if self.get("update_checklist_manual"):
			frappe.msgprint("You can update checklist manually")
			return False
		condition, filters = self.get_condition()
		self.reset_checklist()
		update_checklist(self, condition, filters)




	def get_condition(self):
		
		condition = " "
		filters = frappe._dict()
		condition += " AND for_doctype = 'Boq'"
		if self.boq:
			condition += " AND for_project = %(is_boq)s "
			filters.update({"is_boq":self.boq})
		if self.is_amc:
			condition += "AND for_amc = %(is_amc)s "
			filters.update({"is_amc": self.is_amc})
		if self.is_proposal:
			filters.update({"proposal": self.is_proposal})
			condition += "AND proposal= %(proposal)s "
		if self.comprehensive:
			filters.update({"comprehensive": self.comprehensive})
			condition += "AND comprehensive= %(comprehensive)s "
		if self.non_comprehensive:
			filters.update({"non_comprehensive": self.non_comprehensive})
			condition += "AND non_comprehensive= %(non_comprehensive)s "

		return condition, filters	

	def get_user_message(self):
		
		msg  = ""
		space = " "
		msg += cstr(self.doc.get("our_scope")) + space + cstr(self.doc.get("project_site_name")) + \
				space + cstr(self.doc.get("solution")) + space + cstr(self.doc.get("boq_type"))
		msg += " {0} is assigned by <b>{1}</b>".format(self.doc.get("customer") or self.doc.get("customer_name"), self.doc.get("modified_by"))
		return msg
				
	def reset_checklist(self):
		parent = self.name
		to_remove = []
		for d in self.get("deliverables"):
			to_remove.append(d)
		for d in self.get("checklist_for_preventive_maintenance"):
			to_remove.append(d)
		for d in self.get("checklist_for_reactive_maintenance"):
			to_remove.append(d)
		[self.remove(d) for d in to_remove]
		
		
	def validate_proposal(self):
		
		if self.tablix_status  == "Manager Approval" and self.boq and not self.boq_type:
			self.raise_exception(_("Please enter BoQ Type !!!"))
		if self.tablix_status  == "Manager Approval" and self.is_amc and not self.amc_duration:
			self.raise_exception(_("Please enter AMC Duration !!!"))
		if self.tablix_status  == "Manager Approval" and self.is_amc and (not self.comprehensive and not self.non_comprehensive):
			self.raise_exception(_("Please enter AMC Type !!!"))
			
		if self.tablix_status  == "BDM Verified" and self.is_amc and not self.support_timings:
			self.raise_exception(_("Please enter Support timings !!!"))
		if self.tablix_status  == "BDM Verified" and self.is_amc and not self.type_of_support:
			self.raise_exception(_("Please enter Type of Support !!!"))
		if self.tablix_status  == "BDM Verified" and self.is_amc and not self.response_commitment:
			self.raise_exception(_("Please enter Response Commitment!!!"))
		if self.tablix_status  == "BDM Verified" and self.is_amc and not self.resolution_commitment:
			self.raise_exception(_("Please enter Resolution Commitment !!!"))
		if self.tablix_status  == "Manager Approval" and self.is_amc and not self.amc_yearly:
			self.raise_exception(_("Please enter AMC Items !!!"))
		if self.tablix_status  == "Manager Approval" and self.is_amc and not self.amc_preventive:
			if not self.get("is_preventive_maintenance"):
				return 
			self.raise_exception(_("Please enter AMC Preventive Items !!!"))
		if self.tablix_status  == "Manager Approval" and self.is_amc and not self.amc_reactive:
			if not self.get("is_reactive_maintenance"):
				return
			self.raise_exception(_("Please enter AMC Reactive Items !!!"))
		#if self.tablix_status  == "Designing" and self.is_amc and self.comprehensive and not self.amc_spare_parts:
		#	frappe.throw(_("Please enter AMC Spare Parts Items !!!"))
		if self.tablix_status  == "Manager Approval" and self.is_amc and not self.one_year_maintenance:
			self.raise_exception(_("Please enter No. of PPM required in One year !!!"))
		if self.tablix_status  == "Manager Approval" and self.is_amc and not self.no_of_calls:
			self.raise_exception(_("Please enter No. of calls required in One year for Reactive maintenance !!!"))
			
			
		if self.tablix_status  == "Manager Approval" and self.boq and not self.items:
			self.raise_exception(_("Please enter Item Details with Costing !!!"))
		if self.tablix_status  == "Manager Approval" and not self.our_scope:
			self.raise_exception(_("Please enter Proposal Name !!!"))
		if self.tablix_status  == "Manager Approval" and not self.solution:
			self.raise_exception(_("Please enter Solution Name !!!"))
			
		if self.tablix_status  == "BDM Verified" and self.boq and not self.boq_desired_margin:
			self.raise_exception(_("Please enter desired Margin for Boq !!!"))
		if self.tablix_status  == "BDM Verified" and self.is_amc and not self.amc_desired_margin:
			self.raise_exception(_("Please enter desired Margin for AMC !!!"))
		if self.tablix_status  == "BDM Verified" and not self.payment_term_table:
			self.raise_exception(_("Please enter Payment Terms !!!"))
			
		#if self.tablix_status  == "Boq Complete" and (not self.payment_days or self.payment_days <=0):
		#	frappe.throw(_("Please enter Payment Days !!!"))
		if self.tablix_status  == "Manager Approval" and self.boq and self.boq_type != "Supply" and (not self.proposed_project_completion_time or self.proposed_project_completion_time <= 0) :
			self.raise_exception(_("Please enter Estimated Project Implementation Time !!!"))
		if self.tablix_status  == "Manager Approval" and self.boq and (not self.mobilization_period or self.mobilization_period <= 0):
			self.raise_exception(_("Please enter Mobilization Period !!!"))
		if self.tablix_status  == "Manager Approval" and self.boq and (not self.maintenance_support_period or self.maintenance_support_period <=0) :
			self.raise_exception(_("Please enter Maintenance/Support Period !!!"))
		if self.tablix_status  == "BDM Verified"  and self.boq and (not self.validity_of_proposal or self.validity_of_proposal <=0):
			self.raise_exception(_("Please enter Validity of Proposal !!!"))
		if self.tablix_status  == "Manager Approval" and self.boq and (not self.dlp_period or self.dlp_period <=0):
			self.raise_exception(_("Please enter DLP Period !!!"))
			
		#if self.tablix_status == "Manager Approval" and self.is_proposal == 1 and self.compliance_statements == 0:
		#	frappe.throw(_("Please confirm that Compliance Statement docs are attached !!!"))
		if self.tablix_status == "Manager Approval" and self.boq == 1 and self.material_delivery_period <= 0:
			self.raise_exception(_("Please enter Material Delivery Period !!!"))
			
		if self.tablix_status  == "Manager Approval" and self.boq and self.is_proposal and not self.requirements_vs_solution_:
			self.raise_exception(_("Please enter REQ VS SOLUTION !!!"))
		if self.tablix_status  == "Manager Approval" and self.boq and self.is_proposal and not self.product_overview:
			self.raise_exception(_("Please enter PRODUCT OVERVIEW !!!"))
		if self.tablix_status  == "Manager Approval" and self.boq and self.is_proposal and not self.upload_site_image:
			self.raise_exception(_("Please Upload Site Image with Site name !!!"))
		if self.tablix_status  == "BDM Verified" and self.boq and self.is_proposal and not self.deliverables:
			self.raise_exception(_("Please enter Deliverable details!!!"))
		if self.tablix_status  == "BDM Verified" and self.boq and self.is_proposal and not self.system_overview:
			self.raise_exception(_("Please enter System Overview details!!!"))
		if self.tablix_status  == "Manager Approval" and not self.scope_of_work:
			self.raise_exception(_("Please enter Scope of Work !!!"))
		if self.tablix_status  == "Manager Approval" and not self.exclusions:
			self.raise_exception(_("Please enter Exclusions !!!"))
		
		
	

'''
	Convert BOQ to Sales Order
'''	
@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	boq = frappe.get_doc("Boq", source_name)
	frappe.db.set_value("Opportunity", boq.opportunity, "tablix_status", "Quotation")
	def set_missing_values(source, target):
		_doc = frappe.get_doct(target)
		_doc.ignore_pricing_rule = 1
		_doc.run_method("set_missing_values")
	
	doclist = get_mapped_doc("Boq", source_name, {
		"Boq": {
			"doctype": "Quotation",
			"field_map": {
				"name": "boq",
				"exclusions": "assumptions",
				"material_delivery_period": "delivery_terms",
				"validity_of_proposal": "validity",
				"net_discount": "discount_amount",
				"total_amt": "total",
				"total_cost_amt": "total_cost",
				"amc_type": "amc_type",
				"boq": "is_boq",
				"opportunity": "opportunity_quotation"
			}
		},
		"AMC Yearly Item": {
			"doctype": "Quotation Item",
			"field_map": {
				"name": "boq_detail",
				"amc_item_code": "item_code",
				"amc_item_name": "item_name",
				"amc_stock_uom": "stock_uom",
				"adm_amc_yearly_total": "rate",
				"amc_stock_uom": "uom",
				"amc_yearly_qty": "qty",
				"parent": "boq",
				"amc_item_group": "item_group",
				"amc_item_description": "description"
			},
		},
		"AMC Service Item":{
			"doctype": "Quotation Service Item"
		},
		"BOQ Discount Item": {
			"doctype": "Quotation Discount Item",
		},
		"Boq Item": {
			"doctype": "Quotation Item",
			"field_map": {
				"name": "boq_detail",
				"parent": "boq",
				"stock_uom": "stock_uom",
				"selling_price": "rate",
				"sale_amount": "total",
				"stock_uom" : "uom"
			}
		}
	})

	def update_amc_yearly_item(boq, doclist):
		if boq.get("is_amc"):
			doclist.amc_yearly_item = []
			for item in boq.get("amc_yearly"):
				_temp = item.as_dict()
				_c_doc = frappe.new_doc("Quotation AMC Yearly Item")
				for key, val in _temp.items():
					if key not in FIELD_MAP:
						_c_doc.set(key,val)
				doclist.amc_yearly_item.append(_c_doc)
	
	quotation_items = doclist.get("items")
	doclist.items = []
	for qt_item in quotation_items:
		rate = qt_item.get("rate")
		amount = qt_item.get("rate") * qt_item.get("qty")	
		qt_item.update({
			"rate": rate, "base_rate": rate,
			"price_list_rate": rate, "base_price_list_rate": rate,
			"amount": amount, "base_amount": amount,
		})
		doclist.items.append(qt_item)


	update_amc_yearly_item(boq, doclist)

	doclist.ignore_pricing_rule = 1
	return doclist

	
@frappe.whitelist()	
def marginapply(boq_form, app_margin_perc):
	boq = frappe.get_doc("Boq", boq_form)
	for item in boq.items:
		item.margin_percent = app_margin_perc
	return app_margin_perc
	

amc_item_code_map = frappe._dict({
	"First Year": {
			"amc_item_code": "AMC 1st year", 
			"amc_item_name": "Annual Maintenance Contract for 1st year",
			"amc_item_description": "Annual Maintenance Contract for 1st year",
			"amc_stock_uom": "Nos",
			"amc_item_group": "Annual Maintenance Contract",
			"amc_yearly_qty": 1
	},
	"Second Year": {
			"amc_item_code": "AMC 2nd year", 
			"amc_item_name": "Annual Maintenance Contract for 2nd year",
			"amc_item_description": "Annual Maintenance Contract for 2nd year",
			"amc_stock_uom": "Nos",
			"amc_item_group": "Annual Maintenance Contract",
			"amc_yearly_qty": 1
	},
	"Third Year": {
			"amc_item_code": "AMC 3rd year", 
			"amc_item_name": "Annual Maintenance Contract for 3rd year",
			"amc_item_description": "Annual Maintenance Contract for 3rd year",
			"amc_stock_uom": "Nos",
			"amc_item_group": "Annual Maintenance Contract",
			"amc_yearly_qty": 1
	},
	"Fourth Year": {
			"amc_item_code": "AMC 4th year", 
			"amc_item_name": "Annual Maintenance Contract for 4th year",
			"amc_item_description": "Annual Maintenance Contract for 4th year",
			"amc_stock_uom": "Nos",
			"amc_item_group": "Annual Maintenance Contract",
			"amc_yearly_qty": 1
	},
	"Fifth Year": {
			"amc_item_code": "AMC 5th year", 
			"amc_item_name": "Annual Maintenance Contract for 5th year",
			"amc_item_description": "Annual Maintenance Contract for 5th year",
			"amc_stock_uom": "Nos",
			"amc_item_group": "Annual Maintenance Contract",
			"amc_yearly_qty": 1
	},


})
