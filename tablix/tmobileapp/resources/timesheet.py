

'''
	Developer Sahil Saini
	Email sahil.saini@tablix.ae
'''

'''
	THESE API's are only valid for Specific Android Phone App

	DATE_FORMAT = "YYYY-MM-DD"

'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import flt, cint, cstr, nowdate
from tablix.utils import get_string_datetime, get_week_start_end_date


'''
	Get user Current Day Total
'''
def get_day_total(rh, user_info, employee_info, *args, **kwargs):
	
	data  =  frappe._dict({"total": 0.0, "more_info":[]})
	if user_info:
		filters = {"employee": employee_info.get("name"), "today": nowdate()}
		results  = frappe.db.sql("""SELECT TD.hours, TD.project, TD.task FROM `tabTimesheet` T INNER JOIN \
			`tabTimesheet Detail` TD ON T.name=TD.parent  WHERE T.employee=%(employee)s AND \
			T.start_date=%(today)s """, filters, as_dict=True)
		for item in results:
			data.total += flt(item.get("hours"))
		data.more_info = results

	return data
		

'''
	Get User Current Week Total
'''
def get_weekly_total(rh, user_info, employee_info, *args, **kwargs):

	start_date, end_date = get_week_start_end_date(is_date=False)
	data = frappe._dict({"weekly_total":0.0, "more_info": []})
	if user_info:
		filters = {"employee": employee_info.get("name"), "start_date": start_date, "end_date": end_date}
		results = frappe.db.sql(""" SELECT TD.hours, TD.project, TD.task FROM `tabTimesheet` T INNER JOIN \
			`tabTimesheet Detail` TD ON T.name=TD.parent WHERE (TD.modified BETWEEN %(start_date)s AND 
			 %(end_date)s ) AND T.employee=%(employee)s """, filters, as_dict=True)

		for res in results:
			data.weekly_total += flt(res.get("hours"))
		data.more_info = results
	return data


'''
	Get User Task List
'''
def get_task_list(rh, user_info, employee_info, *args, **kwargs):

	data = []
	if user_info:
		filters = {"user": user_info.get("name"),  "today": nowdate()}
		data = frappe.db.sql(""" SELECT T.subject, T.description, T.priority, T.task_type, T.project FROM `tabTask` T \
				WHERE T.status='Open' AND  T.exp_start_date=%(today)s AND T.assigned_to=%(user)s """, \
				filters, as_dict=True)
	return data


'''
	Get Project total
'''

def get_customer_weekly_total(rh, user_info, employee_info, *args, **kwargs):
	
	data = []
	if user_info:
		weekly_total =  get_weekly_total(rh, user_info, employee_info)
		temp = frappe._dict()
		for info in weekly_total.get("more_info"):
			if not temp.has_key(info.get("project")):
				temp[info.get("project")] = frappe._dict({
							"total": 0.0, "project": info.get("project"), 
							"customer": ""
						})
					
			project = temp.get(info.get("project"))
			project.total += flt(info.get("hours"))
		for key, val in  temp.iteritems():
			data.append(val)

	return data




'''
	GET Employee Day of Information
'''
def get_holidays_info(rh, user_info, employee_info, *args, **kwargs):
	
	data = frappe._dict({"holiday": 0.0, "sick": 0.0, "vocation": 0.0, "more_info": []})
	if user_info:
		pass

	return data



'''
	GET Pay Period Info
'''
	
def my_payment_info(rh, user_info, employee_info, *args, **kwargs):
	data = frappe._dict()

	if user_info:
		pass

	return data
