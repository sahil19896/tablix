
import frappe
import tablix
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr
import os
import json
import sys
from functools import wraps
import importlib
from frappe.utils.response import Response


def dashboard_handler(f):

	def get_module(page_name):
		temp_page_name = page_name.replace("-", "_")
		app_path = frappe.get_app_path("tablix")
		dashboard_path = ""
		for path in frappe.get_hooks("dashboard_path"):
			temp = "{0}/{1}/{2}/{2}.py".format(app_path, path, temp_page_name)
			if os.path.exists(temp):
				dashboard_path = "tablix.{0}.{1}.{1}".format(path, temp_page_name).replace("/", ".")
				break
		try:
			module = importlib.import_module(dashboard_path)
			return module	
		except ImportError as e:
			print(frappe.get_traceback())

	@wraps(f)
	def wrapper(*args, **kwargs):
		filters = kwargs.get("filters")
		page_name = kwargs.get("page_name")
		page = get_module(page_name)

		return f(filters=filters, page_name=page_name, page=page)
	return wrapper

@frappe.whitelist()
@dashboard_handler
def get_data(filters=None, page_name=None, page=None):
	
	results = frappe._dict()
	if hasattr(page, "get_dashboard_data"):
		if filters and isinstance(filters, str):
			filters = json.loads(filters)
		results.update({"results": page.get_dashboard_data(filters)})
	
		
	return convert_to_response(results)



def convert_to_response(data):
	response = Response()
	response.chartset = "utf-8"
	response.mimetype = "application/json"
	response.data = json.dumps(data, separators=(',',':'))
	return response	
	
