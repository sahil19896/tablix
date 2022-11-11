# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from tablix.cpm.cpm_controller import CPMController

class Indicator(CPMController):
	

	def autoname(self):
		self.name = "{0}.{1}".format(self.strategic_objective, self.get_next_number())


	def validate(self):
		self.validate_values()


	def validate_values(self):

		if(not(self.base_value or self.base_percentage or self.base_data)):
			frappe.throw(_("Required Base Value/Percentage/Data"))
		
		if(not(self.target_value or self.target_percentage or self.target_data)):
			frappe.throw(_("Required Target Value/Percentage/Data"))
		
		if(not(self.actual_value or self.actual_percentage or self.actual_data)):
			frappe.throw(_("Required  Actual Value/Percentage/Data"))
	
	
