# -*- coding: utf-8 -*-
# Copyright (c) 2017, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw
from datetime import timedelta
from frappe.utils import cint, flt, cstr, now_datetime
import json
import datetime


class EscalationNotification(Document):
	
	def validate(self):
		self.validate_doctype()
		self.validate_escalation_users()
		self.validate_datetime_filter()
		self.validate_repeat()

	def  validate_doctype(self):
	
		if not self.based_on:
			throw(_("Please select <b> Based On ></b>"))

	def validate_escalation_users(self):
	
		for user in self.get("users"):
			if user.get("enable_condition") and not (user.get("docfield") and user.get("docfield_value")):
				user.docfield = ""
				user.docfield_value = ""
				self.enable_condition = 0
				msg = _("Please don't leave <b>DocField</b> and <b>DocField Value</b> of row {0} Or Uncheck Condition Option")
				msgprint(msg.format(user.get("idx")))	

	def validate_datetime_filter(self):
		if self.get("enable_datetime_filter"):
			if not (self.get("datetime_field") and self.get("notification_time_condition") \
				and self.get("notification_after") and self.get("notification_time")):	
				throw(_("Please select <b>Datetime Field, Notification After, Notification After Condition</b> \
						and <b>Notification Time</b> Or Uncheck Enable Datetime Filter"))

	def validate_repeat(self):
	
		if self.get("repeat"):
			if not self.get("repeat_after"):
				throw(_("Please select the <b>Repeat After</b> interval"))


'''
	Scheduler Task for Escalation Notification
'''
def _send_notification():
	for item in frappe.get_all("Escalation Notification", {"enabled": 1}):
		doc = frappe.get_doc("Escalation Notification", item.get("name"))
		send_notification(doc)

@frappe.whitelist()
def get_field_list(doctype):
	return frappe.get_doc("DocType", doctype).fields	


class EscalationNotificationAlert:
	
	def __init__(self):
		self.escalation = None
		self.todo_fields = ['modified', 'status', 'owner', 'assigned_by', 'reference_type',
	 			'reference_name', 'assigned_by_full_name', 'description', 'creation']
		
	def get_filters(self, escalation_doc):
		filters = frappe._dict()
		if escalation_doc.get("based_on") == "ToDo":
			if escalation_doc.get("docfield"):
				filters.update({escalation.get("docfield"): escalation.get("docfield_value")})
			if escalation_doc.get("for_doctype"):
				filters.update({"reference_type": escalation.get("for_doctype")})
		else:
			if escalation_doc.get("docfield") and escalation_doc.get("docfield_value"):
				filters.update({escalation.get("docfield"): escalation.get("docfield_value")})

		return filters

	def init_escalation_process(self):
		
		for item in frappe.get_list("Escalation Notification", {"enabled": True}):
			escalation_doc = frappe.get_doc("Escalation Notification", item.get("name"))
			filters = self.get_filters(escalation_doc)
			if escalation.get("based_on") == "ToDo":
				self.send_todo_notification(escalation_doc, filters)
			else:
				self.send_doctype_notification(escalation_doc, filters)

	
	
	def send_todo_notification(self, escalation_doc, filters):
		todo_list = frappe.get_all("ToDo", fields=TODO, filters=filters)
		for todo in todo_list:
			log = self.get_logs(todo.get("reference_type"), todo.get("reference_name"))
			ref_doc = frappe.get_doc(todo.get("reference_type"), todo.get("reference_name"))
			self.send_email(ref_doc, todo, escalation, log)

	def send_doctype_notification(self, escalation_doc, filters):

		for item in frappe.get_all(escalation.get("for_doctype"), fields="*", filters=filters):
			log = self.get_logs(escalation.get("for_doctype"), item.get("name"))
			self.send_email(item, None, escalation, log)

	def get_logs(self, document_type, document_name):
		log = frappe.db.sql(""" SELECT name, creation, modified FROM `tabEscalation Logs` WHERE \
			document_name=%(name)s AND document_type=%(doctype)s  ORDER BY modified DESC LIMIT \
			1 """, {"name": document_name,"doctype": document_type},as_dict=True)
		if log:
			log = log[0]
		else:
			log = None
		return log
		
	def send_email(self, escalation_doc, doc, todo, log):
		value = None		
		if todo:
			value = todo.get(escalation_doc.get("datetime_field"))
		else:
			value = doc.get(escalation_doc.get("datetime_field"))
		if escalation_doc.get("enable_datetime_filter") and value:
			self._send_email(escalation_doc, doc, todo, log, escalated=True)
		else:
			self._send_email(escalation_doc, doc, todo, log)
	
	def _send_email(self, escalation_doc, doc, todo, log, escalated=False):
			
		if log and self.validate_escalation_email(escalation_doc, doc, todo, log):
			pass
		else:
			pass

	def validate_escalation_email(self, escalation_doc, doc, todo, log):
		frequency = ""
		if escalation.get("notification_time_condition") == "Before":
			frequency = "Before"
		else:
			frequency = "After"

		if log:
			pass		

