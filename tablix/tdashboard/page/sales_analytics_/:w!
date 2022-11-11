'''
	Added By Sahil
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr
from collections import OrderedDict
from frappe.utils import now_datetime, datetime, today
from datetime import timedelta
from tablix.tdashboard.utils import get_prev_and_cur_quarter_dates,\
					get_prev_and_cur_week_dates,\
					get_prev_and_cur_month_dates

APPROVALS_STATUS = [
		'RFQ Approved', 'Manager Rejected', 'CBDO Approved', 'RFQ', \
		'KAM Rejected','RFQ Approved','Insufficient Information', \
		'Manager Approval', "KAM Approved", "Rfq"
	]

def get_dashboard_data(filters):
	frequency = get_frequency_info(filters)
	data = frappe._dict({
		"leads": {}, "opps":{},
		"quotes": {}, "so": {}, "si": {},
		"target_vs_value": []
		})
	data.leads = get_lead_information(filters)
	data.opps = get_opp_information(filters)
	data.so_booking = get_so_booking_information(filters)
	data.so_closure = get_so_closure_information(filters)
	data.quotes = get_quotes_information(filters)
	data.revenue = get_revenue_information(filters)
	data.target_vs_value = get_target_vs_value(filters)	
	return data

# Lead information for three[Frequencies]
def get_lead_information(filters):
	frequency = get_frequency_info(filters)
	data = frappe._dict({"labels": [], "data": []})	
	cond = get_condition(filters, frequency, "creation")
	results = frappe.db.sql(""" SELECT name, %s  status, creation \
		FROM `tabLead` WHERE %s %s """%(cond.get("select_field"),\
		cond.get("condition"), cond.get("order_by")), as_dict=True)
	
	for res in results:
		if not data.has_key(res.get("select_field")):
			data.data.append(res.get("select_field"))
			data.labels.append(res.get("select_field"))
			data[res.get("select_field")] = frappe._dict({
				"total_leads": 0.0, "lead_to_opp": 0.0,
				"lead_to_quotes": 0.0, "lead_to_so": 0.0,
				"lost_deals": 0.0, "won_leads": 0.0
			})
		temp = data.get(res.get("select_field"))
		temp.total_leads += 1
		if res.get("status")  in ["Quotation", "Opportunity", "Converted"]:
			temp.lead_to_opp += 1	
			if res.get("status") == "Quotation":
				quote = frappe.db.get_value("Quotation", {"lead":res.get("name"), 
					"docstatus":1}, ["status", "base_total"], 
					as_dict=True)
				if quote:
					temp.lead_to_quotes += 1
						
			elif res.get("status") == "Converted":
				temp.lead_to_quotes += 1
				temp.lead_to_opp += 1
				if frappe.db.get_value("Quotation", {"lead": res.get("name"), 
					"docstatus":1, "status": "Ordered"}):
					temp.lead_to_so += 1

		if temp.lead_to_quotes:
			temp.lost_deals = temp.lead_to_quotes - temp.lead_to_so
				

	for res in  data.labels:
		data.data[data.labels.index(res)] = data[res]	
	return data	
					
# Opp information for three[Frequencies]
def get_opp_information(filters):
	frequency = get_frequency_info(filters)
	cond = get_condition(filters, frequency, "creation")
	data = frappe._dict({"labels": [], "data": []})
	results = frappe.db.sql(""" SELECT name, %s status, creation FROM 
			`tabOpportunity` WHERE enquiry_from="Customer" AND %s %s""" %(cond.get("select_field"),
			cond.get("condition"), cond.get("order_by")), as_dict=True)

	for res in results:
		
		if not data.labels.count(res.get("select_field")):
			data.labels.append(res.get("select_field"))
			data.data.append(res.get("select_field"))
			data[res.get("select_field")] = frappe._dict({
				"total_opps": 0, "opp_to_quotes": 0,
				"quotes_value": 0.0, "opp_to_so": 0,
				"lost_opps": 0,	 "so_value": 0.0
			})
		temp = data.get(res.get("select_field"))
		temp.total_opps += 1
		if res.get("status")  == "Quotation":
			quote_info = frappe.db.get_value("Quotation", {"opportunity": res.get("name"),
					"docstatus": 1}, ["status", "base_total"], as_dict=True)
			if quote_info:
				temp.opp_to_quotes += 1
				temp.quotes_value += quote_info.get("base_total")
				if quote_info.get("status") == "Ordered":
					temp.opp_to_so += 1
					temp.so_value += quote_info.get("base_total")
									
		if temp.opp_to_quotes:
			temp.lost_opps = temp.total_opps - temp.opp_to_quotes

	for res in data.labels:
		data.data[data.labels.index(res)] = data[res]		

	return data	

# GET Sales Order Booking value for selected Frequency
def get_so_booking_information(filters):
	frequency = get_frequency_info(filters)
	cond = get_condition(filters, frequency, "SO.transaction_date")
	data = frappe._dict({"labels": [], "data": [], "targets": []})
	so_bookings = frappe.db.sql(""" SELECT SO.name, %s SO.transaction_date, base_total \
			FROM `tabSales Order` SO WHERE docstatus=1 AND %s %s \
			"""%(cond.get("select_field"), cond.get("condition"), cond.get("order_by")),
			as_dict=True)
	for so_b in so_bookings:
		if not data.labels.count(so_b.get("select_field")):
			data.labels.append(so_b.get("select_field"))
			data.targets.append(so_b.get("select_field"))
			data.data.append(so_b.get("select_field"))
			data[so_b.get("select_field")] = frappe._dict({
				"so_booking": 0.0,
			})

		temp = data.get(so_b.get("select_field"))
		temp.so_booking += flt(so_b.get("base_total"))
	for label in data.labels:
		temp = label.split("-")[1]
		data.targets[data.labels.index(label)] = get_target_value(filters, temp)
		data.data[data.labels.index(label)] = data[label]
	
	return data			
		
# GET Sales Order to be closed on same Frequency Value
def get_so_closure_information(filters):
	frequency = get_frequency_info(filters)
	data = frappe._dict({"data": [], "labels": []})
	cond  = get_condition(filters, frequency, "P.expected_end_date")
	so_closure = frappe.db.sql("""SELECT P.sales_order, %s SO.base_total FROM `tabProject` P INNER JOIN \
		`tabSales Order` SO ON P.name=SO.project  WHERE P.status='Open' AND %s %s """%(\
		cond.get("select_field"), cond.get("condition"), cond.get("order_by")), as_dict=True)
	
	for so_c in so_closure:	
		if not data.labels.count(so_c.get("select_field")):
			data.labels.append(so_c.get("select_field"))
			data.data.append(so_c.get("select_field"))
			data[so_c.get("select_field")] = frappe._dict({
				"closure_value": 0.0, "closure_total": 0
			})
		temp = data.get(so_c.get("select_field"))
		temp.closure_value += flt(so_c.get("base_total"))
		temp.closure_total += 1

	for label in data.labels:
		data.data[data.labels.index(label)] = data[label]
	
	return data			
			

#GET Quotation Open/Value/Total No for selected frequency
def get_quotes_information(filters):
	frequency = get_frequency_info(filters)
	data = frappe._dict({"labels": [], "data": []})
	cond = get_condition(filters, frequency, "transaction_date")
	quotes = frappe.db.sql(""" SELECT name, %s base_total,  transaction_date \
			FROM `tabQuotation` WHERE docstatus=0 AND %s %s """%(cond.get("select_field"),
			cond.get("condition"), cond.get("order_by")), as_dict=True)
	
	for quote in quotes:
		if not data.labels.count(quote.get("select_field")):
			data.labels.append(quote.get("select_field"))
			data.data.append(quote.get("select_field"))
			data[quote.get("select_field")] = frappe._dict({
				"quotes_total": 0.0,
				"quotes_value": 0.0,
			})

		temp = data.get(quote.get("select_field"))
		temp.quotes_value += flt(quote.get("base_total"))
		temp.quotes_total += 1

	for label in data.labels:
		data.data[data.labels.index(label)] = data[label]
	return data



# GET Revenue/Invoice Information
def get_revenue_information(filters):
	frequency = get_frequency_info(filters)
	data = frappe._dict({"labels": [], "data": []})
	cond = get_condition(filters, frequency, "posting_date")
	invoices = frappe.db.sql(""" SELECT name, posting_date, %s  base_total FROM `tabSales Invoice`\
		WHERE docstatus=1 AND %s %s """%(cond.get("select_field"),cond.get("condition"),\
		cond.get("order_by")), as_dict=True)

	for invoice in invoices:
		if not data.labels.count(invoice.get("select_field")):
			data.data.append(invoice.get("select_field"))
			data.labels.append(invoice.get("select_field"))
			data[invoice.get("select_field")] = frappe._dict({
				"revenue": 0.0
			})
		temp = data.get(invoice.get("select_field"))
		temp.revenue += flt(invoice.get("base_total"))

	for label in data.labels:
		data.data[data.labels.index(label)] = data[label]
	return data		



#GET target vs Actual
def get_target_vs_value(filters):
	data = frappe._dict({"orders":[], "targets":[], "labels":[]})
	if frappe.db.get_value("Sales Person Target", filters.get("sales_target")):
		target = frappe.db.get_value("Sales Person Target", filters.get("sales_target"), ["name", \
				"employee"], as_dict=True)

		doctype = "Sales Person Target {frequency} Item".format(frequency=filters.get("frequency"))
		targets = frappe.db.get_values(doctype, {"parent": target.get("name")}, "*",\
				order_by="idx ASC", as_dict=True)
		_filters = {"user": frappe.db.get_value("Employee", target.get("employee"), \
				["user_id"], as_dict=True).get("user_id")}

		cond = get_condition_for_target(filters)
		for target in targets:
			_filters.update({
				"start": target.get("start_date"), 
				"end": target.get("end_date")
			})		
			temp = frappe.db.sql("""SELECT IFNULL(SUM(base_total), 0.0) AS amount FROM \
				`tabSales Order` WHERE creation BETWEEN %(start)s AND %(end)s AND \
				docstatus=1 {0} """.format(cond), _filters, as_dict=True)[0]
			data.labels.append(get_target_label(filters, target))
			data.orders.append(temp.get("amount"))
			data.targets.append(target.get("target_value"))
	
	return data

def get_condition_for_target(filters):
	
	cond = ""
	if not frappe.db.get_value("Sales Person Target", filters.get("sales_target")):
		return cond
	target = frappe.get_doc("Sales Person Target", filters.get("sales_target"))
	if not target.get("is_group"):
		cond += " AND account_manager=%(user)s "
	return cond


def get_target_label(filters, target):
	
	label = None
	start = target.get("start_date")
	if filters.get("frequency") == "Quarterly":
		end = target.get("end_date")
		label = "{0}-{1}".format(end.year, end.month/3)
	elif filters.get("frequency") == "Monthly":
		label = "{0}-{1}".format(start.year, start.strftime("%B"))
	else:
		label = "{0}-{1}".format(start.year, start.strftime("%U"))
		
	return label

#Filters and Conditional functions
'''
 --------------------------------------------
