
'''
	Developer Sahil
	Email sahil.saini@tablix.ae
    
'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr
from .notifications import notify_employee
import json

def manual_assign(clr=True, *args, **kwargs):
        
        if not kwargs.get("comment") or not kwargs.get("assign_to") or not kwargs.get("assign_by"):
                throw(_("Mandatory Fields <b> Comment, Assign To, Assign By</b>"))

        frm = kwargs.get("frm")
        if isinstance(frm, str):
                frm = json.loads(frm)

        doc = frappe.get_doc(frm.get("doctype"), frm.get("name"))
        if doc.docstatus == 2:
                throw(_("You cannot assign <b>Cancelled</b> document. \n Please <b>Cancel and Amend</b> \
                        document then assign the document"))
        
        try:
                update_status(doc, **kwargs)
                send_email(doc, **kwargs)
                assign_to(doc, clr=clr, **kwargs)
        except Exception as e:
                print(frappe.get_traceback())
                return {"message": "Failure"}

        return {"message": "Success"}


def update_status(doc, **kwargs):
	setting  = frappe.get_doc("Tablix Setting", "Tablix Setting")
	if kwargs.get("status") and kwargs.get("status_field"):
		if not doc.get("tablix_status"):
			return
		elif doc.get("tablix_status") == kwargs.get("status"):
			throw(_("Please select different status"))

		if not setting.get("allow_change_status"):
			frappe.msgprint(_("You can't change the <b>Status</b> but you can still assign"))
			return 
		frappe.db.set_value(doc.get("doctype"), doc.get("name"), "tablix_status", kwargs.get("status"))

def send_email(doc, **kwargs):
	if not kwargs.get("is_notify") or kwargs.get("is_notify") == '0':
		return
	emails = [kwargs.get("assign_to")]
	msg = kwargs.get("comment")
	notify_employee(doc, emails, msg)

def assign_to(doc, clr=True, **kwargs):
	from frappe.desk.form.assign_to import add, clear
	if clr:
		clear(doc.get("doctype"), doc.get("name"))

	add({
		"assign_to": kwargs.get("assign_to"),
		"name": doc.get("name"),
		"doctype": doc.get("doctype"),
		"description": kwargs.get("comment")
	})
