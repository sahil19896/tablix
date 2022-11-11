
import tablix, frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr, now_datetime
from frappe.utils.background_jobs import enqueue


HR_DOCTYPE = ['Expense Claim', 'Leave Application']
STOCK_DOCTYPE = ['Material Request']
SALES_DOCTYPE = ['Sales Order', 'Delivery Note', 'Sales Invoice', 'Quotation']
BUYING_DOCTYPE = ['Purchase Order', 'Purchase Invoice', 'Purchase Receipt', 'Purchase Invoice']
CRM_DOCTYPE = ['Opportunity']

class NotificationController(object):
	def send_notification(self):
		self.update_defaults_values()	
		if not self.doc.get("__tran_state"):
			return

		self.update_workflow()
		self._send_notification()
		if hasattr(self, "get_project_name"):
			if callable(self.get_project_name):
				self.project = self.get_project_name()
		print(frappe.session.user)
	def update_defaults_values(self):
	
		if hasattr(self, "meta"):
			self.dt = self.doctype = self.meta.get("name")
			self.doc  = self
			self.setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
						
	def _send_notification(self):
	
		if not self.current_workflow_state:
			return
		requested_by = self.get_current_workflow_user()
		approver = self.get_next_workflow_user()
		if self.user_already_approved(approver) and not self.setting.get("required_each_level_of_approval"):
			approver = self.get_next_state_workflow_user(approver)
		
		print("---"*10)
		print(approver)
		print(requested_by)
		print("---"*10)
	
		msg  = self.get_notification_message(with_template=True)
		if not approver:
			return
		
		self.send_final_notification_email(approver, msg)
		self.clear_previous_assignment()
		self.make_document_assignment(approver)
		self.update_workflow_approval_logs(requested_by, approver)

	def make_document_assignment(self, email):
		
		msg = None
		reason = ""
		if self.is_rejected_state():
			if(hasattr(self.doc, "reason")):
				reason = self.doc.get("reason")
		user_msg = ""
		if(hasattr(self, "get_user_message")):
			msg = self.get_user_message()
		else:
			project_args = self.get_notification_message()
			msg = "{project} - {name} has been assigned to you by {user}".format(user_msg=user_msg,\
				project=project_args.get("project"), name=self.doc.get("name"), user=self.doc.get("modified_by"))
		if reason:
			msg += " <br><br><b>Reason for disapproval:</b><br>{0} ".format(cstr(self.doc.get("reason")))
		self._make_document_assignment(email, msg)
				

	def _make_document_assignment(self, email, msg):
	
		from frappe.desk.form.assign_to import add 
		against = ""
		if self.dt in SALES_DOCTYPE:
			against = self.doc.get("customer")
		elif self.dt in BUYING_DOCTYPE:
			against = self.doc.get("supplier")
		elif self.dt in HR_DOCTYPE:
			against = self.doc.get("employee_name")
		add({
			"assign_to": [email],
			"name":  self.doc.get("name"),
			"doctype": self.dt,
			"description": msg
		})

	def update_workflow(self):
		
		self.workflow = {}
		self.current_workflow_state = {}
		self.next_workflow_state = {}

		self.workflow_transition_state_map = frappe._dict()
		for workflow in frappe.db.get_values("Workflow", {"document_type": self.dt,
								"is_active":1}, as_dict=True):
			self.workflow = frappe.get_doc("Workflow", workflow.get("name"))
			
		for transition in self.workflow.get("transitions"):
			#if not self.workflow_transition_state_map.has_key(transition.get("state")):
			if not transition.get("state") in self.workflow_transition_state_map:		
				self.workflow_transition_state_map[transition.get("state")] = []

			self.workflow_transition_state_map[transition.get("state")].append(transition)

		self.update_workflow_current_state()
		self.update_workflow_next_state()

	def get_assign_to_user(self):
		
		assign_to = None
		if hasattr(self, "get_workflow_assign_to"):
			assign_to = self.get_workflow_assign_to()
		if not assign_to:
			assign_to = self.next_workflow_state.get("assign_to")
		return assign_to
	
	def update_workflow_current_state(self):
		self.current_workflow_state = self.doc.get("__tran_state")
	
	def update_workflow_next_state(self):
		self.next_workflow_state = None
		next_state = self.current_workflow_state.get("next_state") if self.current_workflow_state else None
		if next_state and self.workflow_transition_state_map.get(next_state):
			self.next_workflow_state = self.workflow_transition_state_map.get(next_state)[0]

	def get_workflow_state_docstatus(self, state):
		docstatus = 0
		for _state in self.workflow.get("states"):
			if _state.get("state") ==  state.get("state"):
				docstatus = _state.get("doc_status")
				break
		return docstatus
					
	def get_notification_message(self, with_template=False):
		
		project = ""
		bdm = ""
		account_manager = ""
			
		if hasattr(self.doc, "project"):
			project = self.doc.get("project")
		elif hasattr(self.doc, "project_site_name"):
			project = self.doc.get("project_site_name")
		elif hasattr(self.doc, "project_name"):
			project = self.doc.get("project_name")

		if hasattr(self.doc, "bdm"):
			bdm = self.doc.get("bdm")
		if hasattr(self.doc, "account_manager"):
			account_manager = self.doc.get("account_manager")
		if hasattr(self.doc, "customer_name"):
			project = self.doc.get("customer_name")
		if project:
			project = project.encode("ascii", "ignore")
	
		if with_template:
			template = frappe.get_template("templates/email_notifications/approval_notification.html")
			msg = template.render({
					"doc":self.doc, "bdm": bdm, "user": self.get_email_user_fullname(),
					"account_manager": account_manager, "project": project, "doctype":self.dt
				})
		
		else:
			msg = {"project": project, "bdm": bdm, "account_manager": account_manager}	
		
		return msg

	
	def get_next_workflow_user(self):
		user = None
		if self.next_workflow_state:
			user = self.get_workflow_user_email(self.next_workflow_state)
		return user

	def get_current_workflow_user(self):
		user = None
		if self.current_workflow_state:
			user = self.get_workflow_user_email(self.current_workflow_state)
		return user

	def get_workflow_user_email(self, state):
		email = None
		if hasattr(self, "get_workflow_email"):
			email = self.get_workflow_email()
		if not email:
			if state and state.get("based_on") == "Field":
				field = state.get("select_field")
				if field:
					email = self.doc.get(field)
			elif state:
				email = state.get("email")
		if email and email == "Administrator":
			email  = self.setting.get("erp_admin")

		return email		 

	def get_email_user_fullname(self, user=None):
		if not user:
			user = frappe.session.user
		user = frappe.db.get_value("User", self.doc.get("modified_by"), ["first_name", "last_name"], as_dict=True)

		fullname = cstr(user.get("first_name")) + " " + cstr(user.get("last_name"))
		return fullname

	def get_next_state_workflow_user(self, approver):
		
		_workflow_states = [state for state in self.workflow.get("transitions")]
		next_states = 	_workflow_states[self.next_workflow_state.get("idx"):len(_workflow_states)]
		ignored_states = [state.get("state") for state in self.setting.get("ignore_states")]
		_approver = None
		for transition in next_states:
			if transition.get("state") in ignored_states:
				continue
			if self.get_workflow_user_email(transition) != approver and transition.get("action") in ["Approve", "Cancel"]:
				_approver = self.get_workflow_user_email(transition)
				if _approver:
					self.doc.docstatus = self.get_workflow_state_docstatus(transition) 
					self.doc.set(self.workflow.get("workflow_state_field"), transition.get("state"))
					approver = _approver
				break
		return approver 

				
	def send_final_notification_email(self, email, html):
		try:
			if self.setting.get("disable_notification"):
				return
			if not email:
				frappe.msgprint("<b>Email not found</b>, Please discuss with <b>Admin</b>.")
				return False

			if email and isinstance(email, str):
				email = [email]
			subject = "{0}: {1}: {2}".format(self.dt, self.doc.get("name"),
					self.doc.get("tablix_status")or self.doc.get("status") or "")
			frappe.sendmail(email, subject=subject, 
				delayed=False, reference_doctype=self.dt, reference_name=self.doc.get("name"), message=html)

			
		except Exception as e:
			print(frappe.get_traceback())
			frappe.msgprint("""`<h2>Assign this document to respective employee Manually</h2>\n  \
					Report this error to Administrator: \n {0}`""".format(frappe.get_traceback()))

			
	def update_workflow_approval_logs(self, requested_by, approver, current_state={}, prev_state={}):
	
		approval_log = None
		reason = ""
		if hasattr(self.doc, "reason"):
			reason  = self.doc.get("reason")
		is_rejected = self.is_rejected_state()
		if not prev_state and self.current_workflow_state:
			prev_state = self.current_workflow_state
		if not current_state and self.next_workflow_state:
			current_state = self.next_workflow_state

		if not frappe.db.get_value("Approval Logs", self.doc.get("name")):
			approval_log = frappe.get_doc({
					"doctype":"Approval Logs", "document_name": self.doc.get("name"),
					"document_type": self.dt, "current_status": current_state.get("state"),
					"in_current_user_queue": approver, "assigned_time": now_datetime()
				})
			approval_log.save(ignore_permissions=True)
			approval_log.users = []
		else:
			approval_log = frappe.get_doc("Approval Logs", self.doc.get("name"))
		
		approval_log.assigned_time = now_datetime()
		approval_log.current_status = current_state.get("state")
		approval_log.in_current_user_queue =  approver
		approval_log.users.append(frappe.get_doc({
			"idx": len(approval_log.users) + 1, "doctype": "Approval Logs Item",
			"parentfield": "users", "parenttype": "Approval Logs",
			"parent": self.doc.get("name"),
			"user_name": approver, "approval_datetime": now_datetime(),
			"prev_state": prev_state.get("state"), "current_state": current_state.get("state"),
			"approved_by": frappe.session.user, "requested_user": requested_by,
			"action": self.current_workflow_state.get("action"),
			"user_role": self.current_workflow_state.get("allowed"),
			"reason": reason if is_rejected else "",
			"is_rejected":  1 if is_rejected else 0
		}))
		try:
			approval_log.save(ignore_permissions=True)
		except Exception as e:
			print(e)
			print(frappe.get_traceback())
	def is_rejected_state(self):
		return self.current_workflow_state.get("action") == "Reject"
		
	def clear_previous_assignment(self):
		from frappe.desk.form.assign_to import clear
		clear(self.dt, self.doc.get("name"))

	def get_workflow_user_role_based(self):
		# Later depends on company required we will implement
		from frappe.core.page.permission_manager import get_users_with_role
		role = self.next_workflow_state.get("allowed")
	
	def user_already_approved(self, email):
		print("\n\n\n\n\n\n\n")	
		print(email)
		if frappe.db.get_value("Approval Logs Item", {"parent": self.doc.get("name"), "parenttype": "Approval Logs",
				"user_name": email, "action": "Approve"}):
			return True
		else:
			return False
		