'''	
def get_frequency_info(filters, add=0):
	func = ""
	start_end_dates = {}
	if filters.get("frequency") == "Weekly":
		start_end_dates = get_prev_and_cur_week_dates(filters)
		func = "DATE_FORMAT({docfield}, '{_format}')"
	elif filters.get("frequency") == "Monthly":
		start_end_dates = get_prev_and_cur_month_dates(filters)
		func = "DATE_FORMAT({docfield}, '{_format}')"
	elif filters.get("frequency") == "Quarterly":
		start_end_dates = get_prev_and_cur_quarter_dates(filters)
		func = " CONCAT_WS('-', YEAR({docfield}), QUARTER({docfield}))"
	data = frappe._dict({
		"select_func": func
	})
	data.update(start_end_dates)
	return data

def get_condition(filters, frequency, docfield=""):
	frequency.select_func = frequency.select_func.format(docfield=docfield, **frequency)
	data = frappe._dict({
		"condition": "", "docfield": docfield,
		"fiscal_year": filters.get("fiscal_year"),
		"select_field":" {select_func} AS select_field, ".format(**frequency),
		"order_by": " ORDER BY {docfield} {order} ".format(docfield=docfield,
			order="DESC", **frequency)
	})
	data.update(frequency)	
	condition=" {docfield} BETWEEN '{start_date}' AND '{end_date}' ".format(**data)
	print(condition)
	data.update({"condition": condition})
	return data


# GET Target corresponding to Frequency
def get_target_value(filters, val):
	target = 0.0
	if not filters.get("sales_target"):
		return target
	if filters.get("frequency") == "Monthly":
		field = "monthly_items"
	elif filters.get("frequency") == "Quarterly":
		field = "quarterly_items"
	else:
		field = "weekly_items"
	targets = frappe.get_doc("Sales Person Target", filters.get("sales_target")).get(field)
	if filters.get("frequency") == "Monthly":
		for month in targets:
			if month.get("month") == val:
				target = month.get("target_value")
				break
	else:
		temp = targets[cint(val)]
		print(temp.as_dict())
		target = temp.get("target_value")	
					
	return target
			
@frappe.whitelist()
def get_more_data(prev, cur, doctype=None):
		
	print(prev);
	print(cur);
	print(doctype);	
