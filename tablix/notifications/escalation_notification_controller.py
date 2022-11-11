'''
	Added By Sahil
	Developer Sahil
	Email sahil.saini@tablix.ae
'''
import frappe
from frappe import msgprint, throw, _
from frappe.utils import cint, cstr, flt, datetime, now_datetime
from frappe.model.meta import Meta
from tablix.utils.user_roles import get_user_with_role

def test_escalation_notification():
	EscalationController()

class EscalationController(object):

	def __init__(self):
		self.get_and_send_escalation_notification()
	
	def get_and_send_escalation_notification(self):
		
		self.escalation_list = []
		for escalation in frappe.get_all("Escalation Notification", {"enabled": 1}):
			escalation = frappe.get_doc("Escalation Notification", escalation.get("name"))
			self.send_escalation_notification(escalation)	

	def send_escalation_notification(self, escalation):

		users = frappe._dict()
		pending_todo_list = []
		doctype_records = []
		doctype = "ToDo" if escalation.get("based_on") == "ToDo" else escalation.get("for_doctype")
		if escalation.get("based_on") == "ToDo":
			filters = {}
			pending_todo_list = self.get_pending_todo_list(escalation)
			doctype_records = self.get_doctype_records(escalation, pending_todo_list, from_todo=True)
		else:
			doctype_records = self.get_doctype_records(escalation)
		messages = []
		for record in doctype_records:
			message = frappe.render_template(escalation.get("message"), {"doc": record, "doctype": doctype,
						"escalation": escalation})
			if escalation.get("is_consolidate_email"):
				messages.append(message)
			else:						
				is_escalation, emails = self.get_emails(escalation, doctype, record)
				if not emails.get("user_emails"):
					continue
				self.send_escalation_email(escalation, doctype, record, message, emails, is_escalation)
					
		if escalation.get("is_consolidate_email"):
			is_escalation, emails = self.get_emails(escalation, doctype, doctype_records, consolidated=True)		
			self.send_escalation_email(escalation, doctype, doctype_records, messages, emails, is_escalation)


	def send_escalation_email(self, escalation, doctype, doctype_records, messages, emails, is_escalation):
		
		message = ""
		if messages and isinstance(messages, list):
			for msg in messages:
				message = "\n" + cstr(msg)
		else:
			message = messages
		print(message)
		try:
			subject = escalation.get("subject")
			if "{{" in escalation.get("subject"):
				subject = frappe.render_template(escalation.get("subject"), {"messages": messages, \
						"escalation": escalation, "doctype": doctype})
				
			#frappe.send_email(emails.get("user"), "", subject, message=message, cc=emails.get("cc"), \
				#bcc=emails.get("bcc"), delayed=False)
			self.make_escalation_logs(escalation, doctype, doctype_records, message, emails, is_escalation)
		except Exception as e:
			print(e)
			print(frappe.get_traceback())
	def get_pending_todo_list(self, escalation):

		args = self.get_condition_and_filters(escalation)
	
		filters = {
			"fieldvalue": escalation.get("docfield_value"),
			"for_doctype": escalation.get("for_doctype")
		}
		filters.update(args.get("filters"))
		condition = args.get("condition")
		if condition:
			condition += " AND {fieldname}=%(docfield_value)s  AND reference_type=%(for_doctype)s \
				".format(fieldname=escalation.get("docfield"))
		else:
			condition += " WHERE {fieldname}=%(docfield_value)s  AND reference_type=%(for_doctype)s \
				".format(fieldname=escalation.get("docfield"))
		
		query = "SELECT modified, owner, assigned_by, description, priority, date as deadline_date,\
			reference_type, reference_name {field} FROM `tabToDo`  %s".format(field=args.get("field"))
		todo_list =  frappe.db.sql(query%(condition), filters, as_dict=True)
		return todo_list	
			
		
	def get_doctype_records(self, escalation, pending_todo_list=[], from_todo=False):
		
		filters = {}
		condition = ""
		field = ""
		results = []
		if from_todo and not pending_todo_list:
			return results

		if escalation.get("based_on") == "ToDo":
			condition = " WHERE name IN %(name)s "
			filters.update({"name": tuple([todo.get("reference_name") for todo in pending_todo_list])})
		else:
			args = self.get_condition_and_filters(escalation)
			filters = args.get("filters")
			condition += args.get("condition")
			field = args.get("field")
			condition += " AND {status_fieldname}=%(docfield_value)s ".format(status_fieldname=escalation.get("docfield"))
				
		condition += " AND docstatus != 2 "
		query = " SELECT * {field} FROM `tab{doctype}` %s ".format(doctype=\
				escalation.get("for_doctype"), field=field)

		return frappe.db.sql(query%(condition), filters, as_dict=True)


	def get_condition_and_filters(self, escalation):
		
		filters = {"docfield_value":escalation.get("docfield_value")}
		doctype_name = "ToDo" if escalation.get("based_on") == "ToDo" else escalation.get("for_doctype")
		field = ""
		condition = ""
		args = {}
		if escalation.get("enable_datetime_filter"):
			condition, field = self.get_field_and_condition(escalation, doctype_name)
		args.update({"field": field, "condition": condition, "filters":filters})
		return args	
			
	def get_field_and_condition(self, escalation, doctype_name):
		field = self.get_docfield(escalation.get("datetime_field"), doctype_name)
		operator = ">=" if escalation.get("notification_time_condition") == "After" else "<="
		from_variable = to_variable = ""
		if escalation.get("notification_time_condition") == "After":
			from_variable = "CURDATE()" if field == "Date" else "NOW()"
			to_variable = escalation.get("datetime_field")
		else:
			to_variable = "CURDATE()" if field == "Date" else "NOW()"
			from_variable = escalation.get("datetime_field")
			
		filters = {
			"docfield": escalation.get("datetime_field"),
			"value": escalation.get("notification_time"),
			"operator": operator,
			"interval": escalation.get("notification_after").replace("s", ""),
			"from_variable": from_variable, "to_variable": to_variable
		}
		condition = ""
		_field = ""
		if field == "Datetime":
			_field = " , TIME_TO_SEC(TIMEDIFF({from_variable}, {to_variable}))/3600 AS interval_value ".format(**filters)
			condition = " WHERE TIME_TO_SEC(TIMEDIFF({from_variable}, {to_variable}))/3600 {operator} {value} ".format(**filters)
		elif field == "Date":
			_field = "  , DATEDIFF({from_variable}, {to_variable}) AS interval_value ".format(**filters) 
			condition = " WHERE DATEDIFF({from_variable}, {to_variable}) {operator} {value} ".format(**filters) 
		
		return condition, _field
			

	def get_docfield(self, fieldname, doctype):
		
		fieldtype =  None	
		doctype = frappe.get_doc("DocType", doctype)
		if hasattr(doctype.meta, fieldname):
			_fieldname = doctype.meta.get(fieldname)
			if isinstance(_fieldname, datetime.datetime):
				fieldtype = "Datetime"
			elif isinstance(_fieldname, datetime.date):
				fieldtype = "Date"
			elif isinstance(_fieldname, datetime.time):
				fieldtype = "Time"

			return fieldtype
		meta = Meta(doctype)
		for docfield in meta.fields:
			if fieldname == docfield.fieldname:
				fieldtype = docfield.fieldtype
				break

		return fieldtype		

	def get_emails(self, escalation, doctype, doc, consolidated=False):
		emails = frappe._dict({"user_emails":[],"all_emails":[],
			"cc_emails": [], "bcc_emails": []
		})
		
		if doc and isinstance(doc, list):
			doc = doc[0] if len(doc)>=1 else {}
		last_log = self.get_escalation_log(escalation, doctype, doc, " ORDER BY sent_on DESC")
		already_received  = sorted(self.get_users_who_already_received(last_log))
		all_emails = sorted(self.get_all_emails(escalation, doc))
		is_escalation = self.get_users_emails(escalation, doctype, doc, last_log, emails, already_received, all_emails)

		if is_escalation and emails.get("all_emails"):
			if sorted(emails.get("all_emails")) == already_received:
				self.reset_emails(emails)
		else:
			if escalation.get("enable_reminder"):
				diff = now_datetime() - last_log.get("sent_on")
				print(diff.total_seconds()/3600)
				if not (diff.total_seconds()/3600 >= flt(escalation.get("repeat_reminder_after"))):
					self.reset_emails(emails)
			else:
				self.reset_emails(emails)	
		return is_escalation, emails
	
	def get_users_emails(self, escalation, doctype, doc, last_log, emails, already_received, all_emails):
		first_log = {}
		is_escalation = False
		if last_log and last_log.get("escalated"):
			if all_emails != already_received:
				is_escalation = True
			first_log = self.get_escalation_log(escalation, doctype, doc, "ORDER BY sent_on ASC ")
		for user in escalation.get("users"):
			
			if last_log and is_escalation and user.get("enable_escalation"):
				diff =  now_datetime() - first_log.get("sent_on")
				if not (diff.total_seconds()/3600 >= flt(user.get("escalation_value"))):
					continue
			elif user.get("enable_escalation"):
				continue
			self.update_emails(user, doc, emails, is_update=True)
		if not last_log:
			is_escalation=True	
		return is_escalation
	
	def update_emails(self, user, doc, emails={}, is_update=False):
		temp = []
		if user.get("based_on") == "DocField":
			temp.append(doc.get(user.get("user")))
		elif user.get("based_on") == "User Email":
			temp.append(user.get("user_email"))
		elif user.get("based_on") == "Role":
			for role in get_user_with_role(user.get("user_role")):
				temp.append(role.get("user"))
	
		if is_update:	
			emails.all_emails.extend(temp)
			if user.get("cc"):
				emails.cc_emails.extend(temp,)
			elif user.get("bcc"):
				emails.bcc_emails.extend(temp)
			else:
				emails.user_emails.extend(temp)
				
		return temp		
	

	def get_users_who_already_received(self, log):
	
		users = frappe.db.get_values("Escalation Logs User", {"parent": log.get("name"), \
				"parenttype": "Escalation Logs"}, fieldname=["user"], as_dict=True)
		users = [user.get("user") for user in users]
		return users

	def get_all_emails(self, escalation, doc):
		
		all_emails = []
		for user in escalation.get("users"):
			all_emails.extend(self.update_emails(user, doc))
		return all_emails	
		
	def get_escalation_log(self, escalation, doctype, doc, order_by):
		filters = {
			"escalation": escalation.get("name"),
			"document_type": doctype, "order_by": order_by,
			"document_name": doc.get("name")
		}
		condition = ""
		if not escalation.get("is_consolidate_email"):
			condition  += " AND document_name=%(document_name)s"
		logs = frappe.db.sql("""SELECT E.name, E.escalated, E.reminder, E.document_type, E.sent_on FROM\
				`tabEscalation Logs` E WHERE E.document_type=%(document_type)s {0} AND E.escalation=%(escalation)s \
				{order_by} LIMIT 1""".format(condition, order_by=order_by), filters, as_dict=True)

		log = {}
		if logs and len(logs) >= 1:
			log = logs[0]
		return log
			

	def make_escalation_logs(self, escalation, doctype, doctype_records, message, emails, is_escalation):
		if not emails.get("user_emails"):
			return
		doc = None
		if isinstance(doctype_records, list):
			doc = doctype_records[0] if len(doctype_records)>=1 else {}
		else:
			doc = doctype_records
		reminders = 0
		if not is_escalation:
			reminders = self.get_nos_of_reminders(escalation, doctype, doc)
		escalation_log = frappe.get_doc({
			"doctype": "Escalation Logs", "sent_on": now_datetime(),
			"message": message, "document_type": doctype, 
			"escalation": escalation.get("name"),
			"reminder_no": reminders,
			"escalated": is_escalation if is_escalation else False,
			"reminder": True if not is_escalation else False,
			"document_name": doc.get("name") if not escalation.get("is_consolidate_email") else ""	
		})
		escalation_log.users = []
		escalation_log.ref_links = []
		for email in emails.get("all_emails"):
			escalation_log.users.append(frappe.get_doc({
				"doctype": "Escalation Logs User", "idx": len(escalation_log.users)+1,
				"parent": escalation_log.name, "parentfield": "users",
				"user": email, "parenttype": "Escalation Logs",		
			}))
		docs = doctype_records
		if isinstance(doctype_records, dict):
			docs = [doctype_records]
		for doc in docs:
			escalation_log.ref_links.append(frappe.get_doc({
				"document_type": doctype, "document_name": doc.get("name"),
				"parenttype": "Escalation Logs", "parent": escalation_log.name,
				"idx": len(escalation_log.ref_links) +1,
				"parentfield": "ref_links",
				"doctype": "Escalation Notification RefLink Item"
			}))
		#escalation_log.docstatus = 1
		escalation_log.save(ignore_permissions=True)

	def reset_emails(self, emails):
		
		emails.update({
			"user_emails": [], "cc_emails": [],
			"bcc_emails": [], "all_emails": []
		})	

	def get_nos_of_reminders(self, escalation, doctype, doc):
		reminders = 0
		filters = {}
		if not escalation.get("is_consolidate_email"):
			filters.update({"document_name": doc.get("name")})
		filters.update({
			"document_type": doctype,
			"escalation": escalation.get("name")
		})	
		reminders  = len(frappe.db.get_value("Escalation Logs", filters))			
		reminders += 1		
		return reminders
