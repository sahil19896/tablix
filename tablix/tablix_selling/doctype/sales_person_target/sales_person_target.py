# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import calendar
from frappe.utils import flt, cint, cstr
from datetime import timedelta
from frappe import _, msgprint, throw
from tablix.tdashboard.utils import get_all_fiscal_weeks, get_all_fiscal_quarters
import json

class SalesPersonTarget(Document):

	
	def autoname(self):
		self.name = "{0}-{1}-{2}".format(self.get("employee"), self.fiscal_year, "Target")	
	def validate(self):
		self.get_fiscal_year_info()
		self.calculate_system_wise_targets()
		self.calculate_monthly_targets()
		self.update_or_create_sales_person()
	
	def calculate_system_wise_targets(self):
		self.total_target = 0.0
		for target in self.get("targets"):
			self.total_target += target.get("total_amount")	
				
	def calculate_monthly_targets(self):
		if not self.monthly_items:
			default_percentage = 1.0/12.0*100.0
			cur_date = self._fs.year_start_date.strftime("%B")	
			months = get_all_months(self.fiscal_year)
			distribution = self.validate_monthly_distribution()
			for idx, percentage in enumerate(distribution.get("percentages")):
				month = months[idx]
				self.append("monthly_items", {
					"frequency":"Monthly",
					"fiscal_year": month.get("start_date").strftime("%Y"),
					"month": month.get("start_date").strftime("%B"),
					"start_date":  month.get("start_date"),
					"end_date": month.get("end_date"),
					"target_value": percentage.percentage_allocation/100.0*self.total_target,
					"target_percentage": percentage.percentage_allocation,
					"distribution_id": self.monthly_distribution
				})	
		else:
			self.validate_monthly_distribution()
			total_amt = 0.0
			percentage = 0.0
			for item in self.get("monthly_items"):
				percentage += flt(item.get("target_percentage"))
				item.target_value = item.target_percentage/100.0*self.total_target
				total_amt += flt(item.get("target_value"))
			if percentage <= 99.9:
				frappe.throw(_("Total Percentage should be 100%, \
					Actual {0}".format(percentage)))
				
	def update_or_create_sales_person(self):
		if not frappe.db.get_value("Sales Person", {"sales_person_name": self.employee_name}):
			doc = frappe.get_doc({
				"doctype": "Sales Person",
				"parent_sales_person": self.get("parent_sales_person"),
				"employee": self.employee,
				"sales_person_name" : self.employee_name,
				"distribution_id": self.monthly_distribution,
				"is_group": self.get("is_group"),	
				"targets": [
					frappe.get_doc({
						"doctype": "Target Detail",
						"fiscal_year": self.fiscal_year,
						"target_amount": self.total_target 
					})	
				]
			})
			doc.save(ignore_permissions=True)
		else:
			doc = frappe.get_doc("Sales Person", self.employee_name)
			flag = False
			for target in doc.get("targets"):
				if target.get("fiscal_year") == self.fiscal_year:
					flag= True
					target.target_amount = self.total_target
	
			if not flag:
				doc.append("targets", {
					"fiscal_year": self.fiscal_year,
					"target_amount": self.total_target
				})
			doc.save(ignore_permissions=True)
	
	def validate_monthly_distribution(self):
		distribution = frappe.get_doc("Monthly Distribution", self.monthly_distribution)
		if distribution.fiscal_year != self.fiscal_year:
			frappe.throw(_("Fiscal Year Error Target Year:{0}, \
				Monthly Distribution Year:{1}.".format(self.fiscal_year, \
				distribution.fiscal_year)))
		return distribution
	
	def get_fiscal_year_info(self):
		self._fs  = frappe.get_doc("Fiscal Year", self.fiscal_year).as_dict()
	



def get_all_months(fiscal_year):
	months = []
	start_end_dates = frappe.db.get_value("Fiscal Year", fiscal_year,["year_start_date", "year_end_date"],
			as_dict=True)
	if not start_end_dates:
		return months
	start_date = start_end_dates.get("year_start_date") 
	for idx in range(0, 12):
		days = cint(start_date.strftime("%d"))
		total_days = cint(calendar.monthrange(cint(fiscal_year), 
				cint(start_date.strftime("%m")))[1])
		temp = total_days - days
		_start = start_date
		_end = start_date + timedelta(days=temp)
		months.append({"start_date": _start, "end_date": _end, "days": temp+1})
		start_date = _end + timedelta(days=1)
	return months


@frappe.whitelist()
def update_targets(name, frequency, data=[]):

	if data and isinstance(data, str):
		data = json.loads(data)	
	doc = frappe.get_doc("Sales Person Target", name)
	fiscal_year = frappe.db.get_value("Fiscal Year", doc.fiscal_year, \
			["year_start_date", "year_end_date"], as_dict=True)

	if frequency == "Weekly":
		update_weekly_targets(doc, fiscal_year)
	elif frequency == "Quarterly":
		update_quarterly_targets(doc, fiscal_year, data)

def update_quarterly_targets(doc, fiscal_year, data):

	quarters = get_all_fiscal_quarters(fiscal_year)
	doc.quarterly_items = []
	total = 0.0
	for idx, quarter in  enumerate(quarters):
		total += data[idx]
		percentage =  data[idx]/100.0
		value = doc.total_target*percentage
		doc.append("quarterly_items", {
			"fiscal_year": doc.fiscal_year, "start_date": quarter.get("start_date"),
			"end_date": quarter.get("end_date"), "target_percentage": data[idx],
			"target_value": value, "frequency": "Quarterly", "idx": idx+1})
	if total != 100:
		frappe.throw(_("Total Percentage should be equal to 100%."))

	doc.save()
	frappe.db.commit()
			
	
def update_weekly_targets(doc, fiscal_year):

	if not doc.quarterly_items:
		return

	fiscal_weeks = get_all_fiscal_weeks(fiscal_year)
	start = 0
	doc.weekly_items = []
	for quarter in doc.quarterly_items:
		percent = quarter.get("target_percentage")/100.0
		e_percent = percent/13
		for idx in range(0, 13):
			week = fiscal_weeks[start]
			value = doc.total_target*e_percent
			doc.append("weekly_items", {
				"start_date": week.get("start_date"), "end_date": week.get("end_date"),
				"fiscal_year": doc.fiscal_year, "target_percentage": e_percent,
				"target_value": value, "frequency": "Weekly", "idx": start+1
			})
			start += 1
	
	doc.save()
	frappe.db.commit()	
