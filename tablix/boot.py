
import frappe 
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt
from .tgeo.utils import get_geo_setting




def update_boot(boot):

		
	data = frappe._dict({
		"rejected_states": get_rejected_states(),
		"approved_states": get_approved_states(),
		"tablix_setting": get_tablix_setting(),
		"geo": get_geo_setting(),
		"sales": get_bdms_and_managers(),
		"tdashboard": get_tdashboard_setting(),
		"employee": get_employee_info(),
	})

	boot.update({"tablix":data})



def get_rejected_states():
	
	states = frappe.db.sql(""" SELECT name FROM `tabWorkflow State`  WHERE name LIKE '%Disapproved%' """, as_dict=True)
	data  = []
	for state in states:
		data.append(state.get("name"))
	return data

def get_approved_states():
	
	states = frappe.db.sql(""" SELECT name from `tabWorkflow State` WHERE name LIKE '% Approved' """, as_dict=True)
	data = []
	for state in states:
		data.append(state.get("name"))
	return data


def get_tablix_setting():

	doc = frappe.get_doc("Tablix Setting", "Tablix Setting")
	_temp = doc.as_dict()
	_temp.update({

		"taxes_accounts": [item.get("tax_account") for item in doc.get("taxes_accounts")],
		"duties_accounts":  [item.get("other_charges_account") for item in doc.get("other_charges_accounts")]
	})	

	return _temp

def get_bdms_and_managers():
	
	meta = frappe.get_meta("Opportunity")
	data = frappe._dict({
		"bdms": [],
		"managers":[]
	})
	if meta.get_field("bdm"):
		data.update({"bdms": meta.get_field("bdm").options.splitlines()})
	if meta.get_field("account_manager"):
		managers = data.update({"managers": meta.get_field("account_manager").options.splitlines()})
	
	return data	


def get_metabase_setting():
	
	return frappe.get_doc("Metabase Setting", "Metabase Setting").as_dict()

def get_tdashboard_setting():
	
	doc = frappe.get_doc("TDashboard Setting", "TDashboard Setting").as_dict().copy()

	colors = []
	for color in doc.get("monthly_colors"):
		colors.append(color.get("color"))
	doc['colors'] = colors
	return doc
		

def get_employee_info():
	
	emp_info  = frappe.db.get_value("Employee", {"user_id": frappe.session.user},\
		["name", "employee_name"], as_dict=True)	
	return emp_info


