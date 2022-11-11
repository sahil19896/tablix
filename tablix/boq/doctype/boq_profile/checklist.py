# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Checklist(Document):
	
	def update_checklist(self):
		if not self._opp.is_proposal:
			return 
	
		self._update_table_fields()
		self._update_checklist_data()

		
	def _update_table_fields(self):
		self.checklist_table_field = ['BOQ Profile Preventive Maintenance Checklist Item',
						'BOQ Profile Reactive Maintenance Checklist Item',
						'BOQ Profile Terms Checklist Item']
		self._table_fields = {}
		self._table_fields_doctype = []		
		for field in self.meta.get_table_fields():
			if field.options in self.checklist_table_field:
				self._table_fields[field.options] = field.fieldname
				self._table_fields_doctype.append(field.options)
		

	def _update_checklist_data(self):
	
		filters = {
			"is_amc": self.is_amc, "is_project": self.is_project,
			"is_preventive": self.is_preventive, "is_reactive": self.is_reactive,
			"enabled": 1, 
		}
		filters, condition = self._get_filters_condition()
		self.reset_checklist()	
		res = frappe.db.sql("""SELECT topic, `check` AS is_check, for_doctype, topic_fieldname, index_of_topic FROM \
				`tabBOQ Profile Checklist` WHERE enabled=1 %s ORDER BY \
				index_of_topic ASC """%(condition), filters, as_dict=True)
		for cl in res:
			field = self._table_fields[cl.get("for_doctype")]
			print(field)
			print(cl.get("is_check"))
			self.append(field, {"check": cl.get("is_check"), cl.get("topic_fieldname"): cl.get("topic")})

	def _get_filters_condition(self):
		filters = {}
		condition = " AND for_doctype IN %(for_doctype)s "
		if self.get("is_amc"):
			condition += " AND for_amc=%(for_amc)s "		
		if self.get("is_project"):
			condition  += " AND for_project=%(for_project)s "
		if self.get("is_preventive"):
			condition += " AND is_preventive=%(is_preventive)s "
		if self.get("is_reactive"):
			condition += " AND is_reactive=%(is_reactive)s "
	
		filters.update({"for_amc": self.is_amc, "for_project": self.is_project,
			"is_reactive": self.is_reactive, "is_preventive": self.is_preventive,
			"enabled": 1, "for_doctype": tuple(self._table_fields_doctype)})
		return filters, condition

	def reset_checklist(self):
		for doctype, fieldname  in self._table_fields.items():
			self.set(fieldname, [])
