
import frappe
from frappe import _, msgprint, throw
from frappe.utils import flt, cint, cstr
import utils

def get_project_details(rh, user_info, emp_info, *args, **kwargs):

	data = frappe._dict()
	results = utils.get_project_tasks(user_info, emp_info, today=False)
	
	return results	


'''
def get_project_tasks(rh, user_info, empl_info, *args, **kwargs):
	
	data = []
	filters = rh.login_manager.get_filters()
	fields = filters.get("fields")
	if  filters:
		conditon =  ""
		rh.login_manager.get_condition()

		condition += " WHERE T.project=%(project)s AND T.assigned_to=%(user)s AND T.status=%(status)s  "
				FROM `tabTask` {0}""".format(condtion), filters, )

	return data	
'''	
