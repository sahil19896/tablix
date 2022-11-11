'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr
from tablix.utils import get_date, get_next_month


def get_dashboard_data(filters=None):
	data = frappe._dict()
	validate_filters(filters)
	bdms_managers= get_acc_manager_and_bdms()
	fiscal_year_dates = get_start_end_date(filters.get("fiscal_year"))
	data, total = get_data(filters, bdms_managers, fiscal_year_dates)
	data = parse_tuple_to_string(data)
	labels = get_labels(filters, bdms_managers)
	return frappe._dict({
		"data": data,
		"labels": labels,
		"total": total,
		"vaxis": {"title": "Sale Rate"},
		"haxis": {"title": filters.get("report_type").replace("ly", "")}
	})	


def parse_tuple_to_string(data):
	
	parsed_data =  frappe._dict()
	for key, val in data.items():
		temp = "|"
		if key and isinstance(key, tuple):
			temp = temp.join(key)
		parsed_data[temp] = val

	return parsed_data 

def get_labels(filters, bdms_managers):
	bdms = [filters.get("report_type")]
	managers = [filters.get("report_type")]
	if filters.get("bdm"):
		bdms.append(filters.get("bdm"))
	else:
		temp = sorted([ bdm for bdm in bdms_managers.get("bdms") if bdm != ""])
		bdms += temp
	if filters.get("manager"):
		managers.append(filters.get("manager"))
	else:
		temp = ([manager for manager in bdms_managers.get("managers") if manager != ""])
		managers += temp

	return frappe._dict({"bdms": bdms, "managers": managers})

def get_data(filters, bdms_managers, fiscal_year_dates):
	
	condition = get_condition(filters)
	temp_filters = filters
	filters.update({
		"start_date": fiscal_year_dates.get("start_date"),
		"end_date": fiscal_year_dates.get("end_date")
	})
	opportunities = frappe.db.sql("""SELECT OPP.name, OPP.bdm, OPP.account_manager, OPP.owner, \
			OPP.tablix_status, OPP.boq AS project, OPP.is_amc AS amc, OPP.customer_name, \
			OPP.transaction_date FROM `tabOpportunity` OPP %s """%(condition),  filters, \
			as_dict=True)
	
	quotations = get_quotations(opportunities)
	sales_orders = get_sales_orders(quotations)
	return update_data(opportunities, quotations, sales_orders, filters, 
					fiscal_year_dates, bdms_managers)

def get_quotations(opportunities):
	quotations = []
	if not opportunities:
		return quotations

	filters = {}
	filters.update({"opportunities": tuple([item.get("name") for item in opportunities])})
	condition = " AND opportunity_quotation IN %(opportunities)s "
	quotations = frappe.db.sql("""SELECT QT.name AS quotation, QT.base_grand_total,\
			QT.opportunity_quotation AS opportunity,  QT.solution FROM `tabQuotation` QT
			WHERE QT.docstatus<2 %s """%(condition), filters, as_dict=True)
	return quotations

def get_sales_orders(quotations):
	
	sales_orders = []
	filters = {}
	condition = " AND SO.quotation_ref IN %(quotations)s "
	filters.update({"quotations": tuple([item.get("quotation") for item in quotations])})
	if not filters.get("quotations"):
		return sales_orders
	sales_orders = frappe.db.sql("""SELECT SO.name, SO.quotation_ref AS quotation, \
			SO.base_grand_total, SO.customer FROM  `tabSales Order` SO  WHERE SO.docstatus=1 \
			%s """%(condition), filters, as_dict=True)

	return sales_orders

def update_data(opportunities, quotations, sales_orders, filters, fiscal_year_dates, bdms_managers):
	results = []
	total = frappe._dict({
			"amount": frappe._dict({"so":0.0, "opp": 0.0, "qt": 0.0}),
			"number": frappe._dict({"so":0.0, "opp": 0.0, "qt": 0.0}),
					
		})
	report_types = get_report_types(fiscal_year_dates)
	
	data = frappe._dict(report_types.get(filters.get("report_type")))
	update_bdms_and_managers(data, bdms_managers, filters)
	
	for opp in opportunities:
		temp = frappe._dict(opp)
		update_total_and_record(opp, quotations, sales_orders, temp, total)
		update_record(temp, filters, data)
		results.append(temp)
	
	return data, total