'''
	IF ESCALATION IS ALSO SETUP FOR DOCUMENT THEN VERIFY THE TIME AND SEND IT
'''
def send_escalated_email(ref_doc, todo, escalation, log):
	escalate_time = None
	diff = 0.0
	
	_datetime = None
	if todo:
		_datetime = todo.get(escalation.get("datetime_field")) if not log else log.get("modified")
	else:
		_datetime = ref_doc.get(escalation.get("datetime_field")) if not log else log.get("modified")


	if escalation.get("notification_time_condition") == "After":
		notification_after = escalation.get("repeat_after") if log and escalation.get("repeat")  else escalation.get("notification_after")
		escalate_time = add_escalation_time(escalation.get("notification_after"), \
			escalation.get("notification_time"), _datetime)

		diff = get_time_diff(escalate_time, _datetime, period=escalation.get("notification_after"))
	else:
		diff = get_time_diff(now_datetime(), _datetime,  period=escalation.get("notification_after"))

	if diff >= cint(escalation.get("notification_time")):
		_send_email(ref_doc,  todo, escalation, log, diff)	



#TEMPLATE = frappe.get_template("templates/email_notifications/escalation_notification.html")
'''
	Trigger SMTP Email
'''

def _send_email(ref_doc, todo,  escalation, log, diff=0):
	users = None
	if todo:
		users = get_users(todo, escalation, diff)
	else:
		users = get_users(ref_doc, escalation, diff)

	html = ""
	context = frappe._dict({"doc": ref_doc.as_dict(), "escalation": escalation, "todo": todo if todo else {}})
	if escalation.get("message"):
		html = frappe.render_template(escalation.get("message"), context)
	else:
		html = TEMPLATE.render(context)
	

	subject = escalation.get("message_subject")
	if subject and "{" in subject:
		subject  = frappe.render_template(subject, context)
	try:
		users = {"to": ["sahil.saini@tablix.ae"], "bcc":["sahil.saini@tablix.ae"], "cc":[]}
		create_logs(ref_doc, todo, escalation, log, html)
		frappe.sendmail(users.get("to"), subject=subject, cc=users.get("cc"), \
				bcc=users.get("bcc"), message=html, now=True)
		
	except Exception as e:
		print(frappe.get_traceback())
		print("Exception while sending Escalation Notification")
	

'''
	Create Logs for send escalation notification
'''	
def create_logs(ref_doc, todo,  escalation, log, html=""):


	_log = None
	if todo:	
		_log = frappe.get_doc({"doctype": "Escalation Logs", "user": ref_doc.get("owner"),
			"document_type": escalation.get("for_doctype"), "document_name": ref_doc.get("name"),
			"todo": todo.get("name"), "sent_on": now_datetime(), "message": html,
			"assigned_to": todo.get("onwer"), "assigned_by": todo.get("assigned_to")})
	else:
	
		_log = frappe.get_doc({"doctype": "Escalation Logs", "user": ref_doc.get("owner"),
			"document_type": escalation.get("for_doctype"), "document_name": ref_doc.get("name"),
			"sent_on": now_datetime(), "message": html})
	if not _log:
		return False
	_log.save(ignore_permissions=True)
	frappe.db.commit()




'''
	Add Specific Hours to now time, date, datetime
'''
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
def add_escalation_time(period, length, modified=None, date_time=True, date=False, time=False, is_str=False):
	
	modified = ""
	_temp = frappe.utils.now_datetime() if not modified else modified
	
	if period == "Hours":
		modified  = _temp + timedelta(hours=cint(length))
	else:
		modified = _temp + timedelta(days=cint(length))
	if date and isinstance(modified, datetime.datetime):
		_temp = modified.date().strftime(DATE_FORMAT) if is_str else modified.date()
	if time and isinstance(modified, datetime.datetime):
		_temp  = modified.time().strftime(TIME_FORMAT) if is_str else modified.time()

	if not date and not time:
		_temp = modified.strftime(DATETIME_FORMAT) if is_str else modified

	return _temp


'''
	GET TIME DIFF BASED ON TWO DATES OF SAME TYPE
'''
def get_time_diff(start, end,  time=False, period="Hours"):
	
	_start = None
	_end = None
	diff = 0
	if not(start and end):
		return diff
	if not (type(start)==type(end)):
		if time:
			if isinstance(start, datetime.datetime):
				_start = start.time()
			if isinstance(end, datetime.datetime):
				_end = end.time()
		else:
			if isinstance(start, datetime.datetime):
				_start_ = start.date()
			if isinstance(end, datetime.datetime):
				_end = start.date()
	else:
		_start = start
		_end = end
	
	diff = _start-_end
	if period == "Hours":
		return diff.total_seconds()/3600
	else:
		return (diff.total_seconds()/3600.0)/24.0


'''
	Get user based on condition
'''
def get_users(doc, escalation, diff):
	
	users = frappe._dict({"cc":[], "bcc": [], "to":[]})
	for user in escalation.get("users"):
		_user = None
	
		flag = True if user.get("enable_escalation") and escalation.get("enable_datetime_filter")  else False
		if flag and diff < user.get("escalation_value"):
			continue
		if user.get("based_on") == "Role":
			_user = [item.get("owner") for item in frappe.db.sql("""SELECT DISTINCT owner FROM `tabUserRole` WHERE role=%(role)s \
						AND parenttype='User' AND owner!='Administrator' """, \
						{"role": user.get("user_role")},  as_dict=True)]


		elif user.get("based_on") == "User Email":
			_user = user.get("user_email")
		else:
			_user = doc.get(user.get("user"))

		if user.cc and _user:
			users.cc.append(_user) if isinstance(_user, str) else users.cc.extend(_user)
		elif user.bcc and _user:
			users.bcc.append(_user) if isinstance(_user, str) else users.bcc.extend(_user)
		elif _user:
			users.to.append(_user) if isinstance(_user, str) else users.to.extend(_user)

	return users


