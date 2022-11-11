
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr, now_datetime
from tablix.tdashboard.utils import get_category_list

DATE_FORMAT = "%Y-%m-%d"

def get_dashboard_data(filters={}):
	return get_data(filters, with_map=True)
	
def get_data(filters, with_map=False):
	
	if not filters.get("fiscal_year"):
		frappe.throw(_("Please select <b>Fiscal Year</b>"))
	fiscal_year = frappe.get_doc("Fiscal Year", filters.get("fiscal_year"))
	filters.update({
		"start_date":fiscal_year.get("year_start_date").strftime(DATE_FORMAT),
		"end_date": fiscal_year.get("year_end_date").strftime(DATE_FORMAT),
		"month_format": "%b",
	})
	condition = ""
	if filters.get("project_site"):
		condition += " AND proj_site=%(project_site)s "

	results  = frappe.db.sql("""SELECT *, IFNULL(category_of_failure, '') as failure_cat, CONCAT(opening_date, ' ', opening_time) as opening_datetime, \
			TIME_TO_SEC(TIMEDIFF(modified, creation))/3600 AS open_close_time, \
			TIME_TO_SEC(TIMEDIFF(rectification_datetime, attended_datetime))/3600 AS rectified_time, \
			DATE_FORMAT(opening_date, %(month_format)s) AS month from `tabIssue`  WHERE status=%(status)s \
			AND opening_date BETWEEN %(start_date)s AND %(end_date)s  {condition} ORDER BY creation ASC""".format(condition=condition),\
			filters, as_dict=True)


	if with_map:
		return get_data_map(results)

	return results

def get_data_map(results):
		
	category_map  = {}
	for cat in get_category_list():
		if cat is None:
			continue
		category_map[cat.upper()]=0.0;

	month_wise_data_map = frappe._dict()
	for res in results:
		if not month_wise_data_map.has_key(res.get("month")):
			month_wise_data_map[res.get("month")] = get_default_dict(res.get("month"), category_map)
		month_wise_data_map[res.get("month")]['total'] += 1
		update_hourly_data(res, month_wise_data_map)
		update_category_wise_data(res, month_wise_data_map)

	sorted_list = get_sorted_data(month_wise_data_map, category_map)
	return sorted_list

def update_hourly_data(res, month_wise_data_map):

	hourly = month_wise_data_map.get(res.get("month")).get("hourly")
	if res.get("open_close_time") <= 2.0:
		hourly["Less than two hours"] += 1
	
	elif res.get("open_close_time") > 2.0 and res.get("open_close_time") <= 4.0:
		hourly['2-4'] += 1
		
	elif res.get("open_close_time") > 4.0 and res.get("open_close_time") <= 16.0:
		hourly['4-16'] += 1
		
	elif res.get("open_close_time") > 16.0 and res.get("open_close_time") <= 24.0:
		hourly['16-24'] += 1

	elif res.get("open_close_time") > 24.0:
		hourly['>24'] += 1

def update_category_wise_data(res, month_wise_data_map):
	
	category = month_wise_data_map.get(res.get("month")).get("category")
	
	if not category.has_key(res.get("failure_cat")) :
		category[res.get("failure_cat")] = 0.0

	category[res.get("failure_cat")] += 1	

def get_sorted_data(month_wise_data_map, categories_map):
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
		  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

	for month, data in month_wise_data_map.items():
		months[months.index(month)] = data	

	sorted_months = []
	for month in months:
		if isinstance(month, str):
			monthly_item = get_default_dict(month, categories_map)
			sorted_months.append(monthly_item)
		else:
			sorted_months.append(month)

	return sorted_months			

def get_default_dict(month, categories_map):
	return frappe._dict({
		"total": 0.0, "category": frappe._dict(),
		"month": month,
		"hourly": frappe._dict({"Less than two hours":0.0, 
		"2-4":0.0, "4-16":0.0, "16-24": 0.0, ">24":0.0})
	})
