'''
	CRM Controller For Opportunity and Lead
'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr, now_datetime
from tablix.controllers.selling_controller import SellingController

class CRMController(SellingController):
	
	def validate_crm(self):
		if self.dt in ['Lead', 'Opportunity']:
			self.validate_project_or_amc()


	def validate_project_or_amc(self):
		
		if (self.dt != "Lead" and not(self.doc.is_project or self.doc.is_amc)):
			frappe.throw(_("Please check either <b>Is Project</b> OR  <b>Is AMC</b>."))
			
		if(self.doc.account_manager):
			temp = frappe.db.get_value("Account Manager", self.doc.account_manager, "full_name", as_dict=True)
			self.doc.account_manager_name = temp.get("full_name")
		if(self.doc.bdm):
			temp = frappe.db.get_value("BDM", self.doc.bdm, "full_name", as_dict=True)
			self.doc.bdm_name  = temp.get("full_name")

		self.send_notification()
