# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from tablix.notifications.notification_controller import NotificationController
from frappe import _, msgprint, throw

class ChangeRequestDocument(Document,NotificationController):
	
	def validate(self):
		self.update_current_value()
		self.send_notification();

	def update_current_value(self):
		
		doc =  frappe.get_doc(self.for_document, self.for_document_name)
		if not self.ref_field:
			frappe.throw(_("Please select <b>Reference Field Name</b>(Which you wish to change)"))

		self.current_value = doc.get(self.ref_field)

	def on_submit(self):
		try:
			temp = frappe.get_doc(self.for_document, self.for_document_name)
			if temp.meta.get("docstatus") == 2:
				frappe.throw(_("You can't change cancel document"))
			
			if temp.meta.get("is_submittable") == 0:
				frappe.throw(_("This Doctype is not Submittable. There is no need to Changes Request for this Doc."))

			if temp.meta.get("is_submittable") == 1 and temp.get("docstatus") == 1:
				#frappe.db.sql("""UPDATE {0} SET docstatus = 0 WHERE name = "{1}" """.format("`tab"+self.for_document+"`", self.for_document_name))
				#frappe.db.sql("""UPDATE `tab%(doctype)s` SET docstatus = 0 WHERE name = %(name)s """, {"name": self.for_document_name, "doctype": self.for_document})
				#field = self.ref_field
				#doc = frappe.get_doc(self.for_document, self.for_document_name)
				#if(field == "valid_till"):
				#	frappe.db.sql("""UPDATE {0} SET valid_till = {2} WHERE name = "{1}" """.format("`tab"+self.for_document+"`", self.for_document_name, self.revised_value))
				if(self.ref_field == "customer"):
					frappe.db.set_value(self.for_document, self.for_document_name, self.ref_field, self.revised_value)
					frappe.db.set_value(self.for_document, self.for_document_name, "customer", self.revised_value)
					frappe.db.set_value(self.for_document, self.for_document_name, "customer_name", self.revised_value)
				else:
					frappe.db.set_value(self.for_document, self.for_document_name, self.ref_field, self.revised_value)
				#else:
				#	doc.field = self.revised_value
				#doc.save()
				
				#frappe.db.sql("""UPDATE `tab%(doctype)s` SET docstatus = 1 WHERE name = %(name)s """, {"name": doc.get("name"), "doctype": self.for_document})
				#frappe.db.sql("""UPDATE {0} SET docstatus = 1 WHERE name = "{1}" """.format("`tab"+self.for_document+"`", self.for_document_name))
				frappe.db.commit()
		except Exception as e:
			frappe.db.rollback()
			frappe.msgprint(rappe.get_traceback())
