'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe.utils import cint, flt, money_in_words
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt
from tablix.utils.checklist import update_checklist
from tablix.controllers import stock_controller
import sys
from tablix.controllers import margin_updater

'''
	Basic Controller for all sales module
'''

class SellingController(stock_controller.StockController):

	def validate_selling(self):
		super(SellingController, self).validate()
		if self.dt not in ["Sales Order", "Quotation"]:
			return False

		if(self.doc.get("boq_profile")):
			margin_updater.MarginUpdater(self.doc, self.dt).validate_margin()
		self.update_taxes_and_charges()

		if self.dt in ["Sales Order"]:
			self.validate_discount()
		if self.dt in ["Quotation"]:
			if(self.doc.get("boq_profile")):
				self.update_checklist_items()
		self.update_docstatus()
	

	def validate_selling_cancel(self):
		super(SellingController, self).validate_cancel()
		if self.dt == "Sales Order":
			self.unlink_project()

	def validate_selling_submit(self):
		super(SellingController, self).validate_submit()
		if self.dt=="Sales Order":
			self.assign_so()
			self.link_project()

	def assign_so(self):
		from tablix.notifications.notifications import notify_employee
		if(self.doc.get("area_head")):
			emails = []
			for head in self.doc.get("area_head"):
				emails.append(head.get("area_head"))
			if(emails):
				self.make_todo(emails)
				notify_employee(self.doc, emails, reason="")

	def make_todo(self, emails):
		if(emails):
			for e in emails:
				doc = frappe.new_doc("ToDo")
				doc.date = self.doc.get("transaction_date")
				doc.reference_type = "Sales Order"
				doc.owner = e
				doc.reference_name = self.doc.get("name")
				doc.assigned_by = frappe.session.user
				doc.description = self.doc.get("title")+"-"+self.doc.get("name")+" has been assigned to you by "+frappe.session.user
				try:
					doc.save(ignore_permissions=True)
				except Exception as e:
					frappe.msgprint(_("Something went wrong. Contact your System Admin."))

	def link_project(self):
		if(self.doc.project):
			return False
		quotation = None
		for item in self.doc.get("items"):
			quotation = item.get("prevdoc_docname")
			break
		
		name = "{customer}-{qt}-{so}".format(customer=self.doc.get("customer"), \
			 qt=quotation, so=self.doc.get("name"))
		
		if(cint(self.doc.get("docstatus")) == 1):
			if frappe.db.get_value("Project", {"name": name}):
				self.doc.project = name

			doc = frappe.get_doc({
					"doctype": "Project", "project_name": name,
					"expected_start_date": self.doc.get("transaction_date"),
					"sales_order": self.doc.get("name"),
			})	
			doc.save(ignore_permissions=True)
			self.doc.project = doc.name

	def unlink_project(self):
		if not self.doc.get("project"):
			return
		if(cint(self.doc.get("docstatus")) == 2):
			doc = frappe.get_doc("Project", self.doc.get("project"))
			doc.delete()
		self.doc.project  = ""

	def validate_discount(self):
		pass

	def update_checklist_items(self):

		boq_profile = frappe.get_doc("BOQ Profile", self.doc.get("boq_profile")).as_dict()
		opp =  frappe.db.get_value("Opportunity", {"name": boq_profile.get("opportunity")}, \
				fieldname=["is_proposal", "is_amc"], as_dict=True)
		if opp.get("is_proposal") or opp.get("is_amc") or boq_profile.is_project:
			if(boq_profile.get("is_project") and not  self.doc.get("select_index")):
				frappe.throw(_("Please select BOQ Technical Index"))
			if(boq_profile.get("is_project") and not  self.doc.get("select_boq_commercial_index")):
				frappe.throw(_("Please select BOQ Commercial Index"))
			if(boq_profile.get("is_amc") and not  self.doc.get("select_amc_technical_index")):
				frappe.throw(_("Please select AMC Technical Index"))
			if(boq_profile.get("is_amc") and not  self.doc.get("select_amc_commercial_index")):
				frappe.throw(_("Please select AMC Commercial Index"))
		else:
			#  IF BOQ IS NOT PROPOSAL RESET THE CHECKLIST TO DEFAULT CHECKLIST
			self.doc.select_index = ""
			self.doc.select_boq_commercial_index = ""
			self.doc.select_amc_commercial_index = ""
			self.doc.select_amc_technical_index = ""
			self.doc.quotation_index_items =[]
			self.doc.boq_technical_index_items = []
			self.doc.amc_technical_index_items = []
			self.doc.amc_commercial_index_items = []
			return False # RETURN NOT NEED TO UPDATE THE CHECKLIST

		_doc = self.doc.as_dict()
		_doc.update({"opportunity": boq_profile.opportunity, "solution_type": boq_profile.get("solution_type")})
		# UPDATE BOQ TECHNICAL PROPOSAL INDEX
		if not self.doc.get("quotation_index_items"):
			if self.doc.get("select_index"):
				checklist = frappe.get_doc("Checklist", self.doc.get("select_index"))
				self.update_checklist(checklist, _doc, boq_profile,  "quotation_index_items")
		# UPDATE BOQ COMMERCIAL PROPOSAL INDEX
		if not self.doc.get("boq_commercial_index_items"):
			if self.doc.get("select_boq_commercial_index"):
				checklist = frappe.get_doc("Checklist", self.doc.get("select_boq_commercial_index"))
				self.update_checklist(checklist, _doc, boq_profile, "boq_commercial_index_items")
		# UPDATE AMC COMMERCIAL PROPOSAL INDEX
		if not self.doc.get("amc_technical_index_items"):
			if self.doc.get("select_amc_technical_index"):
				checklist = frappe.get_doc("Checklist", self.doc.get("select_amc_technical_index"))
				self.update_checklist(checklist, _doc, boq_profile, "amc_technical_index_items")
		# UPDATE AMC TECHNICAL PROPOSAL INDEX
		if not self.doc.get("amc_commercial_index_items"):
			if self.doc.get("select_amc_commercial_index"):
				checklist = frappe.get_doc("Checklist", self.doc.get("select_amc_commercial_index"))
				self.update_checklist(checklist, _doc, boq_profile, "amc_commercial_index_items")

	def update_checklist(self, checklist, _doc, boq_profile,  fieldname):
		self.doc.set(fieldname, [])
		for item in checklist.get("items"):
			temp = frappe._dict({
					"class_name":item.get("class_name"),"topic_name": item.get("topic_name"), 
					"page_number":item.get("page_number"), "contents": item.get("contents"),
					
			})
				
			temp.topic_name = frappe.render_template(temp.topic_name, {"doc":_doc,"boq_profile": boq_profile})
			temp.contents  = temp.contents.format(**temp)
			self.doc.append(fieldname, temp)
		
		

	def update_docstatus(self):
		if self.dt in ['Sales Order', 'Quotation'] and self.doc.get("opportunity"):
			status  = "Quotation" if self.dt == "Quotation" else "Converted"
			doc = frappe.get_doc("Opportunity", self.doc.get("opportunity"))
			doc.tablix_status = status
			doc.status = status
			doc.save(ignore_permissions=True)
					
						
			
