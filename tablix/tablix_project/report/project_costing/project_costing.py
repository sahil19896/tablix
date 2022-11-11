# Copyright (c) 2013, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns =  get_columns(filters)
	return columns, data


def get_columns(filters=None):
	
	return [
		_("Sales Order")+":Link/Sales Order:100", _("Project")+":Link/Project:150",
		_("Sales Invoice") +":Link/Sales Invoice:100", _("Delivery Note")+":Link/Delivery Note:100",
		_("Purchase Order") +": Link/Purchase Order:100",
		_("Sales Order Item") +":Data:150", _("Purchase Order Item")+":Data:150",
		_("Sales Invoice Item")+":Data:150", _("Delivery Note Item")+":Data:150",
	]
