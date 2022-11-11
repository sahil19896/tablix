# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, throw, _


class SolutionSystemType(Document):

	def validate(self):
		self.validate_is_group()
	
	def validate_is_group(self):
		pass	
	def on_trash(self):
		if self.name == "ELV":
			frappe.throw(_("You can't delete <b>Root Group</b>. "))
			
