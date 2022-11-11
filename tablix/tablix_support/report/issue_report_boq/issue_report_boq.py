# Copyright (c) 2013, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from tablix.tdashboard.page.issue_dashboard.issue_dashboard import get_data

def execute(filters=None):
	columns, data = [], []
	data = _get_data(filters)
	columns = get_columns()
	return columns, data



def get_columns():
	
	return [
		_("Issue Name")+":Link/Issue:100", _("Project Site")+ ":Link/Maintenance Contract:150",
		_("Failure Category")+":Data:150", _("Subject")+":Data:250",
		_("Opening Datetime")+ ":Data:175", _("Close Datetime")+ ":Data:175",
		_("Attended Datetime")+ ":Data:150", _("Rectification Datetime")+":Data:150",
		_("Open-Close-Diff")+":Data:150", _("Attend-Rectify-Diff")+":Data:150",
		
	]


def _get_data(filters):
		
	data = []
	for item in get_data(filters):
		data.append([
			item.get("name"), item.get("proj_site"), item.get("failure_cat"),
			item.get("subject"), item.get("opening_datetime"), item.get("modified"),
			item.get("attended_datetime"), item.get("rectification_datetime"),
			item.get("open_close_time"), item.get("rectified_time")
		])		

	return data	
