# Copyright (c) 2013, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict
from frappe import msgprint

def execute(filters=None):
	columns, data = [], []
	
	if not filters: filters = {}
	
	columns = get_columns()	
	quo_data = get_data(filters)	

	for d in quo_data:
		value = ""
		margin = 0
		boq = get_boq_data(d.boq_profile)
		if(boq):
			if(boq[0].is_project):
				value = "Project"
			else:
				value = "AMC"
		else:
			value = ""
		
		opty = get_opty(d.opportunity)
		so = get_so_detail(d.name)
		if(so):
			so_name = so[0].parent
			so_creation = so[0].creation
			so_data = get_so_data(so[0].parent)
			if(so_data):
				po_no = so_data[0].po_no
				po_date = so_data[0].po_date
				project = so_data[0].project
			else:
				po_no = ""
				po_date = ""
				project = ""
		else:
			so_name = ""
			so_creation = ""
			po_no = ""
			po_date = ""
			project = ""
		if(d.total_margin_percent):
			if(d.total_margin_percent < 1):
				margin = 0
			else:
				margin = float("{0:.2f}".format(d.total_margin_percent))

		comp_date, sub_date = get_comm_detail(d.get("name"))

		data.append([d.lead, d.customer_name, d.contact_display, d.contact_email, d.contact_mobile, d.opportunity, opty[0].opportunity_from, opty[0].expected_date, opty[0].creation, d.bdm, d.name, d.creation, comp_date, sub_date, margin, d.valid_till, value, d.boq_profile, boq[0].owner, boq[0].creation, boq[0].scope_of_work, boq[0].project_site_name, boq[0].system_type, d.total, d.grand_total, d.status, so_name, so_creation, d.payment_terms_template, po_no, po_date, project ])

	return columns, data


def get_columns():
	"Return columns based on filters"

	columns = [
		{
			"label": _("Lead No."),
			"fieldname": "lead",
			"fieldtype": "Link",
			"options": "Lead",
			"width": 150
		},
		{
			"label": _("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Contact Person"),
			"fieldname": "contact_person",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Email"),
			"fieldname": "email",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Phone No."),
			"fieldname": "phone_no",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("OPTY No."),
			"fieldname": "opty_no",
			"fieldtype": "Link",
			"options": "Opportunity",
			"width": 150
		},
		{
			"label": _("OPTY From(Lead/Customer)"),
			"fieldname": "opty_from",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("OPTY Expected Date"),
			"fieldname": "opty_expected_date",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": _("OPTY Created on."),
			"fieldname": "opty_created_on",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Tab Rep/BDM"),
			"fieldname": "tablix_rep",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Quotation ID"),
			"fieldname": "quotation_id",
			"fieldtype": "Link",
			"options": "Quotation",
			"width": 150
		},	
		{
			"label": _("QTN Started date"),
			"fieldname": "qtn_started_date",
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"label": _("QTN Completed Date"),
			"fieldname": "qtn_completed_date",
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"label": _("QTN Submitted Date"),
			"fieldname": "qtn_submitted_date",
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"label": _("Total Margin %"),
			"fieldname": "margin",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("QTN Validity Date"),
			"fieldname": "qtn_validity_date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Project/AMC"),
			"fieldname": "project_amc",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("BOQ Profile"),
			"fieldname": "boq_profile",
			"fieldtype": "Link",
			"options": "BOQ Profile",
			"width": 150
		},
		{
			"label": _("BOQ Owner"),
			"fieldname": "boq_owner",
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		},
		{
			"label": _("BOQ Creation Date"),
			"fieldname": "boq_creation_date",
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"label": _("Scope of Work"),
			"fieldname": "scope_fo_work",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Project Site Name"),
			"fieldname": "project_site_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Solution"),
			"fieldname": "solution",
			"fieldtype": "Data",
			"width": 250
		},
		{
			"label": _("Cost Price Total"),
			"fieldname": "cost_price_total",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Grand Total (including VAT)"),
			"fieldname": "grand_total",
			"fieldtype": "Data",
			"width": 150
		},
		{	
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("SO No."),
			"fieldname": "so_no",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 150
		},
		{
			"label": _("SO Created Date"),
			"fieldname": "so_created_date",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Payment Terms"),
			"fieldname": "payment_terms",
			"fieldtype": "Link",
			"width": 150,
			"options": "Payment Terms Template"
		},
		{
			"label": _("Customer LPO NO."),
			"fieldname": "lpo_no",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Customer LPO Date"),
			"fieldname": "lpo_date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Project Name"),
			"fieldname": "project_name",
			"fieldtype": "Link",
			"options": "Project",
			"width": 250
		}
	]

	return columns

def get_condition(filters):
	condition = ""
	if filters.get("customer"): condition += "  AND customer = %(customer)s"
	if filters.get("lead"): condition += " AND lead = %(lead)s"
	
	return condition


def get_data(filters):
	condition = get_condition(filters)
	row = []
	data = frappe.db.sql("""SELECT lead, customer_name, contact_display, contact_email, contact_mobile, opportunity, \
			bdm, boq_profile, name, creation, total_margin_percent, total, grand_total, status, payment_terms_template,
			valid_till FROM `tabQuotation`
			WHERE docstatus != 2 AND boq_profile IS NOT NULL %s """%condition, filters, as_dict=True)
	
	return data

def get_boq_data(name):
	boq_data = frappe.db.sql("""SELECT creation, is_amc, is_project, scope_of_work, project_site_name, system_type, owner FROM `tabBOQ Profile` WHERE name = %s """,(name), as_dict=True)
	return boq_data

def get_opty(name):
	opty = frappe.db.sql("""SELECT creation, opportunity_from, expected_date FROM `tabOpportunity` where name = %s """,(name), as_dict=True)
	return opty

def get_so_detail(name):
	try:
		so = frappe.db.sql("""SELECT parent, creation FROM `tabSales Order Item` WHERE quotation_detail = %s LIMIT 1 """,(name), as_dict=True)
	except:
		so = ""

	return so

def get_so_data(name):
	try:
		so_data = frappe.db.sql("""SELECT po_no, po_date, project FROM `tabSales Order` WHERE name = %s """,(name), as_dict=True)
	except:
		so_data = ""
	return so_data

def get_comm_detail(q_name):
	comp_date = ""
	sub_date = ""
	doc = []
	try:
		doc = frappe.db.sql("""select * from `tabCommunication` where reference_name = %s """,(q_name), as_dict=True)
	except:
		doc = []

	if(doc):
		for d in doc:
			if((d.get("content") == "Boq Complete") or (d.get("content") == "DOS Approved")):
				comp_date = d.creation
			if(d.content == "Submitted"):
				sub_date = d.creation

		return comp_date, sub_date
	else:
		return "", ""
