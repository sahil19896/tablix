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
			temp = frappe.get_doc(self.for_document, self.for_document_name).as_dict().copy()
			if temp.get("docstatus") == 2:
				throw(_("You can't change cancel document"))

			if temp.get("meta").get("is_submittable") and temp.get("docstatus") ==1:
				frappe.db.sql("""UPDATE `tab{doctype}` SET docstatus=0 WHERE name=%(name)s """.format(doctype=self.for_document), 
					{"name": self.for_document_name, "doctype": self.for_document})
			
			doc = frappe.get_doc(self.for_document, self.for_document_name)
			doc.set(self.ref_field, self.revised_value)
			doc.save()
			if temp.get("meta").get("is_submittable") and temp.get("docstatus") ==1:
				frappe.db.sql("""UPDATE `tab{doctype}` SET docstatus=1 WHERE name=%(name)s """.format(doctype=self.for_document), 
					{"name": doc.get("name"), "doctype": self.for_document})
			frappe.db.commit()
		except Exception as e:
			frappe.db.rollback()
			frappe.msgprint(e)
			frappe.msgprint(_("Error while changing status, Error: {0}".format(e.message)))
				
	
						
						
