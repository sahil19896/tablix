
import frappe
import json
from frappe import _
from frappe.utils import flt, cint,  cstr
from tablix.tmobileapp.request_handler import RequestHandler
from functools import wraps
import json

def resource_wrapper(func):

	def validate_payload(*args, **kwargs):
		if not kwargs.get("data"):
			return 
		data = kwargs.get("data")
		try:
			if isinstance(data, str):
				data = json.loads(data)
		except ValueError as e:
			print(frappe.get_traceback())
		
	@wraps(func)
	def wrapper(*args, **kwargs):
		validate_payload(*args, **kwargs)
		return func(*args, **kwargs)
	return wrapper

@frappe.whitelist(allow_guest=True)
@resource_wrapper
def request_handler(*args, **kwargs):
	try:
		login_manager = RequestHandler(*args, **kwargs)	
		return login_manager.response
	except Exception as e:
		print(frappe.get_traceback())
