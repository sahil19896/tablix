'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt, datetime, today, nowdate, nowtime, get_link_to_form
from calendar import monthrange
from tablix.utils import  update_emp_leave, get_date, format_date, get_first_last_date, get_next_month
from erpnext.hr.doctype.leave_allocation.leave_allocation import get_carry_forwarded_leaves
from tablix.notifications.notification_controller import NotificationController



class HRController(NotificationController):

	def __init__(self, doc, doctype, method):
		self.doc = doc
		self.doctype =  doctype
		self.dt = doctype
		self.method = method
		self.setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
		
	def validate(self):
		self.update_expense_account()
		self.validate_leave_approval()
		self.send_notification()


	def validate_cancel(self):
		self.clear_previous_assignment()

	def validate_submit(self):
		self.update_leave_application_status()
		self.send_notification()
		

	def update_expense_account(self):
		if(self.doctype in ['Expense Claim']):
			if(self.doc.comapny == "Tablix Technology LLC"):
				self.doc.payable_account = self.setting.get("default_expense_account")
				self.doc.cost_center = "Main - Tab"
			else:
				self.doc.payable_account = "200113 - Expense Claim Account - T-IND"
				self.doc.cost_center = "Main - T-IND"
	
	def validate_leave_approval(self):
		if(self.doctype in ['Leave Application']):
			emp = frappe.get_doc("Employee", self.doc.get("employee"))
			if not emp.get("reports_to"):
				frappe.throw(_("Please enter reports to in Employee <b>{0}</b> ".format(emp.get("name"))))
				
			if self.doc.get("leave_approval"):
				approver = frappe.db.get_value("Employee Leave Approver", {"parent": self.doc.get("employee"), \
						"parenttype": "Employee"}, as_dict=True),
				if approver:
					self.doc.leave_approver = approver.get("leave_approver")
				
			if not self.doc.get("leave_approver"):
				raise frappe.ValidationError(_("Please update <b>Leave Approval in Employee List</b>, Talk to HR for more info."))


	def update_leave_application_status(self):
		if(self.doctype in ['Leave Application']):
			self.doc.status = self.doc.tablix_status


		
DATE_FORMAT = "%Y-%m-%d"
'''
	Update Expsense Claim assignment after updation of document
'''

def assign_expense_claim(doc, method=None):
        from frappe.desk.form.assign_to import add, clear
        clear(doc.get("doctype"), doc.get("name"))
        add({
                "assign_to": doc.get("exp_approver"),
                "name": doc.get("name"),
                "doctype": doc.get("doctype"),
                "description":  "{0} ".format(doc.get("owner"))
        })

def update_leaves(*args, **kwargs):

	for emp in frappe.get_list("Employee"):
		doc =  frappe.get_doc("Employee", emp.get("name"))
		doc.save()


def update_leave_application(doc, method=None):	
	update_emp_leave(doc, method)



def update_employee_leaves(doc, method=None):
	setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	doj = doc.get("date_of_joining")
	date = get_date(doj, DATE_FORMAT)
	now_date = get_date(nowdate(), DATE_FORMAT)
	create_leave_allocation(doc, date, setting)
	while True:
		date = get_next_month(date)
		if date <= now_date:
			create_leave_allocation(doc, date, setting)
		else:
			break
	'''
	create_leave_allocation(doc, setting)
	'''
'''
# Comment Standard  function
def update_employee_leaves(doc, method=None):
	setting = frappe.get_doc("Tablix Setting", "Tablix Setting")                 
	doj=str(doc.date_of_joining)
	doj=datetime.datetime.strptime(doj, "%Y-%m-%d")
	d2=datetime.datetime.strptime(today(),"%Y-%m-%d")
	delta = 0
	while True:
		mdays = monthrange(doj.year, doj.month)[1]
		if doj <= d2:
			delta += 1
		else:
			break
		doj += datetime.timedelta(days=mdays)
		

	leaves_alloc = delta*2.5
	doc.total_leaves_allocated = leaves_alloc
	doc.balance_leave = flt(leaves_alloc) - flt(doc.total_leaves_consumed)
	if not method:
		doc.save()
		frappe.db.commit()

'''

