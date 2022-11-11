# -*- coding: utf-8 -*-
# Copyright (c) 2019, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from tablix.notifications.notification_controller import NotificationController
from frappe import _, msgprint
import datetime

class Notification(Document, NotificationController):
	def validate(self):
		from tablix.notifications.notifications import notify_employee
		self.send_notification()
		if(self.doc.get("tablix_status") == "Approval Request"):
			if(self.doc.get("approver")):
				self.tablix_status = "Waiting For Approval"
				users = self.doc.get("approver")
				self.send_approval(users)
		
		if(self.doc.get("tablix_status") == "Completed"):
			emails = []
			emails.append(self.doc.request_by)
			self.make_todo(emails)
			notify_employee(self.doc, emails, reason="")

		if(self.doc.get("tablix_status") == "Open"):
			emails = []
			emails.append(self.doc.request_by)
			if(self.doc.get("approver")):
				count = 0
				for usr in self.doc.get("approver"):
					if(usr.get("accept") > 0 or usr.get("decline") > 0):
						count += 1

				if(count == len(self.doc.get("approver"))):
					self.make_todo(emails)
					notify_employee(self.doc, emails, reason="")

		if(self.doc.get("tablix_status") == "Waiting For User's Approval"):
			from tablix.notifications.notifications import notify_employee
			if(self.doc.get("employee")):
				emails = []
				self.tablix_status = "Approved"
				self.approved_date = frappe.utils.nowdate()
				users = self.doc.get("employee")
				for usr in users:
					emails.append(usr.get("email"))
				if(emails):
					self.make_todo(emails)
					notify_employee(self.doc, emails, reason="")

	def send_approval(self, users):
		from tablix.notifications.notifications import notify_employee
		emails = []
		for usr in users:
			if((usr.get("accept") == 0)):
				emails.append(usr.get("email"))
		if(emails):
			self.make_todo(emails)
			notify_employee(self.doc, emails, reason="")

	
	def make_todo(self, emails):
		for e in emails:
			doc = frappe.new_doc("ToDo")
			doc.date = self.doc.get("date")
			doc.reference_type = "Notification"
			doc.owner = e
			doc.reference_name = self.doc.get("name")
			doc.assigned_by = self.doc.get("request_by")
			doc.description = self.doc.get("subject")+"-"+self.doc.get("name")+" has been assigned to you by "+self.doc.get("request_by")
			try:
				doc.save(ignore_permissions=True)
			except Exception as e:
				frappe.msgprint(_("Something went wrong. Contact your System Admin."))
