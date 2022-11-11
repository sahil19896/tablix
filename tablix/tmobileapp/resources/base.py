
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt

class QueryBuilder:
	
	def __init__(self, rh):
		self.query = ""
		self.filters = frappe._dict()
		self.rh = rh
		self.update_filters()
		self.build_query()

	def build_query(self):
		fields  = self.get_fields		

	def update_filters(self):
		pass

	def get_query(self):
		
		return self.query


	def get_filters(self):
		return self.filters