def update_record(temp, filters, data):
	str_date = temp.get("transaction_date").strftime("%b-%Y")
	quotes  = temp.get("qt")  if temp.get("qt") else []
	sales_orders = temp.get("so") if temp.get("so") else []
	bdms =  (tuple([report_type, val])  for report_type, val in data.items() \
			if str_date in report_type).next()
	bdm = data[bdms[0]].get("bdms").get(temp.get("bdm"))
	manager = data[bdms[0]].get("managers").get(temp.get("account_manager"))
	for so in sales_orders:
		if bdm and bdm.has_key("so"):
			bdm.so += flt(so.get("base_grand_total"))
		if manager and manager.has_key("so"):
			manager.so += flt(so.get("base_grand_total"))
	for qt in quotes:
		if bdm and bdm.has_key("qt"):
			bdm.qt += flt(qt.get("base_grand_total"))
		if manager and manager.has_key("qt"):
			manager.qt += flt(qt.get("base_grand_total"))

	
def update_total_and_record(opp, quotations, sales_orders, temp,  total):
	total.number.opp += 1
	quotes =  [item for item in quotations \
		if item['opportunity'] == opp.get("name")]
	temp.update(frappe._dict({"qt": [], "so":[]}))
	if not quotes:
		return
	for qt in quotes:	
		total.number.qt += 1
		total.amount.qt += qt.get("base_grand_total");
		temp.qt.append(qt)
	sales_orders=[item for item in sales_orders if item['quotation']==quotes[0].get("quotation")]
	for so in sales_orders:
		temp.so.append(so)
		total.number.so += 1
		total.amount.so += so.get("base_grand_total");

def update_bdms_and_managers(data, bdms_managers, filters):

	for key, val in data.items():
		for ikey, ivalues in bdms_managers.items():
			if ikey == "bdms":
				for jval in ivalues:
					if filters.get("bdm") and filters.get("bdm") != jval:
						continue
					val.bdms[jval] = frappe._dict({"so": 0.0, "qt": 0.0})
					
			if ikey == "managers":
				for jval in ivalues:
					if filters.get("manager") and filters.get("manager") !=  jval:
						continue
					val.managers[jval] = frappe._dict({"so": 0.0, "qt": 0.0})

def get_acc_manager_and_bdms():

	data = frappe._dict()
	doc = frappe.get_meta("Opportunity")
	acc_manager =   doc.get_field("account_manager")
	bdm = doc.get_field("bdm")
	
	data.update({
		"managers": acc_manager.options.splitlines(), 
		"bdms": bdm.options.splitlines()
	})
	return data

def get_start_end_date(fiscal_year):
	
	fiscal_year = frappe.db.get_value("Fiscal Year", fiscal_year, fieldname=\
				["year_start_date", "year_end_date"], as_dict=True)
	return frappe._dict({
			"fiscal_year": fiscal_year,
			"start_date": get_date(fiscal_year.get("year_start_date"), is_string=True),
			"end_date": get_date(fiscal_year.get("year_end_date"), is_string=True)
		})
def get_condition(filters):

	condition = ""	
	if filters.get("company"):
		condition += " WHERE OPP.company=%(company)s "
	if filters.get("fiscal_year"):
		condition += " AND OPP.transaction_date BETWEEN %(start_date)s AND  %(end_date)s "
	if filters.get("manager"):
		condition += " AND OPP.account_manager=%(manager)s "
	if filters.get("opportunity"):
		condition += " AND OPP.name=%(opportunity)s "
	if filters.get("bdm"):
		condition += " AND OPP.bdm=%(bdm)s "
	return condition 	

def validate_filters(filters):
	
	if not filters.get("fiscal_year"):
		frappe.throw("Please select <strong>Fiscal Year</strong>")
	if not filters.get("company"):
		frappe.throw("Please select <strong>Company</strong>")


def get_report_types(fiscal_start_end_date):
	fiscal_start_end_date  = fiscal_start_end_date.get("fiscal_year")
	start_date = fiscal_start_end_date.get("year_start_date")
	end_date = fiscal_start_end_date.get("year_end_date")
	months = [start_date.strftime("%b-%Y")]
	for idx in range(0, 11):
		start_date = get_next_month(start_date)
		months.append(start_date.strftime("%b-%Y"))
	report_types =  _get_report_types(months)
	return report_types
	
def _get_report_types(months):
	report_type_map = {
		"Monthly": 1,
		"Quarterly": 3,
		"Half Year": 6
	}

	data = frappe._dict()
	for key, val in report_type_map.items():
		d = []
		to = 0
		if key == "Monthly":
			to = 13
			d = [i for i in range(1, 14)][::val]
		elif key == "Quarterly":
			to = 5
			d = [i for i in range(1, 14)][::val]
		elif key == "Half Year":
			to = 3
			d = [i for i in range(1, 14)][::val]
		current = 0
		temp_data = {}
		for i in range(1, to):
			start = d[i-1]
			end = d[i]
			temp = []
			for j in range(start, end):
				temp.append(months[j-1])
			temp = tuple(temp)
			temp_data[temp] = frappe._dict({
					"bdms": frappe._dict(),
					"managers": frappe._dict()
					})
		data[key] = temp_data
			
	return data		
