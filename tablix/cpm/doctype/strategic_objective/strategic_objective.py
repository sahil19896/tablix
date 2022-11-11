# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from tablix.cpm.cpm_controller import CPMController
from frappe import _, msgprint, throw

class StrategicObjective(CPMController):
	
	def autoname(self):
		num = self.get_next_number()
		self.name = "{0}.{1}".format(self.strategic_theme, num)


	def validate(self):
		self.validate_objectives()


	def validate_objectives(self):
		
		if not self.select_series:
			frappe.throw(_("Select Series"))

			
		
 	
