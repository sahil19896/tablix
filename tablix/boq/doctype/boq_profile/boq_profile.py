# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from .checklist import Checklist
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr
from frappe.model.document import Document
from tablix.notifications.notification_controller import NotificationController

class BOQProfile(Document, NotificationController):
	
	def validate(self):
		self._opp = frappe.get_doc("Opportunity", self.opportunity)
		self.validate_opportunity()

		self.validate_amc_info()
		self.validate_project_info()
		#self.validate_missing_information()
		self.update_system_type()

	def validate_opportunity(self):
		self.is_project = self._opp.is_project
		self.is_amc = self._opp.is_amc
		if not self.is_amc and not self.is_project:
			frappe.throw(_("Please select Is AMC or Is BOQ "))
		if self._opp.is_proposal or self._opp.is_amc:
			self.validate_images()


		if(self._opp.is_proposal or self._opp.is_amc):
			if self.is_amc:
				if not(self.support_timings or self.response_commitment or \
					self.type_of_support or self.resolution_commitment):
					frappe.throw(_("Please enter value in <b>Support Timing, Response Commitment, \
					Type of Support and Resolution Commitment </b>, It's required"))
				self.update_total_amc_months()

			if self.is_project:
				if not self.product_overview_items:
					frappe.throw(_("Please select Product Overview Items"))
				if not self.req_vs_solution_items:
					frappe.throw(_("Please select Req vs Solution Items"))
				if not self.inclusion:
					frappe.throw(_("Please enter Inclusion"))
				if not self.exclusion:
					frappe.throw(_("Please enter Exclusion"))
				if not self.deliverable_items:
					frappe.throw(_("Please enter <b>Deliverables</b>"))
				if not self.scope_of_work:
					frappe.throw(_("Please enter <b>Scope of Work</b> "))
				if not self.notes:
					frappe.throw(_("Please <b>Notes</b> "))
			

	def validate_amc_info(self):
		if not self.get("is_amc"):
			self.no_of_years_for_amc = None
			self.is_preventive = False
			self.is_reactive = False
			self.amc_type = None
			self.support_timings = None
			self.response_commitment = None
			self.type_of_support = None
			self.resolution_commitment = None
			self.amc_duration = None

		else:
			if (not self.is_preventive and not self.is_reactive):
				frappe.throw(_("Select <b>Is Preventive</b> OR <b>Is Reactive</b>"))	
			if(not self.amc_type):
				frappe.throw(_("Please select <b>AMC Type</b>."))
	def validate_images(self):
		if self.is_new()  == 1:
			return False
		if not self.company_image or not self.site_image or not self.company_logo:
			frappe.throw(_("""Please attach <b>Company Image, Company Logo and Site Image</b>.
					It's only required if BOQ is Proposal/Tender or AMC."""))


	
	def validate_project_info(self):
		if not self.get("is_project"):
			self.proposed_project_starting_time = None
			self.material_delivery_period = None
			self.proposed_project_completion_time = None
			self.mobilization_period = None
			self.validity_of_proposal = None
			self.maintenance_support_period = None
			self.dlp_period = None	
		else:
			if not self.project_type:
				frappe.throw(_("Please select <b>Project Type</b>."))
			if not self.project_site_name:
				frappe.throw(_("Please select <b>Project Site Name</b>."))
		
		self.update_project_time()	

	def update_project_time(self):
		self.proposed_project_completion_time = cint(self.project_implementation_time)+ \
							cint(self.material_delivery_period)
	
	def validate_missing_information(self):
		if not self._opp.is_proposal:
			return False
		for system in self.system_items:
			_temp = frappe.get_doc("Solution System Type", system.get("system_type"))
			system_type = system.get("system_type")
			if self.is_preventive:
				if not _temp.preventive_checklist_items:
					frappe.throw(_("Please update <b>Preventive Checklist</b> in {0}.".format(system_type)))
			if self.is_reactive:
				if not _temp.reactive_checklist_items:
					frappe.throw(_("Please update <b>Reactive Checklist</b> in {0} ".format(system_type)))

			if self.is_project:
				if not system.system_overview:
					frappe.throw(_("Please update <b>System Overview</b> in {0}.".format(system_type)))		
							
	def validate_amc_timings(self):
		if not self.project_implementation_time:
			frappe.throw(_("Please enter <b>Project Implementation Time</b>."))
		if not self.material_delivery_period:
			frappe.throw(_("Please enter <b>Material Delivery Period</b> ."))
		if not self.mobilization_period:
			frappe.throw(_("Please enter <b>Mobilization Period</b>. "))

	def update_system_type(self):
		self.system_type = ""
		temp = []
		for system in self.get("system_items"):
			if not system.get("parent_solution_system_type"):
				frappe.throw(_("Please select <b>Parent Solution System Type</b> in system \
					{0}.".format(system.get("system_type"))))
			d  = frappe.get_doc("Solution System Type", system.get("parent_solution_system_type"))
			if not d.get("abbreviation_of_system"):
				frappe.throw(_("Please enter Abbreviation of system {0} in row {1} \
					".format(d.get("system_type"), system.get("idx"))))
			if temp.count(d.get("abbreviation_of_system")) == 0:
				temp.append(d.get("abbreviation_of_system"))
		
		self.system_type = ", ".join(temp)
	
	def update_total_amc_months(self):	
		if not self.amc_duration_years and not self.amc_duration_months:
			frappe.throw(_("Please select either <b>Months or Years</b> for AMC."))
		else:
			months = 0
			if self.amc_duration_years:
				months += 12*cint(self.amc_duration_years)
			if self.amc_duration_months:
				months +=  cint(self.amc_duration_months)
			self.total_amc_months = months
