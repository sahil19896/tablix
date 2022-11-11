# Copyright (c) 2019, Tablix and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _, throw

@frappe.whitelist()
def get_data(name):
	if(name):
		try:
			data = frappe.db.sql("""select memo_name, memo_type, date, memo_description 
					from `tabMemos` where name = %s  """,(name), as_dict=True)

			if(data):
				return data

		except Exception as e:
			frappe.throw(_("Error, Please Contact to your System Admin. {0}").format(e))

def submit_data(user, ref_no):
	if(user and ref_no):
		try:
			doc = frappe.get_doc("Memos", {"name":ref_no})
			emp = frappe.get_doc("Employee", {"user_id": user})

			if(doc and emp):
				emp.append("document_viewed", {
					"document_name": doc.memo_name,
					"ref_no": doc.name,
					"document_type": doc.memo_type,
					"date": frappe.utils.nowdate()
				})
				emp.save(ignore_permissions=True)

			msg = ("You confirm to have Read, Understood & Accepted the " + doc.memo_name + " of the company. Attached the doccument for your reference. ")

			my_attachments = [frappe.attach_print(doc.doctype, doc.name, file_name=doc.name, print_format="Memo")]

			frappe.sendmail(recipients=[user], subject=doc.memo_name, delayed=False, message=msg, attachments=my_attachments)

		except Exception as e:
			print(frappe.get_traceback())
			frappe.throw(_("Error, Please Contact to your System Admin. {0}").format(e))


@frappe.whitelist()
def check_accepted(user, ref_no):
	accept = []
	if(user and ref_no):
		doc = frappe.db.sql("""select accepted from `tabPolicy Employee` where email = %s and parent = %s """,(user, ref_no), as_dict= 1)	
		if(doc):
			if(doc[0]['accepted'] == 1):
				return {"accept": doc[0]['accepted']}
			else:
				frappe.db.sql("""update `tabPolicy Employee` set accepted = 1 where email = %s and parent = %s """,(user, ref_no))
				return {"accept": 0}
