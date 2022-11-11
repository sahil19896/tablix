# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BDM(Document):
	
	def validate(self):
		if frappe.db.get_value("Employee", {"user_id": self.bdm}):
			self.update_account_manager_detail()


	def update_account_manager_detail(self):
		
		detail = frappe.db.get_value("Employee", {"user_id": self.bdm}, 
				fieldname=["name", "employee_name"], as_dict=True)
		self.employee_id = detail.get("name")
		self.full_name = detail.get("employee_name")

		
