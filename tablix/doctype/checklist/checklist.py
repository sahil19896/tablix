# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, cstr
from frappe import _,  msgprint, throw

class Checklist(Document):
	
	def validate(self):
		self.update_checklist()


	def update_checklist(self):
		if not self.items:
			throw(_("Please enter items. "))	
