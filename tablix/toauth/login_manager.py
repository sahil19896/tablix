'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe import _, throw
from frappe.utils import cint, flt, cstr
from frappe.utils.password import check_password
from frappe.sessions import Session
import json
import werkzeug.exceptions
from tablix.tmobileapp import utils 
from tablix.tgeo import location as geo_location, logs

KEYS_TO_DISCARD = ['cmd', 'usr', 'pwd', 'method']
DOC_KEYS_TO_DISCARD = ['parent', 'parenttype', 'parentfield', 'owner', 'creation',
		 'modified', "modified_by", 'last_known_versions']
class LoginManager:

	def __init__(self, request_handler,  *args, **kwargs):
		self.kwargs = frappe._dict(kwargs)
		self.data =  frappe._dict()
		self.user_id = None
		self.filters = frappe._dict()
		self.device_info = frappe._dict()
		self.user_info = frappe._dict()
		self.employee_info = frappe._dict()
		self.headers = frappe._dict()
		self.update_headers()
		self.resources = frappe._dict()
		self.location = frappe._dict()
		self.update_location_info()
		self.update_device_info()
		self.credentials  = frappe._dict()
		self.request_handler = request_handler
		self.update_api_resources()
		self.validate_session()
		self.update_filters()
		self.logs = logs.MobileLog(self)

	def validate_session(self):

		credentials = self.get_credentials_info()
		if credentials.get("User-Id"):
			user =  frappe.db.get_value("User", {"user_id": credentials.get("User-Id")},
				fieldname=["name", "email", "name", "user_id"], as_dict=True)
			if not user:
				msg = _("Invalid user id")
				self.data.update({"msg": msg})
				raise werkzeug.exceptions.Unauthorized(self.request_handler.response)
			else:
				self.session = Session(user.get("email"))
				self.update_user_info(user.get("name"))	
		else:
			self.validate_user(credentials)

	def validate_user(self, credentials):
		self.validate_request()
		if not (credentials.get("usr") and credentials.get("pwd")):
			self.data.update({"msg": _("Username and Password are mandatory")})
			raise werkzeug.exceptions.Unauthorized(self.request_handler.response)
		else:
			try:
				check_password(credentials.get("usr"), credentials.get("pwd"))
				user = frappe.db.get_value("User", credentials.get("usr"), fieldname=\
					["first_name", "last_name", "email", "user_id", "name"], \
					as_dict=True)
				self.user_id = user.get("user_id")
				self.data.update({
					"msg": _("Logged In"),
					"user_info": user
				})
				self.update_user_info(user.get("name"))
			except frappe.AuthenticationError as e:
				self.data.update({"msg": _("Invalid User/Password")})
				raise werkzeug.exceptions.Unauthorized(self.request_handler.response)

	def update_device_info(self):
		self.device_info.update({
			"imei": self.kwargs.get("IMEI"),
			"device": self.kwargs.get("device"),
			"phone": self.kwargs.get("mobile"),	
		})
		self.data.update(self.device_info)

	def get_device_info(self):
		return self.device_info

	def update_headers(self):
		for header in frappe.request.headers:
			self.headers[header[0]] = header[1]	
	
	def update_user_info(self, user):
		doc = frappe.get_doc("User", user)
		temp_dict = utils.doc_to_dict(doc)
		self.user_info.update(temp_dict)
		self.update_employee_information()

	def update_employee_information(self):
		employee = frappe.db.get_value("Employee",{"user_id":self.user_info.get("name")},\
			   as_dict=True)
		if not employee:
			return
		doc = frappe.get_doc("Employee", employee.get("name"))
		doc_dict = utils.doc_to_dict(doc)
		self.employee_info.update(doc_dict)	
	
	def update_location_info(self):
		if not self.kwargs.get("location"):
			return False
		location = self.kwargs.get("location")
		self._location = geo_location.Location(location)
		self.location.update(self._location.location_dict)

	
	def update_api_resources(self):
		self.resources.update({
			"usr": self.kwargs.get("usr"),
			"pwd": self.kwargs.get("pwd"),
			"method": self.kwargs.get("method")
		})

	def update_filters(self):
		
		if self.kwargs.get("filters"):
			self.filters.update(self.kwargs.get("filters"))

	def get_filters(self):
		return self.filters

	def get_headers(self):
		return self.headers

	def get_credentials_info(self):
		headers = self.get_headers()
		if headers.get("User-Id"):
			self.credentials.update({
				"type": "session", 
				"User-Id": headers.get("User-Id")
			})
		else:
			self.credentials.update({
				"type": "user",
				"usr": self.kwargs.get("usr"),
				"pwd": self.kwargs.get("pwd")
			})
			
		return self.credentials	
	
	def get_user_info(self):
		return self.user_info
	
	def get_api_resources(self):
		return self.resources

	def get_location_info(self):
		return self.location

	def get_employee_info(self):
		return self.employee_info
	
	def validate_request(self):	
		resources = self.get_api_resources()
		if not resources.get("method") or (resources.get("method") and \
				resources.get("method") !=  "login"):
			raise werkzeug.exceptions.MethodNotAllowed(self.request_handler.response)	
		if resources.get("method") == "login":
			if frappe.local.request.method in ["GET", "DELETE", "PUT"]:
				raise werkzeug.exceptions.MethodNotAllowed(self.request_handler.response)


