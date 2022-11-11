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
			data = frappe.db.sql("""select document_name, document_type, date, policy_description 
					from `tabPolicy Document Management` where name = %s  """,(name), as_dict=True)

			if(data):
				quiz = frappe.db.sql("""select question, choice_1, choice_2, choice_3, choice_4 from `tabPolicy Questions` where parent = %s """,(name), as_dict=True)
				if(quiz):
					data.append(quiz)

				return data
		except Exception as e:
			frappe.throw(_("Error, Please Contact to your System Admin. {0}").format(e))

@frappe.whitelist()
def check_data(name):
	quiz = []
	if(name):
		try:
			quiz = frappe.db.sql("""select question, choice_1, choice_2, choice_3, choice_4, a, b, c, d from `tabPolicy Questions` where parent = %s """,(name), as_dict=True)

			return quiz
		except Exception as e:
			frappe.throw(_("Error, Please Contact to your System Admin. {0}").format(e))


@frappe.whitelist()
def submit_data(user, ref_no, sign):
	if(user and ref_no):
		try:
			doc = frappe.get_doc("Policy Document Management", {"name":ref_no})
			emp = frappe.get_doc("Employee", {"user_id": user})

			if(doc and emp):
				emp.append("document_viewed", {
					"document_name": doc.document_name,
					"ref_no": doc.name,
					"document_type": doc.document_type,
					"date": frappe.utils.nowdate()
				})

				if(sign):
					emp.signature = sign

				emp.save(ignore_permissions=True)

			msg = ("You confirm to have Read, Understood & Accepted the " + doc.document_name + " of the company. Attached the doccument for your reference. ")

			my_attachments = [frappe.attach_print(doc.doctype, doc.name, file_name=doc.name, print_format="Policy Management")]

			frappe.sendmail(recipients=[user], subject=doc.document_name, delayed=False, message=msg, attachments=my_attachments)

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

