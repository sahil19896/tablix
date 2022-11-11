# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from tablix.cpm.cpm_controller import CPMController
from tablix.cpm.utils import get_number

class StrategicTheme(CPMController):

	def autoname(self):
		num = 1
		last_num = frappe.db.sql(""" SELECT name FROM `tabStrategic Theme` WHERE 
			select_series=%(series)s ORDER BY creation DESC LIMIT 1 """,\
			{"series": self.select_series}, as_dict=True)
		if last_num:
			num = get_number(last_num[0].get("name"))+1	
		
		self.name = "{0}{1}".format(self.select_series, num)
	
	def validate(self):
		
		if(self.get("perspective") ==  "Finance"):
			self.priority = 1
		if(self.get("perspective") ==  "Customers"):
			self.priority = 2
		if(self.get("perspective") ==  "Internal Processes"):
			self.priority = 3
		if(self.get("perspective") ==  "Learning & Growth"):
			self.priority = 4
		
				

