
import frappe
from frappe import _, msgprint, throw
from frappe.utils import flt, cint, cstr, nowdate, now_datetime,  datetime


def get_project_tasks(user_info, employee_info, today=True, status='Open'):
	user = user_info.get("name")
	emp = employee_info.get("name")
	filters = frappe._dict({"user": user, "emp": emp, "status": status})
	condition = ""
	if today:
		filters.update({"today": nowdate()})
		condition += " AND T.exp_start_date=%(today)s "
	else:
	
		current  =  now_datetime()
		today = current.strftime("%Y-%m-%d")
		week_before = current + datetime.timedelta(days=-7)
		condition  += " AND T.exp_start_date BETWEEN %(week_before)s AND %(today)s "
		filters.update({"today": today, "week_before": week_before.strftime("%Y-%m-%d")})

	tasks = frappe.db.sql("""SELECT T.description, T.subject, T.name, T.project, T.assigned_to, P.location \
			FROM `tabProject` P INNER JOIN `tabTask` T ON P.name=T.project WHERE T.assigned_to=%(user)s \
			AND T.project IS NOT NULL AND T.status=%(status)s {0} """.format(condition), filters, as_dict=True)

	data = frappe._dict()
	for task in tasks:
		if not data.has_key(task.get("project")):
			temp = frappe._dict()
			locations  = frappe.db.sql("""SELECT SLI.location_name FROM `tabSite Location Item` SLI WHERE SLI.parent=%(parent)s""", 
					{"parent": task.get("location")}, as_dict=True)
			temp.update({"locations": locations, "tasks": [], "project": task.get("project")})	
			data[task.get("project")] = temp
		temp = data.get(task.get("project"))
		temp.tasks.append({"subject": task.get("subject"), "name": task.get("name")})
		
	return data

