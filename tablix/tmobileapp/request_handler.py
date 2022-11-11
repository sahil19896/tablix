
import frappe
from frappe.utils import flt, cint, cstr
from tablix.toauth.login_manager import LoginManager
import resources #resources from current directory
from frappe.utils.response import Response
import json
import werkzeug.exceptions
import exceptions
from frappe.utils.logger import get_logger

class RequestHandler:
	
	def __init__(self, *args, **kwargs):
		self.logger = get_logger("tmobileapp")
		self.logger.info("Request Initialize")
		self.response = Response()
		self.login_status = True
		self.user_data =  frappe._dict()
		try:
			self.login_manager = LoginManager(self, *args, **kwargs)
		except werkzeug.exceptions.Unauthorized as e:
			self.login_status = False
	
		self.handle_request(*args, **kwargs)

	def handle_request(self, *args, **kwargs):
		self.data = self.login_manager.data
		method = self.login_manager.resources.get("method")
		self.update_info()
		try:
			if method and hasattr(resources, method):
				user_info = self.login_manager.get_user_info()
				emp_info = self.login_manager.get_employee_info()
				self.data.update({"results": getattr(resources, method)(self, user_info, emp_info)})
				

		except werkzeug.exceptions.MethodNotAllowed as e:
			print(frappe.get_traceback())
	
		self.update_response()

	def update_response(self):
		self.response.mimetype = "application/json"
		self.response.chartset = "utf-8"
		self.response.headers.add_header("User-Id", self.login_manager.user_id)
		try:
			self.response.data = json.dumps(self.data)
		except ValueError as e:
			print("Error while updating response")

	def update_info(self):
	
		self.data.update({
				"user_info": self.login_manager.user_info, 
				"employee_info": self.login_manager.employee_info

		})

