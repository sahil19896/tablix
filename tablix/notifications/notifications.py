
'''
	Developer Sahil
        Email sahil.saini@tablix.ae
'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr, get_link_to_form
import json
from tablix.utils import get_all_emails, get_setting, user_roles, validation


DOCTYPES = [
	"Boq", "Purchase Order", "Sales Invoice", "Task",  "Sales Order", \
	"Material Request", "Employee", "Expense Claim", "Opportunity",  \
	"Leave Application", "Expense Claim"
]
STOCK = ["Material Request"]
SELLING = ["Boq", "Sales Order", "Quotation", "Opportunity", "Delivery Note"]
BUYING = ["Purchase Order", "Purchase Receipt", "Purchase Invoice"]
HR = ["Leave Application", "Expense Claim"]
PROJECT = ['Task', 'Project']

def notify(doc, method):
	from tablix.notifications.notification_controller import NotificationController
	doctype = doc.meta.get("name")
	setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	if setting.get("disable_notification"):
		return 
	if doc.get("doctype") not in DOCTYPES:
		return

	if not doc.get("__tran_state"):
		return 

	current_state = doc.get("__tran_state")
	if doc.get("doctype") == "Purchase Order":
		return send_purchase_order_notification(doc, current_state)

	elif doc.get("doctype") == "Sales Order":
		return send_sales_order_notification(doc, current_state)

	elif doc.get("doctype") == "Purchase Invoice":
		return send_purchase_order_notification(doc, current_state)

	elif doc.get("doctype") == "Boq":
		return send_boq_notification(doc, current_state)

	elif doc.get("doctype") == "Employee":
		return send_employee_notification(doc, current_state)
		
	elif doc.get("doctype") == "Material Request":
		return send_material_request_notification(doc, current_state)
		
	elif doc.get("doctype") == "Opportunity":
		return send_opportunity_notification(doc, current_state)

	elif doc.get("doctype") == "Expense Claim":
		return send_expense_claim_notification(doc, current_state)
		
	elif doc.get("doctype") == "Leave Application":
		return send_leave_application_notification(doc, current_state)
		
	elif doc.get("doctype") == "Task":
		return send_task_notification(doc, current_state);

def send_expense_claim_notification(doc, current_state):
	emails = []
	assign_to_user = None
	if validate_rejected(doc):
		assign_to_user = doc.get("owner")
		emails = [assign_to_user]
		reason = doc.get("reason")
		send_approval(doc, current_state, emails, reason)
		assign_to(doc, assign_to_user, current_state, reason)
	else:
		if (current_state.get("next_state")  == "Review"):
			dept = frappe.db.get_value("Employee", doc.get("employee"), "department")
			if dept == "Project Management":
				assign_to_user = current_state.get("email")
			else:
				doc.tablix_status = "Expense Approval"
				assign_to_user = doc.get("exp_approver")
			emails = [assign_to_user]
		elif (current_state.get("next_state")  == "Expense Approval"):
			assign_to_user = doc.get("exp_approver")
			emails = [assign_to_user]
		else:
			assign_to_user = current_state.get("email")
			emails = [assign_to_user]
			
		send_approval(doc, current_state, emails)
		assign_to(doc, assign_to_user, current_state)	
	
def send_leave_application_notification(doc, current_state):
	emails = []
	assign_to_user = None
	if validate_rejected(doc):
		assign_to_user = doc.get("owner")
		emails = [assign_to_user]
		reason = doc.get("reason")
		send_approval(doc, current_state, emails, reason)
		assign_to(doc, assign_to_user, current_state, reason)
	else:
		if (current_state.get("next_state")  == "HR Approved"): 
			assign_to_user = doc.get("leave_approver")
			emails = [assign_to_user]
		elif (current_state.get("next_state")  == "Approved"): 
			assign_to_user = doc.get("owner")
			emails = [assign_to_user]
		else :
			assign_to_user = current_state.get("email")
			emails = [assign_to_user]
			
		send_approval(doc, current_state, emails)
		assign_to(doc, assign_to_user, current_state)	
		
	
def send_boq_notification(doc, current_state):
	emails = []
	assign_to_user = None
	if (current_state.get("next_state")  == "Boq Complete" or current_state.get("next_state")  == "Sales Complete"):
		assign_to_user = doc.get("bdm")
		emails = [assign_to_user]
		
		if doc.get("bdm") and user_roles.has_role(doc.get("bdm"), "CEO") or user_roles.has_role(doc.get("bdm"), "CBDO") or user_roles.has_role(doc.get("bdm"), "COO"):
			if not doc.get("opp_owner") == "Administrator":
				if not doc.get("opp_owner") in emails:
					assign_to_user = doc.get("opp_owner")
					emails.append(doc.get("opp_owner"))
					
	elif (current_state.get("action")  == "Mark Complete" or current_state.get("action")  == "Design" or current_state.get("action")  == "Survey"):
		if current_state.get("state")  == "Site Visit" or current_state.get("state")  == "Site Survey":
			assign_to_user = None
			emails = [doc.get("bdm")]
			if doc.get("bdm") and user_roles.has_role(doc.get("bdm"), "CEO") or user_roles.has_role(doc.get("bdm"), "CBDO") or user_roles.has_role(doc.get("bdm"), "COO"):
				if not doc.get("opp_owner") == "Administrator":
					if not doc.get("opp_owner") in emails:
						emails.append(doc.get("opp_owner"))
		else:
			assign_to_user = doc.get("created_by")
			emails = [assign_to_user]
						
	elif (current_state.get("next_state")  == "BDM Verified"):
		assign_to_user = doc.get("account_manager")
		emails = [assign_to_user]
		
	else:
		emails, assign_to_user = get_emails(doc, current_state, "bdm")
		
	if validate_rejected(doc):
		reason = doc.get("reason")
		send_approval(doc, current_state, emails, reason)
		assign_to(doc, assign_to_user, current_state, reason)
	else:
		send_approval(doc, current_state, emails)
		if assign_to_user != None:
			assign_to(doc, assign_to_user, current_state)


def send_purchase_order_notification(doc, current_state):
	
	emails = []
	if validate_rejected(doc):
		assign_to_user = None
		assign_to_user = doc.get("tablix_rep")
		emails.append(assign_to_user)
		reason = doc.get("reason")
		send_approval(doc, current_state, emails, reason)
		assign_to(doc, assign_to_user, current_state, reason)
	else:
		emails.append(current_state.get("email"))
		assign_to_user = emails[0]
		if current_state.get("action") == "Approve":
			if not doc.get("owner") == "Administrator":
				if not doc.get("owner") in emails:
					emails.append(doc.get("owner"))
		send_approval(doc, current_state, emails)
		assign_to(doc, assign_to_user, current_state)	


def send_sales_order_notification(doc, current_state):

	if (current_state.get("next_state")  == "Approved"):
		assign_to_user = doc.get("manager_service_delivery") 
		emails = [assign_to_user]
		emails.append(doc.get("tablix_rep"))
		if doc.get("tablix_rep") and user_roles.has_role(doc.get("tablix_rep"), "CEO") \
			or user_roles.has_role(doc.get("tablix_rep"), "CBDO") \
			or user_roles.has_role(doc.get("tablix_rep"), "COO"):
			
			if not doc.get("owner") == "Administrator":
				if not doc.get("owner") in emails:
					emails.append(doc.get("owner"))

	else:
		emails, assign_to_user = get_emails(doc, current_state, "tablix_rep")
	if validate_rejected(doc):
		reason = doc.get("reason")
		send_approval(doc, current_state, emails, reason)
		assign_to(doc, assign_to_user, current_state, reason)
	else:
		send_approval(doc, current_state, emails)
		assign_to(doc, assign_to_user, current_state)


def send_material_request_notification(doc, current_state):
	emails = []
	assign_to_user = None
	if (doc.get("current_state") == current_state.get("state") and doc.get("next_state") == current_state.get("next_state")):
		return
	else:
		if validate_rejected(doc):
			reason = doc.get("reason")
			assign_to_user = doc.get("owner")
			emails.append(assign_to_user)	
			send_approval(doc, current_state, emails, reason)
			assign_to(doc, assign_to_user, current_state, reason)
		else:
			if current_state.get("next_state") == "Commercial Approved" and validation.has_substitute_item(doc):
				assign_to_user = current_state.get("email")
				emails.append(assign_to_user)
			elif current_state.get("next_state") == "Commercial Approved":
				doc.docstatus = 1
				doc.tablix_status = "CTO Approved"
				assign_to_user = current_state.get("assign_to")
				emails.append(assign_to_user)
			else:
				assign_to_user = current_state.get("email")
				emails.append(assign_to_user)
				
			if current_state.get("action") == "Approve":
				if not doc.get("owner") == "Administrator":
					if not doc.get("owner") in emails:
						emails.append(doc.get("owner"))	
			send_approval(doc, current_state, emails)
			assign_to(doc, assign_to_user, current_state)
			doc.current_state = current_state.get("state")
			doc.next_state = current_state.get("next_state")
		

def send_purchase_invoice_notification(doc, current_state):
	print("Purchase Invoice Notification")
	print("\n\n\n")


	
def send_employee_notification(doc, current_state):
	print("Employee")
	print("\n\n\n")

	
def send_opportunity_notification(doc, current_state):

	emails, assign_to_user = get_emails(doc, current_state, "bdm")
	#msgprint(str(assign_to_user))
	if validate_rejected(doc):
		reason = doc.get("reason")
		send_approval(doc, current_state, emails, reason)
		assign_to(doc, assign_to_user, current_state, reason)
	else:
		send_approval(doc, current_state, emails)
		assign_to(doc, assign_to_user, current_state)
	

def send_task_notification(doc, current_state):
	
	emails = []
	if not doc.get("assigned_to") or not doc.get("assigned_by"):
		
		frappe.throw(_("Mandatory fields: <b style='color:red'> Assigned To Rep \
			 and Assigned By Rep</b>"))

	if current_state.get("action") == "Reject":
		emails.append(doc.get("owner"))
		send_approval(doc, current_state, emails, doc.get("reason"))
		assign_to(doc, doc.get("owner"), current_state, doc.get("reason"))		

	elif current_state.get("action") == "Review":
		email = doc.get("task_approver") if doc.get("task_approver") else doc.get("assigned_to")
		emails.append(email)
		send_approval(doc, current_state, emails)
		assign_to(doc, email, current_state)
	else:
		email = doc.get("assigned_to") if doc.get("task_approver") else doc.get("owner")
		emails.append(email)
		send_approval(doc, current_state, emails)
		assign_to(doc, email, current_state)
		

def get_emails(doc, current_state, fieldname):
	
	emails = []
	assign_to_user = None
	
	if current_state.get("action") == "Reject":
		assign_to_user = doc.get(fieldname)
		emails = [assign_to_user]
		# if bdm/tablix_rep is ceo/coo/cbdo after rejection it should be assigned to owner & not bdm/tablix rep & mail will also go to owner
		if assign_to_user and user_roles.has_role(assign_to_user, "CEO") \
			or user_roles.has_role(assign_to_user, "CBDO") \
			or user_roles.has_role(assign_to_user, "COO"):
			if doc.get("doctype") != "Boq":
				if not doc.get("owner") == "Administrator":
					assign_to_user = doc.get("owner")
					if not doc.get("owner") in emails:
						emails.append(doc.get("owner"))
			else:
				if not doc.get("opp_owner") == "Administrator":
					assign_to_user = doc.get("opp_owner")
					if not doc.get("opp_owner") in emails:
						emails.append(doc.get("opp_owner"))
		if current_state.get("next_state") == "Designing":
			assign_to_user = doc.get("created_by")
			emails.append(assign_to_user)
	else:
		if (current_state.get("next_state")  == "Manager Approval" and doc.get("doctype") != "Boq"):
			assign_to_user = doc.get("account_manager")
			emails = [assign_to_user]
		else:
			assign_to_user = current_state.get("email")
			emails = [assign_to_user]
			# on every approval a mail should go to bdm/tablix_rep & if bdm/tablix_rep is \
			# ceo/coo/cbdo a mail should also go to owner & not bdm/tablix rep & mail will also go to owner
			if current_state.get("action") == "Approve":
				if not doc.get(fieldname) in emails:
					emails.append(doc.get(fieldname))
				if doc.get(fieldname) and user_roles.has_role(doc.get(fieldname), "CEO") \
					or user_roles.has_role(doc.get(fieldname), "CBDO") \
					or user_roles.has_role(doc.get(fieldname), "COO"):
					if doc.get("doctype") != "Boq":
						if not doc.get("owner") == "Administrator":
							if not doc.get("owner") in emails:
								emails.append(doc.get("owner"))
					else:
						if not doc.get("opp_owner") == "Administrator":
							if not doc.get("opp_owner") in emails:
								emails.append(doc.get("opp_owner"))
			

	return emails, assign_to_user
	
def send_approval(doc, current_state, emails=[], reason=""):

	#setting = get_setting()
	setting = {}
	if doc.get("docstatus") == 2:
		frappe.msgprint("Cancelled")
		return send_cancel_notification(doc, current_state, emails,  setting)

	else:	
		return notify_employee(doc, emails, reason)

		
def send_cancel_notification(doc, current_state, emails=[], setting={}):

	emails.extend(current_state.get("email"))
	args = get_current_state(doc, current_state)
	notify_employee(doc, emails)

def notify_employee(doc, emails,  reason=""):

	selling, buying, stock, project = None, None, None, None
	if doc.get("doctype") in SELLING:
		selling = True
	if doc.get("doctype") in STOCK:
		stock = True
	
	if doc.get("doctype") in BUYING:
		buying = True
	if doc.get("doctype") in PROJECT:
		project = True

	user = frappe.session.user
	template = frappe.get_template("templates/email_notifications/approval_notification.html")
	link = get_link_to_form(doc.doctype, doc.name)
	html = template.render({"doc": doc, "link":link, "reason": reason, "selling": selling,\
				 "buying": buying, "stock":stock, "project":project, "user":user})
	send_email(doc, html, emails)
	

def send_email(doc, html, emails):
	try:
		subject = " {0}: {1}: {2}".format(doc.get("doctype"), doc.get("name"), doc.get("tablix_status")or doc.get("status") or "")
		frappe.sendmail(emails, subject=subject, delayed=False, reference_doctype=doc.get("doctype"), \
				reference_name=doc.get("name"), message=html)
	except Exception as e:
		print(frappe.get_traceback())
		frappe.msgprint("""`<h2>Assign this document to respective employee Manually</h2>\n  \
				Report this error to Administrator: \n {0}`""".format(frappe.get_traceback()))
		


def assign_to(doc, assign_to, current_state, reason=None):
	from frappe.desk.form.assign_to import add, clear
	clear(doc.get("doctype"), doc.get("name"))
	if not reason:
		reason = doc.get("reason") if doc.get("reason") else None
	
	description = ""
	# For Stock Modules
	if doc.get("doctype") in STOCK:
		description = "{0} of {1} has been assigned by {2}".format(doc.get("project").encode('ascii','ignore'),\
				 doc.get("customer_order"), doc.get("modified_by"))
	# For HR Modules
	elif doc.get("doctype") in HR:
		description = "{0} of {1} has been assigned by {2}".format(doc.get("doctype"), \
				doc.get("employee_name"), doc.get("modified_by"))
	
	# For Selling Module
	elif doc.get("doctype") in SELLING:
		project = ""
		customer = doc.get("customer_name") if doc.get("customer_name")  else doc.get("customer")
		if not customer:
			customer = ""
		if doc.get("project_name") :
			project = doc.get("project_name")
		elif doc.get("project"):
			project = doc.get("project")
		elif doc.get("project_site_name"):
			project  = doc.get("project_site_name")
			
		description = "{0} of {1} has been assigned by {2}".format(project.encode('ascii','ignore'),\
				 customer.encode('ascii','ignore'), doc.get("modified_by"))

	# For Buying Module
	elif doc.get("doctype") in BUYING:
		supplier = doc.get("supplier") or ""
		project = doc.get("project") or ""
		description = "{0} of {1} has been assigned by {2}".format(project.encode('ascii','ignore'),\
				 supplier.encode('ascii','ignore'), doc.get("modified_by"))

	elif doc.get("doctype") in PROJECT:
		description = "Task No: {0} has been Assigned To {1} and By {2}, Please approve it.\
				<br>".format(doc.get("name"), doc.get("assigned_to"), doc.get("assinged_by"))
		
	
	add({
		"assign_to": assign_to,
		"name": doc.get("name"),
		"doctype": doc.get("doctype"),
		"description":  "{0}<br><br> Reason(Only if Rejected):<br>{1}".format(description, reason)
	})
	

'''
	User information is linked with 
'''

def get_user_info(doc,  current_state):

	args = frappe._dict()
	args['assign_to'] = frappe.db.get_value("Employee", filters={"user_id": current_state.get("email")}, fieldname="*", as_dict=True)
	args['assign_by'] = frappe.db.get_value("Employee", filters={"user_id": frappe.session.user}, fieldname="*", as_dict=True)
	return args


def validate_rejected(doc):
	status = frappe.db.sql(""" SELECT name FROM `tabWorkflow State`  WHERE name LIKE '%Rejected%' """)
	status = [i[0] for i in status]
	return doc.get("tablix_status") in status



'''
	UserInfo is current state
'''
def get_next_state(current_state):

	next_action = None
	nex_state = None
	if current_state.get("action") == "Reject":
		next_action = "Approval Request"
		next_stae
	else:
		next_action = "Approve"
		
	try:
		doc = frappe.db.value("Workflow Transition", filters={"state": current_state.get("next_state"),"action": current_state.get("action"),\
					"parent": current_state.get("parent"), "parentfield":"transitions"}, fieldname="*", as_dict=True)
		return doc
	except Exception as e:
		frappe.throw("error")		
