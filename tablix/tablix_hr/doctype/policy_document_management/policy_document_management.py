# -*- coding: utf-8 -*-
# Copyright (c) 2019, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from tablix.notifications.notification_controller import NotificationController
from frappe import _, msgprint
import datetime

class PolicyDocumentManagement(Document, NotificationController):

	def validate(self):
		from tablix.notifications.notifications import notify_employee
		self.send_notification()
		if(self.doc.get("tablix_status") == "Approval Request"):
			if(self.doc.get("policy_approver")):
				self.tablix_status = "Waiting For Approval"
				users = self.doc.get("policy_approver")
				self.send_approval(users)
		
		if(self.doc.get("tablix_status") == "Completed"):
			emails = []
			emails.append(self.doc.policy_request_by)
			self.make_todo(emails)
			notify_employee(self.doc, emails, reason="")

		if(self.doc.get("tablix_status") == "Open"):
			emails = []
			emails.append(self.doc.policy_request_by)
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
			if(self.doc.get("policy_employee")):
				emails = []
				self.tablix_status = "Approved"
				self.approved_date = frappe.utils.nowdate()
				users = self.doc.get("policy_employee")
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
			doc.reference_type = "Policy Document Management"
			doc.owner = e
			doc.reference_name = self.doc.get("name")
			doc.assigned_by = self.doc.get("policy_request_by")
			doc.description = self.doc.get("document_name")+"-"+self.doc.get("name")+" has been assigned to you by "+self.doc.get("policy_request_by")
			try:
				doc.save(ignore_permissions=True)
			except Exception as e:
				frappe.msgprint(_("Something went wrong. Contact your System Admin."))


#----Fetch Employee----#
 
@frappe.whitelist()
def get_employee_data(department):
	if(department != "ALL"):
		return frappe.db.sql(""" select name, employee_name, user_id, signature from `tabEmployee` where department = %s and status = "Active" and user_id != ""  """,department, as_dict=1)

	else:
		return frappe.db.sql(""" select name, employee_name, user_id, signature from `tabEmployee` where status = "Active" and user_id != ""  """, as_dict=1)

@frappe.whitelist()
def get_company_employee(department):
	if(department == "Tablix Technology LLC"):
		return frappe.db.sql(""" select name, employee_name, user_id, signature from `tabEmployee` where status = "Active" and user_id != "" and company = %s """,department, as_dict=1)
	
	elif(department != "Tablix Technology LLC"):
		return frappe.db.sql(""" select name, employee_name, user_id, signature from `tabEmployee` where status = "Active" and user_id != "" and company = %s """,department, as_dict=1)

#----Approver notification----#

@frappe.whitelist()
def approver_notify():
	policy = frappe.db.sql("""select tp.name, tp.tablix_status, tp.date, tp.approval_date, pa.email, 
			pa.accept, pa.decline, tp.document_name 
			from `tabPolicy Document Management` tp inner join `tabPolicy Approvers` pa on tp.name = pa.parent 
			where tp.tablix_status = "Waiting For Approval"  """, as_dict=True)

	if(policy):
		for p in policy:
			if(p.approval_date == datetime.datetime.now().date() and p.accept == 0 and p.decline == 0):
				msg = "Policy Document Management: "+ p.name + " has been assigned to you. No action for Approve or Decline yet taken. Please complete the Task <b>Immediately</b>"

				frappe.sendmail(recipients=[p.email], subject=p.document_name, message=msg, delayed=False)
	else:
		print("Done!!!")


@frappe.whitelist()
def final_approver_notify():
	policy = frappe.db.sql("""select tp.name, tp.tablix_status, tp.date, tp.approval_date, 
			pa.email, pa.accept, pa.decline, tp.document_name 
			from `tabPolicy Document Management` tp inner join `tabPolicy Approvers` pa on tp.name = pa.parent
			where tp.tablix_status = "Waiting For Approval"  """, as_dict=True)

	if(policy):
		for p in policy:
			if(datetime.datetime.now().date() > p.approval_date and p.accept == 0 and p.decline == 0):
				msg = "Policy Document Management: "+ p.name + " has been assigned to you. No action for Approve or Decline yet taken. Please complete the Task <b>Immediately</b> as this is pending in queue for long. If task not completed immediately, escalation notification will be sent to <b>CEO</b>"

				frappe.sendmail(recipients=[p.email], cc=['gopu@tablix.ae'], subject=p.document_name, message=msg, delayed=False)
	else:
		print("DONE!!!")


