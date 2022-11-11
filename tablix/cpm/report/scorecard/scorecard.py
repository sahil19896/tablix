# Copyright (c) 2013, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cstr, cint, flt

def execute(filters={}):
	columns, data = [], []

	data = get_data(filters)
	columns = get_columns(filters)
	
	return columns, data


def get_columns(filters):
	fy = ""
	if filters.get("fiscal_year"):
		fy = "(" +cstr(filters.get("fiscal_year")) + ")"
	return [
		_("Perspective") + cstr(fy)+ ":Data:100", _("Strategic Theme")+cstr(fy)+":Data:300", 
		_("Strategic Objective")+cstr(fy)+":Data:300", _("Indicator(KPI)")+cstr(fy)+":Data:200",
		_("UOM")+cstr(fy)+":Data:100", _("Strategic Owner")+cstr(fy)+":Data:200",
		_("Base Value")+cstr(fy)+":Data:150", _("Target Value")+cstr(fy)+":Data:150",
		_("Actual Value")+cstr(fy)+":Data:150"
	]

def get_condition(filters):
	condition = ""
	if filters.get("company"):
		condition += " AND ST.company=%(company)s "
	if filters.get("fiscal_year"):
		condition += " AND ST.fiscal_year=%(fiscal_year)s "
	return condition

def get_data(filters={}):
	condition = get_condition(filters)
	
	data = []
	results = frappe.db.sql("""SELECT ST.select_series, ST.perspective, ST.fiscal_year, ST.name AS t_name, ST.title AS t_title, O.name AS o_name, \
			O.title AS o_title, I.name AS i_name, I.uom, I.base_value, I.base_data, I.base_percentage, \
			I.target_percentage, I.target_data, I.title as i_title, I.target_value, I.actual_value, I.actual_data, ST.strategic_owner_name, 
			I.actual_percentage FROM `tabStrategic Theme` ST INNER JOIN `tabStrategic Objective` O \
			ON ST.name=O.strategic_theme INNER JOIN `tabIndicator` I ON O.name=I.strategic_objective \
			WHERE ST.select_series IS NOT NULL %s  ORDER BY ST.priority, I.name"""%(condition), filters, as_dict=True)

	themes = {}
	objectives = {}
	for res in results:
		theme_title = ""
		perspective = ""
		theme = ""
		objective = ""
		objective_title = ""
		if not themes.has_key(res.get("t_name")):
			themes[res.get("t_name")] = True
			theme= cstr(res.get("t_name"))+" - "+cstr(res.get("t_title"))
			perspective = res.get("perspective")
		if not objectives.has_key(res.get("o_name")):
			objectives[res.get("o_name")] = True
			objective = cstr(res.get("o_name"))+ " - " +cstr(res.get("o_title"))
	
		base_value, target_value, actual_value = "" , "", ""
		if(res.get("uom")) == "Value":
			base_value = res.get("base_value")
			target_value = res.get("target_value")
			actual_value = res.get("actual_value")
		elif(res.get("uom")) == "Percentage":
			base_value = res.get("base_percentage")
			target_value = res.get("target_percentage")
			actual_value = res.get("actual_percentage")

		elif(res.get("uom")) == "Data":
			base_value = res.get("base_data")
			target_value = res.get("target_data")
			actual_value = res.get("actual_data")
		data.append([perspective, theme, objective, cstr(res.get("i_name"))+" - "+cstr(res.get("i_title")), 
			res.get("uom"), res.get("strategic_owner_name"), base_value, target_value, actual_value])


	return data
