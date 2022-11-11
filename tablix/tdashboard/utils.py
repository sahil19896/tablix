

import frappe
from frappe import _, msgprint, throw
from frappe.utils import datetime, now_datetime, today, cint, flt, cstr
from datetime import timedelta
import calendar
def get_category_list():

	categories = [cat.get("category") for cat in frappe.db.sql("""SELECT category_of_failure \
			as category FROM `tabIssue` GROUP BY category_of_failure """, as_dict=True)]
	return categories


DATE_FORMAT = "%Y-%m-%d"
# GET Current and Previous fiscal year Date

def get_prev_and_cur_quarter_dates(filters):
	months = 1
	cur_date = now_datetime()
	start_data = end_data = ""
	fiscal_year = cint(filters.get("fiscal_year"))
	quarter = cint(filters.get("quarter")) 
	if not fiscal_year:
		fiscal_year = cur_date.year
	if not quarter:
		if cur_date.month >= 1 and cur_date.month <= 3:
			quarter = 1
		elif cur_date.month >= 3 and cur_date.month <= 6:
			quarter = 2
		
		elif cur_date.month >= 7 and cur_date.month <= 9:
			quarter = 3
		
		elif cur_date.month >= 10 and cur_date.month <= 12:
			quarter = 4
		
	d_format = "%Y-%m-%d"
	data = "{0}-{1}-{2}"
	if quarter == 1:
		start_date = data.format(fiscal_year-1, 10, 31)
		end_date = data.format(fiscal_year, 3, 31)	
	elif quarter == 2:
		start_date = data.format(fiscal_year, 1, 31)
		end_date = data.format(fiscal_year, 6, 30)		
	elif quarter == 3:
		start_date = data.format(fiscal_year, 4, 30)
		end_date = data.format(fiscal_year, 9, 30)		
	elif quarter == 4:
		start_date = data.format(fiscal_year, 6, 30)
		end_date = data.format(fiscal_year, 12, 31)		

	start_date = datetime.datetime.strptime(start_date, d_format)
	end_date = datetime.datetime.strptime(end_date, d_format)
	return {
		"start_date": start_date.strftime(DATE_FORMAT),
		"end_date": end_date.strftime(DATE_FORMAT),
		"_format": "%Y-%b"	
	}

#GET Previous and Current Weeks Date
def get_prev_and_cur_week_dates(filters):
	start_date = end_date = ""
	week = cint(filters.get("week"))
	fiscal_year = 0
	_format = "%Y-W%W-%w"
	cur_date = now_datetime()
	if filters.get("fiscal_year"):
		fiscal_year = cint(filters.get("fiscal_year"))
	else:
		fiscal_year = cur_date.year
		
	if week:
		week = cint(filters.get("week"))
		cur_date = cur_date.strptime("{0}-W{1}-0".format(fiscal_year, week), _format)
		if cur_date.isoweekday() > 0:
			cur_date  = cur_date - timedelta(days=cur_date.isoweekday())	
	else:
		if cur_date.isoweekday() > 0:
			cur_date = cur_date - timedelta(days=cur_date.isoweekday())		
	print(cur_date)	
	end_date = cur_date + timedelta(days=6)
	start_date = cur_date - timedelta(days=7)
	return {
		"start_date": start_date.strftime(DATE_FORMAT),
		"end_date": end_date.strftime(DATE_FORMAT),
		"_format": "%Y-%U"
	}

# GET Previous Month and Current month Date
def get_prev_and_cur_month_dates(filters):
	cur_date = now_datetime()
	start_date = end_date = ""
	_format = "%Y-%b-%d"
	fiscal_year = cint(filters.get("fiscal_year"))
	month = filters.get("month")

	if not fiscal_year:
		fiscal_year = cur_date.year
	if not month:
		_format = "%Y-%m-%d"
		month = cur_date.month
	
	data = "{0}-{1}-{2}".format(fiscal_year, month, 1)
	end_date = cur_date.strptime(data, _format)
	total_days = calendar.monthrange(fiscal_year, end_date.month)
	end_date = end_date.replace(end_date.year, end_date.month, total_days[1])
	prev_month = end_date - timedelta(days=45) #Go to prev montih
	total_days = calendar.monthrange(prev_month.year, prev_month.month)
	data = "{0}-{1}-{2}".format(prev_month.year, prev_month.month, 1)
	start_date = datetime.datetime.strptime(data, "%Y-%m-%d")
	return {
		"start_date": start_date.strftime(DATE_FORMAT),
		"end_date": end_date.strftime(DATE_FORMAT),
		"_format": "%Y-%M"
	}


# GET all weeks in Fiscal Year
def get_all_fiscal_weeks(fiscal_start_end):
	weeks = []
	start_date = fiscal_start_end.get("year_start_date")
	end_date = fiscal_start_end.get("year_end_date")
	weekday = cint(start_date.isoweekday())
	temp = None
	if weekday > 0:
		days = 6 - weekday
		temp = start_date + timedelta(days=days)
	else:
		temp = start_date + timedelta(days=6)

	weeks.append({"start_date": start_date, "end_date": temp,
			"week": cint(start_date.strftime("%U"))})	 		
		
	while((temp + timedelta(days=7)) < end_date):
		start_date = temp + timedelta(days=1)
		temp = temp+timedelta(days=7)
		weeks.append({"start_date": start_date, "end_date": temp,
			"week": cint(start_date.strftime("%U")) })

	if(temp < end_date):
		start_date = temp+timedelta(days=1)
		days = calendar.monthrange(cint(end_date.strftime("%Y")), cint(end_date.strftime("%m")))[1]
		days = days - cint(start_date.strftime("%d"))			
		if days > 0:
			weeks.append({"start_date": start_date, "week":	start_date.strftime("%U"),
				"end_date": start_date+timedelta(days=days)})
	return weeks

# Get all quarters for Fiscal Year
def get_all_fiscal_quarters(fiscal):
	quarters = []
	start_date = fiscal.get("year_start_date")
	end_date = fiscal.get("year_end_date")
	temp = start_date
	for idx in range(1, 5):
		temp = start_date
		for jdx in range(0, 3):
			days = calendar.monthrange(cint(temp.strftime("%Y")), \
				cint(temp.strftime("%m")))[1]
			temp = temp + timedelta(days=days)
		
		quarters.append({"start_date": start_date, "end_date": temp-timedelta(days=1)})
		start_date = temp
	
	return quarters	
