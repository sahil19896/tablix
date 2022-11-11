
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr
import json
import re

class Location:
	
	def __init__(self, raw_location):
		self.keys = []
		self.values = []
		self.location_dict = frappe._dict()
		self.raw_location= raw_location
		if raw_location:
			self.parse_raw_location()

	def parse_raw_location(self):
		regex  = re.compile("(\w+)=")
		addrline = re.compile("\]|\[|0\:|\"|\'")
		raw_data = self.raw_location
		keys = regex.findall(raw_data)
		for idx, val in enumerate(regex.split(raw_data)):
			if idx == 0:
				continue
			if val in keys:
				key = val.lower()
				continue
			temp = addrline.sub("", val)	
			if temp.rfind(",") == len(temp)-1:
				temp = temp[0:len(temp)-1]	
			self.location_dict[key] = temp
			
	def get_val(self, key):
		if self.location_dict.has_attr(key):
			return self.location_dict.get(key)
