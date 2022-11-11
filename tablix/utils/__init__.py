
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt, datetime, today
from calendar import monthrange
import calendar

def get_service_groups():

	setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	return [service.get("name") for service in setting.get("service_groups")]



def get_po_sales_order():
	
	setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	return [so.get("name") for so in setting.get("si_sales_order")]




def get_si_sales_order():
	setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	return [so.get("name")  for so in setting.get("si_sales_order")]



def get_default_uom():

	return frappe.get_doc("Tablix Setting", "Tablix Setting").get("default_uom")

def get_setting():
	
	return frappe.get_doc("Tablix Setting", "Tablix Setting")


def send_mail(template, employee_name, desgination, user_id, no):

	html = template.render({"employee_name": employee_name, "designation": designation, "uesr_id":user_id, "no":no})

	frappe.sendmail(recipients = cust_email_id,
                        subject=_("{0}/ Opportunity-{1}").format(self.name, self.project_name),
			cc = [self.bdm],
			message=_("{0}").format(html),
			reply_to= self.bdm
	)
	

'''
	Get all email from database
'''
def get_email(designation):
	
	email = frappe.db.get_value("Employee", filters={"designation":designation}, fieldname="user_id", as_dict=True)
	email =  email if email else {}
	return email.get("user_id")

	


'''
	Email Approval Email Template
'''
def get_status_template(doc, subject, customer, message, email_from, _email_to, designation=None, url=None):

	doctype = doc.get("doctype")
	docname = doc.get("docname")
	url = get_link_to_form(self.doctype, self.name) if url	else None
	template = frappe.get_template("status_template")
	msg = template.render({"doctype":doctype, "subject":subject, "customer":customer, "message": message, \
			"designation": designation, "docname":name, "link":url})

	return msg



'''
	Get Date time in string format
'''
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
def get_string_datetime(str_format=None):

	frmt = DATETIME_FORMAT if not str_format else str_format
	cur_datetime = frappe.utils.now_datetime()
	return cur_datetime.strftime(frmt)



'''
	Get all emails
'''
def get_all_emails(setting=None):
	
	if not setting:
		setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	
	emails =  {}
	for email in setting.get("emails"):
		emails[email.get("designation")] =  email.get("user_id")	
	return frappe._dict(emails)




def update_emp_leave(doc, method):

	emp = frappe.get_doc("Employee", doc.get("employee"))
	if method == "on_cancel":
		emp.total_leaves_consumed -= flt(doc.total_leave_days)
		emp.balance_leave = flt(emp.total_leaves_allocated) - flt(emp.total_leaves_consumed)
			
	elif method == "on_submit" and doc.status == "Approved":
		emp.total_leaves_consumed += flt(doc.total_leave_days)
		emp.balance_leave = flt(emp.total_leaves_allocated) - flt(emp.total_leaves_consumed)
	
	emp.save()
	doc.total_leaves_left = emp.balance_leave
	frappe.db.commit()





'''
	Convert Standard datetime MySQL datetime
'''
IN_DATE = "%d-%m-%Y"
OUT_DATE = "%Y-%m-%d"
OUT_FORMAT = "%Y-%m-%d %H-%M-%S.%f"
IN_FORMAT = "%d-%m-%Y %H:%M:%S"
def format_datetime(dt_str, out_frmt=None, in_frmt=None):
	
	global OUT_FORMAT, IN_FORMAT
	out_frmt =  OUT_FORMAT if not out_frmt else out_frmt
	in_frmt = IN_FORMAT if not in_frmt else in_frmt
	dt_obj = datetime.datetime.strptime(dt_str, in_frmt)
	return dt_obj.strftime(out_frmt)

'''
	Convert String Datetime to Standard Python
	Datetime Object
'''
def get_datetime(str_datetime, for_doctype=False, dtfrmt=None):
	frmt = OUT_FORMAT
	if for_doctype:	
		frmt = "%Y-%m-%d %H:%M:%S.%f"
	if dtfrmt:
		frmt =dtfrmt
	return datetime.datetime.strptime(str_datetime, frmt) 

'''
	Get Mysql Date only format

'''
def get_date(datestr, frmt=None, is_string=False, is_date=False):

	if not frmt:
		frmt = IN_DATE
	temp = datestr
	if  isinstance(datestr, str):
		temp = datetime.datetime.strptime(datestr, frmt)
	if is_string:
		temp = temp.strftime(OUT_DATE)

	if is_date and isinstance(temp, datetime.datetime):
		return  temp.date()
	return temp


