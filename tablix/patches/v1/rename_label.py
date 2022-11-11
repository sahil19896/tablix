
import frappe

def execute():
	
	frappe.db.sql(""" UPDATE `tabCustom Field` SET label="Amount in Words" WHERE fieldname="amt_words" AND dt="Journal Entry" """)
