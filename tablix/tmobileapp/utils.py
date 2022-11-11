
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr
from frappe.utils import datetime

KEYS_TO_DISCARD = ['cmd', 'usr', 'pwd', 'method']
DOC_KEYS_TO_DISCARD = ['parent', 'parenttype', 'parentfield', 'owner', 'creation', "idx",
                 'modified', "modified_by", 'doctype', 'docstatus', 'last_known_versions',
		'user_id','enabled', 'roles', 'role_profile_name']

def doc_to_dict(doc, memory=frappe._dict()):
	doc = doc.as_dict()
	for key, val in doc.iteritems():
		if key not in DOC_KEYS_TO_DISCARD:
			if val and isinstance(val, list):
				for item  in val:
					memory[key] = []
					if item and isinstance(item, dict):
						c_doc = frappe._dict()
						for c_key, c_val in item.iteritems():
							if c_key not in DOC_KEYS_TO_DISCARD:
								if val and not isinstance(c_val, str):
									c_doc[c_key] = cstr(c_val)
								else:
									c_doc[c_key] = c_val 
						memory[key].append(c_doc)
			else:
				if val and not isinstance(val, str):
					memory[key] = cstr(val)
				else:
					memory[key] = val

	return memory	

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%I:%M:%S"
DATETIME_FORMAT = "%Y-%m-%d %I:%M:%S"
def convert_obj_to_str(data):
	
	def _convert_obj_to_str(data):	
		temp = frappe._dict()
		for key, val in data.iteritems():
			if val and isinstance(val, str):
				temp[key] = val
				continue	
			if val and isinstance(val, datetime.date):
				temp[key] = val.strftime(DATE_FORMAT)
			if val and isinstance(val, datetime.datetime):
				temp[key]= val.strftime(DATETIME_FORMAT)
			if val and isinstance(val, datetime.time):
				temp[key] = val.strftime(TIME_FORMAT)
		return temp
	
	if(data and isinstance(data, list)):
		results = []
		for item in data:
			if item and isinstance(item, dict):
				results.append(_convert_obj_to_str(item))
		return results

	elif(data and isinstance(data, dict)):
		return _convert_obj_to_str(data)
