# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CompanyProfile(Document):
	
	def validate(self):
		self.validate_solutions_system_items()

	def validate_solutions_system_items(self):
			
		if not self.solutions_items:
			for item in frappe.db.get_values("Solution System Type", {"enabled": 1}, 
					["system_type", "description"], order_by=" system_type ASC", as_dict=True):
				temp = frappe._dict({
						"system_type": item.get("system_type"), 
						"description": item.get("description")
				})
				self.append("solutions_items", temp)
	
