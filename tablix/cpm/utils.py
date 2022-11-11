
'''
	Added by Sahil Saini
	Email sahil.saini@tablix.ae
'''
import frappe
from frappe.utils import flt, cint, cstr
import re
import json

def get_number(name=None):
	number = 1
	if not name:
		return number
	com = re.compile(r'[a-zA-Z]')
	lst = com.split(name)
	if lst:
		number = cint(lst[len(lst)-1])
	
	return number	
		
	
@frappe.whitelist()
def get_children(doctype, parent=None, is_root=None, company=None, fiscal_year=False, is_strategic=0, is_objective=0, is_indicator=0):
	
	data = frappe._dict()
	results =[]
	condition = ""
	if company:
		condition += " AND company=%(company)s "
	if fiscal_year:
		condition += " AND fiscal_year=%(fiscal_year)s "

	if is_root or not parent:
		results =  frappe.db.sql("""SELECT 1 AS is_strategic, name AS value, 1 AS expandable, select_series, \
			CONCAT_WS(' - ', name, title, fiscal_year, company, '<b>Theme</b>') AS title, 'Strategic Theme' AS  \
			doctype, name AS strategic_theme FROM `tabStrategic Theme` WHERE docstatus=0 %s
			ORDER BY priority """%(condition),{"company": company, "fiscal_year": fiscal_year}, as_dict=1)
		
	elif is_strategic == "1":
		results = frappe.db.sql("""SELECT 1 AS is_objective, name AS value, 1 AS expandable, select_series, \
			CONCAT_WS(' - ', name, title, '<b>Objective</b>') AS title, 'Strategic Objective' \
			AS doctype, strategic_theme, name AS strategic_objective FROM `tabStrategic Objective` \
			WHERE strategic_theme=%(theme)s ORDER BY name """, {"theme": parent},  as_dict=True)

	elif is_objective == "1":
		results = frappe.db.sql("""SELECT 1 AS is_indicator, name AS value, 0 AS expandable, select_series, \
			CONCAT_WS(' - ', name, strategic_owner_name, '<b>Indicator</b>') AS title, 'Indicator' AS doctype  FROM `tabIndicator`
				WHERE strategic_objective=%(objective)s ORDER BY name """, {"objective": parent},  as_dict=True)
	
	return results


@frappe.whitelist()
def add_child(doc, data):
	
	if doc and isinstance(doc, str):
		doc = json.loads(doc)
	if data and isinstance(data, str):
		data = json.loads(data)
	doc = frappe.get_doc(doc)
	doc.save()
	frappe.db.commit()