TIME_FORMAT = "%H:%M:%S"
'''
	Get Time
'''

def get_time(timestr, frmt=None, is_string=False):
	temp = None
	if not frmt:
		frmt = TIME_FORMAT
	if timestr and isinstance(timestr, str):
		temp = datetime.datetime.strptime(timestr, frmt)

	return temp.time() if temp else None	
		

'''
	Get Date format in SQL date format
'''
def format_date(datestr):
	return datetime.datetime.strptime(datestr, IN_DATE)

'''
	Get  first and Last date of the month
	This is the system based format date
'''
def get_first_last_date(date=None, frmt=None, is_string=False, start_of_month=False):
	
	frmt = IN_DATE if not frmt else frmt
	if not date:
		date = datetime.datetime.strptime(today(), OUT_DATE)
		date = datetime.datetime(date.year, date.month, 1)
	else:
		date = datetime.datetime.strptime(date, frmt)
	if start_of_month:
		date = datetime.datetime(date.year, date.month, 1)
	days = monthrange(date.year, date.month)[1]
	next_date = datetime.datetime(date.year, date.month, days)
	
	if is_string:
		date = date.strftime(IN_DATE)
		next_date = next_date.strftime(IN_DATE)

	return [date, next_date]

'''
	Get Next month
'''
def get_next_month(date):

	if date:
		days = monthrange(date.year, date.month)[1]
		date = date + datetime.timedelta(days)
		return date		


'''

	Get Time diff in minutes
'''
def get_time_diff(from_hrs, to_hrs, in_minutes=False, in_hours=False):

	diff = 0
	tdelta = frappe.utils.time_diff(from_hrs, to_hrs)
	diff = tdelta.total_seconds()
	if in_minutes:
		diff = tdelta.total_seconds()/60
	if in_hours:
		diff = flt(tdelta.total_seconds()/60)/60
	
	return diff
	

'''
	Get Week Start and End Date 
'''
WEEK_MAP = {
	'Sun': 6, 'Mon': 0, 'Tue':1,
	'Web':2,'Thu':3, 'Fri':4,
	'Sat':5,
}

def get_week_start_end_date(is_str=True, is_date=True):
	setting = frappe.get_doc("Time and Attendance Setting", "Time and Attendance Setting")
	start_week_day = WEEK_MAP.get(setting.get("week_start_day"))
	end_week_day = WEEK_MAP.get(setting.get("week_end_day"))
	temp_today  = frappe.utils.now_datetime()
	cur_week_day = temp_today.weekday()
	diff = start_week_day - cur_week-day if cur_week_day > start_week_day else 6-start_week_day +1

	start_date = datetime.datetime.today() - datetime.timedelta(days=diff)
	end_date =  start_date + datetime.timedelta(days=setting.get("total_days"))
	
	if is_date:
		start_date = start_date.strftime(OUT_DATE) if is_str else start_date.date()
		end_date = end_date.strftime(OUT_DATE) if is_str else end_date.date()
	else:
		start_date = start_date.strftime(DATETIME_FORMAT) if is_str else start_date
		end_date = end_date.strftime(DATETIME_FORMAT) if is_str else end_date

	return [start_date, end_date]

	
'''
	Get Month First and Last Date
'''
def get_month_first_and_last_date(curr_month=True, month_year=(), is_str=True, is_date=True):

	if not curr_month and not month_year:
		frappe.throw(_("Please pass Month year tuple as second argument"))
	
	temp = frappe.utils.now_datetime() if curr_month else frappe.utils.datetime.datetime(month_year[0], month_year[1], 1)
	temp = frappe.utils.datetime.datetime(temp.year, temp.month, 1)
	start_date, end_date = None, None
	if is_date:
		end_date = temp +  datetime.timedelta(days=monthrange(temp.year, temp.month)[1]-1)
		end_date = end_date.date().strftime(OUT_DATE) if is_str else end_date.date()
		start_date = temp.date().strftime(OUT_DATE) if is_str else temp.date()
	else:
		end_date = temp +  datetime.timedelta(days=monthrange(temp.year, temp.month)[1]-1)
		end_date = end_date.strftime(DATETIME_FORMAT) if is_str else end_date
		start_date = temp.strftime(DATETIME_FORMAT) if is_str else temp
		
	return [start_date, end_date]

def get_base_server_address():
	print(frappe.local.request.headers)
	
