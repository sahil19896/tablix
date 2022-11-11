'''
	Developer Sahil
	Email sahil.saini@tablix.ae

'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt, now_datetime, datetime
from tablix.notifications.notification_controller import NotificationController
from tablix.utils import get_date, get_time, get_datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class SupportController(NotificationController):
	

	def __init__(self, doc, doctype, method):
		self.doc = doc
		self.doctype = doctype
		self.method = method

	def validate(self):
		self.validate_issues()
		self.validate_maintenance_contract()	
		print("Support Validate")
		

	def validate_cancel(self):
		print("Support validate cancel")


	def validate_submit(self):
		
		print("Support Submit")


	def validate_issues(self):
		if not self.doctype  == "Issue":
			return 
		self.update_issue_times()

	def update_issue_times(self):
		
		if self.doctype  != "Issue" or not self.doc.get("status") == "Closed":
			return False
		if not self.doc.get("attended_datetime") or not self.doc.get("rectification_datetime"):
			raise frappe.ValidationError(_("Please enter the <b>Attended Datetime and Rectification Datetime</b>"))
		attended_datetime  = get_datetime(self.doc.get("attended_datetime"), dtfrmt=DATETIME_FORMAT)
		rectification_datetime = get_datetime(self.doc.get("rectification_datetime"), dtfrmt=DATETIME_FORMAT)
		if attended_datetime >= rectification_datetime:
			raise frappe.ValidationError(_("Attended Datetime can not be <b>greater than/equal to </b> rectification datetime"))
		diff = rectification_datetime - attended_datetime
		self.doc.rectification_time = diff.total_seconds()/3600

		if self.doc.status == "Closed":
			opening_date = get_date(self.doc.get("opening_date"), "%Y-%m-%d", is_date=True)
			opening_time = get_time(self.doc.get("opening_time"))
			if not opening_date or not opening_time:
				raise frappe.ValidationError("Please enter  <b>Opening Date and Opening Time </b>.")
			opening_datetime = datetime.datetime(opening_date.year, opening_date.month, opening_date.day, \
						opening_time.hour, opening_time.minute, 00)
			diff = rectification_datetime - opening_datetime
			self.doc.time_duration_ = (diff.total_seconds()/3600)



	def validate_maintenance_contract(self):
		print(self.doctype)
		if self.doctype != "Maintenance Contract":
			return
		self.validate_maintenance_contract_mandatory_fields()
	
	def validate_maintenance_contract_mandatory_fields(self):
		if not self.doc.get("so_number"):
			frappe.ValidationError(_("Please enter Sales Order Number."))
		if not self.doc.get("title"):
			frappe.ValidationError(_("Please enter <b>Title</b>"))
			
		so = frappe.get_doc("Sales Order", self.doc.get("so_number"))
		if not so.is_amc:
			frappe.ValidationError(_("Please enter the corrent <b>Sales Order</b>. This contact doesn't cover any AMC."))
	
		self.doc.boq = so.get("boq")
		self.doc.customer = so.get("customer")
		self.doc.customer_name = so.get("customer_name")
				
			