'''
	Check whether user are new joinee  or no
	and then give leaves accordingly
'''
def create_leave_allocation(doc, _date, setting):
	doj = get_date(_date, is_string=True)
	
	first_date, last_date = get_first_last_date(doj, DATE_FORMAT, start_of_month=True)
	if not frappe.db.sql(""" SELECT name from `tabLeave Allocation` WHERE from_date = %(from_date)s  AND to_date=%(to_date)s """,\
				{"from_date": first_date, "to_date": last_date}):
		insert_leave(doc, setting, first_date, last_date)
			
'''
	Create leave allocation for employee
'''
def insert_leave(doc, setting, first_date, last_date, leaves=None):

	if not leaves:
		leaves = setting.get("leave_days")
	cf = get_carry_forwarded_leaves(**{"employee":doc.get("employee"), "carry_forward":1, "leave_type": setting.get("leave_type"), "date": first_date})
	total = cf + leaves
	doc  = frappe.get_doc({ "doctype": "Leave Allocation", "employee": doc.get("name"), "leave_type": setting.get("leave_type"),
				"from_date":first_date, "to_date": last_date, "new_leaves_allocated": leaves, "carry_forward":	1,
				"total_leaves_allocated":total, "carry_forwarded_leaves": cf, "docstatus":1})
	try:
		doc.save(ignore_permissions=True)
		frappe.db.commit()
	except:
		pass


def bulk_expiry_reminder():
	
	expired_records = []
	template = frappe.get_template("templates/email_notifications/expiry_notification.html")
	emp_list = frappe.get_list("Employee", filters={"status": "Active"}, fields="*")
	for emp in emp_list:
		flag = expiry_reminder(emp)
		if flag:
			expired_records += flag
	
	headers = ['Document Type', 'Employee ID', 'Employee Name', 'Employee Email', 'Expiry Date', 'Days Left']	
	if expired_records:
		send_expiry_notification(expired_records, headers, template)



def expiry_reminder(doc, method=None):

	res  = []
	flags = frappe._dict({
		"visa_expiry":is_expired(doc.get("visa_expiry"), None, "visa_expiry", "Visa"), 
		"eid_expiry": is_expired(doc.get("eid_expiry"), None, "eid_expiry", "Emirate ID"), 
		"health_card_expiry":is_expired(doc.get("health_card_expiry"),None, "health_card_expiry", "Health Card"),
		"labour_card_expiry_date":is_expired(doc.get("labour_card_expiry_date"), None, "labour_card_expiry_date", "Labour Card")
	})
	flag = False
	for key, val in flags.iteritems():
		if val:
			flag = True
			res.append({"doc":doc, "field": val.get("field"), "doc_type": val.get("doc_type"), "days": val.get("days")})
		
	return res if flag else None
	
		
	
def send_expiry_notification(expiry_records, headers, template):
	
	html = template.render({"records": expiry_records, "headers":headers})
	emails = [email.get("user_id") for email in frappe.get_list("Employee", "user_id", filters={"status": "Active", "designation": "HR Manager"})]
	frappe.sendmail(emails, subject="Document Expiry Detail of Employee", message=html, delayed=False) 

	
def is_expired(from_date, cur_date=None, field=None, doc_type=None):
	data  = {}
	if not cur_date:
		cur_date = get_date(nowdate(), DATE_FORMAT, is_date=True)
	if not from_date:
		return False
	
	diff = from_date - cur_date
	if diff.days <= 30:
		data.update({"field": field, "doc_type": doc_type, "days": diff.days})
		return data
	return False	




def send_notification(doc, method=None):

	from frappe.desk.form.assign_to import add, clear
	from tablix.notifications.notifications import notify_employee
	emails  = []
	reason, approver =  "", ""
	setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	if not setting.get("account_expense_claim_approver"):
		msgprint(_("Kindly set <b>Account Expense Claim Approver</b> in Tablix Setting doctype"))
		return

	if doc.get("approval_status") == "Approved":
		clear(doc.get("doctype"), doc.get("name"))
		emails.append(setting.get("account_expense_claim_approver"))
		approver = setting.get("account_expense_claim_approver")
	else:
		clear(doc.get("doctype"), doc.get("name"))
		emails.append(doc.get("owner"))
		approver = doc.get("owner")
		reason = "{0}-{1} Rejected by <b>{2}</b>.".format(doc.get("doctype"), doc.get("name"), frappe.session.user)
	add({
		"assign_to": approver,
		"name": doc.get("name"),
		"doctype": doc.get("doctype"),
		"description": "{0}-{1} assign to you by {2}".format(doc.get("doctype"), doc.get("name"), frappe.session.user)
	})	
	notify_employee(doc, emails, reason)
