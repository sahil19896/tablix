# -*- coding: utf-8 -*-
# Copyright (c) 2018, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt
from frappe import _, msgprint, throw
from frappe.model.mapper import get_mapped_doc
from frappe.utils import now_datetime
from tablix.notifications.notification_controller import NotificationController
from frappe import _, msgprint

class SalesOrderChangeRequest(Document, NotificationController):
	
	def validate(self):
		self._so = frappe.get_doc("Sales Order", self.sales_order)
		self.update_current_so_cost()
		self.validate_dates()
		self.update_items()
		self.update_total_amount()
		self.calculate_total_after_change()
		self.update_base_amount()
		self.send_notification();

	def validate_dates(self):	
		if self.get("date_of_submission") > self.get("date_required"):
			frappe.throw(_("Date of submission cannot be greater than Date Required."))

	def update_current_so_cost(self):
		self.update({
			"before_cost_amount": self._so.total_cost_amount,
			"base_before_cost_amount": self._so.base_total_cost_amount,
			"before_selling_amount": self._so.total,
			"base_before_selling_amount": self._so.base_total,
			"before_margin_amount": self._so.total_margin_amount,
			"base_before_margin_amount": self._so.base_total_margin_amount,
			"before_margin_percentage": self._so.total_margin_percent
		})	

	def update_items(self):
		total_cost = 0.0
		quotation_name = self.get_quotation_name()
		for item in self.get("items"):
			item.margin_type = "Percentage"
			item.prevdoc_docname = quotation_name
			if item.get("cr_type") == "Deletion":
				if(not item.get("sales_order_item")):
					frappe.throw(_("Please select item to be removed."));

				self.update_so_item_default_prices(item)

			self.validate_item(item)
			self.update_default_item_details(item)

			price_list = frappe.db.get_value("Item Price", {"price_list": self._so.selling_price_list,
				 "item_code":item.get("item_code"), "selling": True}, ["currency", "price_list_rate"], as_dict=True)
			if price_list:
				item.price_list_rate = flt(price_list.get("price_list_rate"))
			if item.get("price_list_rate")  and (item.get("selling_amount") and item.get("cost_amount")):
				diff = item.get("selling_amount")  - item.get("price_list_rate")
				if diff:
					item.margin_rate_or_amount  = flt(diff)/flt(item.get("price_list_rate"))*100.0
			
			self.update_margin(item)	
						


	def update_so_item_default_prices(self, item):
		so_item = frappe.get_doc("Sales Order Item", item.get("sales_order_item"))
		copy = so_item.as_dict()	
		for key, val in copy.iteritems():
			if key in ["cost_amount", "selling_amount", "margin_amount", "rate", "amount", 
				"total_cost_amount", "warehouse", "prevdoc_docname", "quotation_item_detail",
				"site", "delivery_date", "qty",  "brand", "item_group", "price_list_rate", "description"]:
				item.set(key, val)

		item.set("item_code", so_item.get("item_code"))
		item.set("item_name", so_item.get("item_name"))
	
	def update_default_item_details(self, item):
		item_detail = frappe.get_doc("Item", item.get("item_code"))
		item.set("item_group", item_detail.get("item_group"))
		item.set("brand", item_detail.get("brand"))		
	
	def update_margin(self, item):
		margin_type = item.get("select_margin_type")
		if item.get("cost_amount") and margin_type == "Amount":
			if not item.get("selling_amount"):
				item.selling_amount = flt(item.get("cost_amount"))
		else:
			item.selling_amount = flt(item.get("cost_amount"))

		if item.get("selling_amount"):
			item.margin_amount = item.get("selling_amount") - flt(item.get("cost_amount"))
			if item.margin_amount:
				item.margin_percentage = item.margin_amount/item.selling_amount*100.0
			else:
				item.margin_percentage = 0.0
		self.update_item_base_amount(item)

	def update_item_base_amount(self, item):
		if self._so:
			conversion_rate = self._so.conversion_rate or 1.0
			item.base_cost_amount = item.cost_amount*conversion_rate
			item.base_total_cost_amount = item.total_cost_amount*conversion_rate
			item.base_selling_amount = item.selling_amount*conversion_rate
			item.base_amount = item.amount*conversion_rate
			item.base_margin_amount = item.margin_amount*conversion_rate
			item.base_rate = item.rate*conversion_rate
					

	def update_total_amount(self):
		self.reset_default_amounts()
		self.reset_current_amounts()
	
		for item in self.get("items"):
			if item.get("cr_type") == "Addition":
				self.add_amount_to_total(item)	
			else:
				self.modify_total_amount(item)


	def reset_default_amounts(self):
		self.after_cost_amount =  0.0
		self.after_base_before_cost_amount = 0.0
		self.after_selling_amount = 0.0
		self.base_after_selling_amount = 0.0
		self.after_margin_amount = 0.0
		self.base_after_margin_amount  = 0.0
		self.after_margin_percent  = 0.0
		self.base_cost_amount = 0.0
		self.base_selling_amount = 0.0

	def reset_current_amounts(self):
		self.cost_amount = 0.0
		self.selling_amount = 0.0

	def add_amount_to_total(self, item):
		self.cost_amount += flt(item.total_cost_amount)
		self.base_cost_amount +=  flt(item.base_total_cost_amount)
		self.selling_amount += flt(item.amount)
		self.base_selling_amount += flt(item.base_amount)
		
	def modify_total_amount(self, item):
		so_item = frappe.get_doc("Sales Order Item", item.get("sales_order_item"))
		cost_diff = 0.0
		selling_diff = 0.0

		if item.get("cr_type") == "Deletion":
			cost_diff -= item.get("total_cost_amount")
			selling_diff -= item.get("amount")
		elif item.get("cr_type") == "Modification":
			cost_diff = item.get("total_cost_amount") - so_item.get("total_cost_amount")
			selling_diff = item.get("amount") - so_item.get("amount")
		self.cost_amount +=  flt(cost_diff)
		self.selling_amount += flt(selling_diff)


	def calculate_total_after_change(self):
		if self._so:
			self.after_cost_amount = self.before_cost_amount
			self.after_selling_amount = self.before_selling_amount
			self.after_margin_amount = self.before_margin_amount
			self.after_margin_percentage = 0.0
			if self.after_margin_amount:
				self.after_margin_percentage = self.after_margin_amount/self.after_selling_amount*100.0
			
	
	def update_base_amount(self):
		if self._so:
			conversion_rate = self._so.conversion_rate
			self.base_after_cost_amount = self.after_cost_amount*conversion_rate
			self.base_after_selling_amount = self.after_selling_amount*conversion_rate
			self.base_after_margin_amount = self.after_margin_amount*conversion_rate
			self.base_cost_amount  = self.cost_amount*conversion_rate
			self.base_selling_amount = self.selling_amount*conversion_rate

								
	def validate_item(self, item):
		
		if item.get("cr_type") in ["Deletion", "Modification"]:
			if not frappe.db.get_value("Sales Order Item", item.get("sales_order_item")):
				throw(_("Please select <b>Sales Order Item to be modified/subtract </b>."))
		if item.get("select_margin_type") == "Percentage" and item.get("margin_percentage") == None:
			throw(_("Please enter <b>Margin Percentage</b>"))
		elif item.get("select_margin_type") == "Amount" and item.get("margin_amount") == None:
			throw(_("Please enter <b>Margin Amount</b>"))
		

	def get_quotation_name(self):
		
		quotation_name = ""
		for item in self._so.get("items"):
			if item.get("prevdoc_docname"):
				quotation_name = item.get("prevdoc_docname")
				break
		return quotation_name

	def on_submit(self):
		tobe_removed = []
		tobe_added = []
		changed = []
		self._so = frappe.get_doc("Sales Order", self.sales_order)
		if self._so:
			for item in  self.get("items"):
				if item.get("cr_type") == "Deletion":
					self.validate_deletion_item(item)
				elif item.get("cr_type") == "Modification":
					tobe_added.append(self.get_item_tobe_add(item))
				else:
					#changed.append(self.get_item_tobe_removed(item))
					tobe_added.append(self.get_item_tobe_add(item))
				
				if item.get("cr_type") in ["Modification", "Deletion"]:
					for i in self._so.items:
						if i.get("name") == item.get("sales_order_item"):
							tobe_removed.append(i)
					changed.append(self.get_item_tobe_removed(item))

			self.update_sales_order(tobe_removed, tobe_added, changed)				

	def validate_deletion_item(self, item):
		so_item = frappe.get_doc("Sales Order Item", item.get("sales_order_item"))
		for field in  ["ordered_qty", "billed_qty", "delivered_qty", "returned_qty"]:
			if flt(so_item.get(field)) > 0.0:
				frappe.throw(_("User Item {0}, <b>Status: already {1} {2}</b>. Action <b>{3}</b> \
					cannot be performed.".format(so_item.get("item_code"), so_item.meta.get_label(field),\
					so_item.get(field), item.get("cr_type"))))
	
		
	def get_item_tobe_add(self, item):
		doc = get_mapped_doc("Sales Order Change Request Item", item.get("name"), {
			"Sales Order Change Request Item":{
				"doctype": "Sales Order Item",
				"field_map":{
					"cr_type": "item_status",
					"margin_percentage": "margin_percent",
					"parent": "sales_order_cr",
					"name": "sales_order_cr_detail",
					"quotation_detail": "quotation_item_detail",
					"prevdoc_docname": "quotation_detail",
				}
			}
		})
		return doc

	def get_item_tobe_removed(self, item):
		doc = get_mapped_doc("Sales Order Item", item.get("sales_order_item"), {
			"Sales Order Item":{
				"doctype": "Sales Order Change Item",
				"field_map":{
					"parent": "sales_order_change_request",
					"item_code": "substitute_item",
					"name": "sales_order_change_request_detail",
					"cr_type": "item_status",
					"quotation_detail": "quotation_item_detail",
					"prevdoc_docname": "quotation_detail",
					"qty": "qty"
				}
			}
		})
		frappe.msgprint(_("{0}").format(item.qty))
		return doc

	def update_sales_order(self, tobe_removed, tobe_added, changed):
	
		try:
			frappe.db.sql(""" UPDATE `tabSales Order` SET docstatus=0 WHERE name=%(so)s """, {"so": self.sales_order})
			if not self._so.changed_items:
				self._so.changed_items = []
			for item in tobe_removed:
				try:
					self._so.items.remove(item)
				except:
					pass
			for item in changed:
				self._so.append("changed_items", item)
			for item in tobe_added:
				self._so.append("items", {
					"item_code": item.item_code,
					"item_name": item.item_name,
					"description": item.description,
					"qty": item.qty,
					"uom": item.uom,
					"margin_amount": item.margin_amount,
					"select_margin_type": item.select_margin_type,
					"cost_amount": item.cost_amount,
					"selling_amount": item.selling_amount,
					"rate": item.rate,
					"warehouse": item.warehouse,
					"prevdoc_docname": item.quotation_detail,
					"quotation_detail": item.parent,
					"quotation_item_detail": item.name,
					"site": item.site,
					"margin_type": item.margin_type,
					"idx": item.idx
				})
			self._so.save()
			frappe.db.sql(""" UPDATE `tabSales Order` SET docstatus=1 WHERE name=%(so)s """, {"so": self.sales_order})
			frappe.db.commit()	

		except Exception as e:
			frappe.msgprint(_("{0}, {1}").format(e, frappe.get_traceback()))
			frappe.db.rollback()	


			
	def on_cancel(self):
		pass

