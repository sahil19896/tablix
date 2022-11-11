# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EmployeeTarget(Document):
	
	def autoname(self):
		
		self.name = "{0}-{1}-{2}".format(self.fiscal_year, self.target_for, self.user_id)


	def validate(self):
		pass

	def update_weekly_data(self):
		pass


	def update_monthly_data(self):
		pass

	def update_quarterly_data(self):
		pass	
