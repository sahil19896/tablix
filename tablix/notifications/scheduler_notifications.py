
import frappe
from frappe import _, msgprint, throw
from calendar import monthrange
from frappe.utils import flt, cstr, cint, datetime, now_datetime, get_link_to_form
from frappe.desk.form.assign_to import add, clear


def send_reminder_notification(doctype):
	
	status, results = get_list(doctype)
	for item in results:
		status = item.get(item.get("status_field"))
		args  = {"reference_name": item.get("name"), "reference_type": doctype}
		fields, temp  = get_list("ToDo", args)
		if temp:
			try:
				args  = temp[0]
				if validate_notification_time(item, args, status):
					clear(doctype, item.get("name"))
					add({
						"assign_to": args.get("owner"),
						"doctype": doctype,
						"name": item.get("name"),
						"description": "<h1>Reminder Assignment</h1>" + cstr(item.get("description"))
					})
					send_reminder_email(doctype, item, args)	

			except Exception as e:
				print(frappe.get_traceback())
				print(e)

def get_list(doctype, args={}):
	status  = condition_map[doctype]
	fields = ", ".join([fname for fname in status.get("fields")])
	condition = status.get("condition")
	orderby = status.get("orderby")
	limit = status.get("limit") if status.get("limit") else ""
	return status, frappe.db.sql("""SELECT {fields} FROM `tab{doctype}` WHERE {condition} ORDER BY {orderby} {limit}""".\
			format(fields=fields,doctype=doctype, condition=condition, orderby=orderby, limit=limit), args, as_dict=True)
	
	



def send_reminder_email(doctype, doc, args):
	template = frappe.get_template("templates/email_notification/reminder_notification.html")
	full_name = frappe.db.get_value("User", args.get("owner"), "first_name")
	html = template.render({"doctype": doctype, "doc": doc, "args": args, "full_name": full_name or "", "get_link_to_form": get_link_to_form})
	subject = "{0}-{1}-{2}".format(doctype, doc.get("name"), "Reminder")
	emails = ["sahil.saini@tablix.ae"]
	
	frappe.sendmail(emails, subject=subject, message=html, reference_doctype=doctype, reference_name=doc.get("name"), \
			delayed=False)
	


def validate_notification_time(doc, args, status):
	
	flag= False
	status = "Sam Approved"
	temp = frappe.db.get_value("Escalation Notification", filters={"document_status": status,\
			 "for_doctype": "Boq"},fieldname="notify_time", as_dict=True)
	if not temp:
		return flag
	hours = temp.get("notify_time")
	diff = now_datetime() - args.get("creation")
	hours_diff, seconds_diff = divmod(diff.seconds, 3600)
	if hours_diff > cint(hours):
		flag = True
	return flag	
		
		
condition_map = {
	
	"Boq":{
		"fields": ["name", "modified", "status", "creation"],
		"condition": "status NOT IN ('Quotation', 'Cancelled')",
		"orderby": "creation ASC",
		"status_field": "status"
	},
	"ToDo":{
		"fields": ["name", "creation", "reference_name", "reference_type", "assigned_by", "owner", "description"],
		"condition": "reference_type=%(reference_type)s AND reference_name=%(reference_name)s AND status='Open'",
		"orderby": "creation DESC",
		"limit": "LIMIT 1"
	}
}
