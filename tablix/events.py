'''
	Developer Sahil
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt, datetime, today, get_link_to_form
from  calendar import monthrange
from .utils import update_emp_leave, get_base_server_address

def expiry_reminder():
	setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	if not setting.get("disable_notification"):
		return False
	from .controllers.hr import bulk_expiry_reminder
	bulk_expiry_reminder()


'''
	Send BOQ notification to user
'''
def send_boq_notification():
	from .notifications.scheduler_notifications import send_reminder_notification
	return send_reminder_notification("Boq")




def update_user_id(doc, method=None):
	doc.user_id = frappe.generate_hash()
	doc.save()