#----Employee Notification----#

@frappe.whitelist()
def employee_notify():
	employee = frappe.db.sql("""select tp.name, tp.approved_date, pe.email, pe.accepted, tp.document_name
			from `tabPolicy Document Management` tp inner join `tabPolicy Employee` pe on tp.name = pe.parent
			where tp.tablix_status = "Approved" """, as_dict=True)

	if(employee):
		for e in employee:
			if(e.approved_date == datetime.datetime.now().date() and e.accepted == 0):
				msg = "Policy Document Management: "+ e.name + " has been assigned to you. No action for review or accept yet taken. Please complete the Task <b>Immediately</b>"
				frappe.sendmail(recipients=[e.email], cc=['prathyoosh.b@tablix.ae'], subject=e.document_name, message=msg, delayed=False)
	else:
		print("DONE!!!")


@frappe.whitelist()
def final_employee_notify():
	employee = frappe.db.sql("""select tp.name, tp.approved_date, pe.email, pe.accepted, tp.document_name
			from `tabPolicy Document Management` tp inner join `tabPolicy Employee` pe on tp.name = pe.parent
			where tp.tablix_status = "Approved" """, as_dict=True)

	if(employee):
		for e in employee:
			if(datetime.datetime.now().date() > e.approved_date and e.accepted == 0):
				msg = "Policy Document Management: "+p.name + " has been assigned to you. No action for review yet taken. Please complete the Task <b>Immediately</b> as this is pending in queue for long. If task not completed immediately, escalation notification will be sent to <b>CEO</b>"
				frappe.sendmail(recipients=[e.email], cc=['prathyoosh.b@tablix.ae', "gopu@tablix.ae"], subject=e.document_name, message=msg, delayed=False)

	else:
		print("DONE!!!")


#----Re-assign Doc----#

@frappe.whitelist()
def reassign_policy():
	policy = frappe.db.sql("""select name, date, notification 
			from `tabPolicy Document Management` where tablix_status = "Approved" and notification != "" """, as_dict=True)
	
	if(policy):
		for p in  policy:
			if(p.notification == "Weekly"):
				now = p.date
				week = datetime.timedelta(days=7)
				weekly = now + week

				if(weekly == datetime.datetime.now().date()):
					set_status_notify(p.name)
			elif(p.notification == "Monthly"):
				now = p.date
				month = datetime.timedelta(days=30)
				monthly = now + month

				if(monthly == datetime.datetime.now().date()):
					set_status_notify(p.name)
			elif(p.notification == "Quarterly"):
				now = p.date
				quarter = datetime.timedelta(days=90)
				quarterly = now + quarter

				if(quarterly == datetime.datetime.now().date()):
					set_status_notify(p.name)
	else:
		print("Done!!!")


def set_status_notify(name):
	from tablix.notifications.notifications import notify_employee
	doc = frappe.get_doc("Policy Document Management", name)
	if(doc):
		child = doc.get("policy_employee")
		emails = []
		if(child):
			for c in child:
				c.accepted = 0
				emails.append(c.email)

			doc.save(ignore_permissions=True)
			if(emails):
				make_todo(doc, emails)
				notify_employee(doc, emails, reason="")


def make_todo(policy, emails):
	for e in emails:
		doc = frappe.new_doc("ToDo")
		doc.date = policy.date
		doc.reference_type = "Policy Document Management"
		doc.owner = e
		doc.reference_name = policy.name
		doc.assigned_by = policy.policy_request_by
		doc.description = policy.document_name+"-"+policy.name+" has been assigned to you by "+policy.policy_request_by
		try:
			doc.save(ignore_permissions=True)
		except Exception as e:
			print(e)


@frappe.whitelist()
def send_reason(msg, user, doc):
	email = ["gopu@tablix.ae", "kartik@tablix.ae", "bala@tablix.ae", "rajesh.k@tablix.ae"]
	final_list = []
	for e in email:
		if(e != user):
			final_list.append(e)

	try:
		notify = "The Document "+ doc+ " has been declined by "+user+" with reason "+msg
		frappe.sendmail(recipients=final_list, subject="Declined", message=notify, delayed=False)
		return "Done!"
	except Exception as e:
		return e
