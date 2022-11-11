# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from tablix.cpm.cpm_controller import CPMController

class Objective(CPMController):

	def validate(self):
		self.select_series = self.naming_series[0]

	def validate(self):
		if not self.is_parent and not self.parent_objective:
			frappe.throw(_("Enter Parent Objective or Mark the Is Parent field"))

			
