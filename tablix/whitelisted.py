
import frappe
from frappe import msgprint, throw, _
from frappe.utils import cint, cstr, flt, money_in_words, today
from .notifications.notifications import send_approval
from frappe.model.mapper import get_mapped_doc
import json
from frappe.desk.reportview import DatabaseQuery, compress
import datetime
from calendar import monthrange

@frappe.whitelist()
def send_for_approval(doc, status, remark=""):

	if not doc or not status:
		frappe.msgprint(_("Invalid Arguments"));
		return
	if isinstance(doc, str):
		doc = frappe._dict(json.loads(doc))
	
	
	doctype = doc.get("doctype")
	if doctype == "Sales Order":
		send_notification_so(doc, status, remark)
	
	if doctype == "Purchase Order":
		send_notification_po(doc, status, remark)

	if doctype == "Material Request":
		send_notifications_mr(doc, status, remark)

	if doctype == "Opportunity":
		send_notification_opp(doc, status, remark)


@frappe.whitelist()
def make_contact(source_name, target_doc=None):
	msgprint("Test")
	target_doc = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Contact",
			"field_map": {
				"lead_name": "first_name",
				"email_id": "email_id",
				"contact_type": "type",
				"company_name": "organization_name"
			}
		}}, target_doc)

	return target_doc



'''
	Function for updating the reason for notification
'''
@frappe.whitelist()
def more_info(doc, **kwargs):
	
	if not doc:
		frappe.throw(_("Something went wrong"))
	session = {}
	if kwargs.get("session") and isinstance(kwargs.get("session"), str):
		session = json.loads(kwargs.get("session"))
		session = frappe._dict(session)
	elif isinstance(kwargs.get("session", dict)):
		session = frappe._dict(kwargs.get("session"))
	if isinstance(doc, dict):
		doc = frappe._dict(doc)
	if isinstance(doc, str):
		doc = frappe._dict(json.loads(doc))
	reason = kwargs.get("reason")
	send_approval(doc, reason=reason)


@frappe.whitelist()
def make_boq(source_name, target_doc=None):
	boq = frappe.get_doc("Opportunity", source_name)
	frappe.db.set_value("Opportunity", source_name, "tablix_status", "Boq")
	#frappe.db.set_value("Opportunity", boq.opportunity, "tablix_status", "Boq")
	doclist = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Boq",
			"field_map": {
				"account_manager": "account_manager",
				"name": "opportunity",
				"enquiry_from":"opportunity_from",
				"lead":"party_name",
				"customer":"customer",
				"project_name":"project_site_name",
				"solution":"system_type",
				"owner":"opp_owner",
				"customer_name":"customer_name"
			}
		}
	})

	return doclist


@frappe.whitelist()
def get_remaining_leaves(doc):
	
	if doc and isinstance(doc, dict):
		doc = frappe._dict(doc)
	elif doc and not isinstance(doc, dict):
		doc = frappe._dict(json.loads(doc))


	data = {}
	if not doc.get("employee"):
		msgprint(_("Select Employee name"))
		return data

	data = frappe.db.get_value("Employee", doc.get("employee"), fieldname=["total_leaves_allocated", \
					"total_leaves_consumed", "balance_leave"], as_dict=True)

@frappe.whitelist()
def get_time_diff(from_time, to_time):
	
	from .utils import get_time_diff
	return get_time_diff(to_time, from_time, in_minutes=True)


@frappe.whitelist(allow_guest=True)
def gps_location(*args, **kwargs):
	return {"sahil":"Saini"}
	save_location(*args, **kwargs)



@frappe.whitelist()
def get_gps_data(*args, **kwargs):

	from .gps.gps import get_employee_data	
	filters = frappe._dict(kwargs)
	if filters.has_key("cmd"):
		 del filters['cmd']
	return get_employee_data(filters)




@frappe.whitelist()
def clock_in_clock_out_report(*args, **kwargs):
	from .gps.gps import get_cin_cout_report
	filters = frappe._dict(kwargs)
	if filters.has_key("cmd"):
		del filters["cmd"]

	return get_cin_cout_report(filters)	


@frappe.whitelist()
def get_price_list(doc, item):
	from .controllers.boq import get_price_list
	if doc and isinstance(doc, str):
		doc = json.loads(doc)
		
	if item and isinstance(item, str):
		item = json.loads(item)

	return get_price_list(doc, item)

@frappe.whitelist()
def amount_to_words(amt, currency):	
	return money_in_words(amt, currency)	
	
	
@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	purchase_receipt = frappe.get_doc("Purchase Receipt", source_name)
	#frappe.db.set_value("Opportunity", boq.opportunity, "status", "Quotation")
	doclist = get_mapped_doc("Purchase Receipt", source_name, {
		"Purchase Receipt": {
			"doctype": "Delivery Note",
			"field_map": {
				"purchase_receipt_ref": "name",
				"customer": "customer",
				"project_ref":"project_ref"
			}
		},
		"Purchase Receipt Item": {
			"doctype": "Delivery Note Item",
			"field_map": {
				"uom": "stock_uom",
			}
		}
	})

	return doclist


@frappe.whitelist()
def download_report(doctype, fields, filters, **kwargs):
	
	if isinstance(filters, str):
		filters = json.loads(filters)

	return compress(DatabaseQuery(doctype=doctype).execute(fields=fields, filters=filters))



@frappe.whitelist()
def make_expense_je(frm, credit_info):
	
	if frm and isinstance(frm, str):
		frm = json.loads(frm)
	if credit_info and isinstance(credit_info, str):
		credit_info = json.loads(credit_info)
	if frappe.db.get_value("Journal Entry", filters={"name": frm.get("journal_entry"), "docstatus":["!=", 2]}):
		throw(_("Journal Entry {0} already created".format(frm.get("journal_entry"))))

	now  = frappe.utils.nowdate()
	user_remark = "{0}: {1}\n{2}: {3}".format(frm.get("doctype"), frm.get("name"), "Date",  now)
	je = frappe.get_doc({
			"doctype":"Journal Entry", "posting_date": now,
			"cheque_no": frm.get("name"), "cheque_date": now,
			"user_remark": user_remark})
	
	total = 0.0
	ec = frappe.get_doc("Expense Claim", frm.get("name"))
	if not je.get("accounts"):
		je.accounts = []
	idx = 0
	for expense in frm.get("expenses"):
		idx += 1
		expense_account = frappe.db.get_value("Expense Claim Account", {"company": frm.get("company"), "parent": \
					expense.get("expense_type")},["default_account"], as_dict=True)
		total += expense.get("claim_amount") or 0.0
		account = frappe.get_doc({
				"idx": idx,
				"party_type": "Employee",
				"party": frm.get("employee"),
				"cost_center": frm.get("cost_center"),
				"doctype": "Journal Entry Account",
				"parenttype": "Journal Entry",
				"parentfield": "accounts",
				"parent": je.get("name"),
				"account" :expense_account.get("default_account") or "",
				"debit_in_account_currency": expense.get("claim_amount"),
				"reference_type": "Expense Claim",
				"reference_name": expense.get("parent")
			})
		je.accounts.append(account)
	if credit_info:
		account = frappe.get_doc({
				"idx":idx,
				"cost_center": frm.get("cost_center"),
				"doctype": "Journal Entry Account",
				"parenttype": "Journal Entry",
				"parentfield": "accounts",
				"parent": je.get("name"),
				"account":credit_info.get("credit_account"),
				"credit_in_account_currency": total,
				"reference_type": "Expense Claim",
				"reference_name": expense.get("parent")
			})

		je.accounts.append(account)
	je.flags.ignore_missings = True
	je.save(ignore_permissions=True)
	frappe.db.sql("""UPDATE `tabExpense Claim` SET status='Paid', mode_of_payment="Cash", is_paid=1, journal_entry=%(je)s WHERE name=%(name)s""",\
			 {"je": je.name, "name":ec.name})

	frappe.db.commit()
	return je



@frappe.whitelist()
def manual_assign(*args, **kwargs):
        if isinstance(kwargs, str):
                kwargs = json.loads(kwargs)

        from .notifications.manual_assign import manual_assign
        return manual_assign(clr=False, **kwargs)




@frappe.whitelist()
def apply_pricing_rule(args):
	out = []
	setting =  frappe.get_doc("Tablix Setting", "Tablix Setting")
	if setting.get("ignore_pricing_rule"):
		return out

	else:
		from erpnext.accounts.doctype.pricing_rule.pricing_rule import apply_pricing_rule
		out = apply_pricing_rule(args)

	return out	
	return []


'''
	Calculate Taxes and charges for every document
'''
@frappe.whitelist()
def get_taxes_and_charges(doc, master_doctype, master_name):
	from .controllers.taxes_and_charges import  get_taxes_and_charges	
	return get_taxes_and_charges(doc, master_doctype, master_name)


@frappe.whitelist()
def update_leave_approver(emp):	
	leave_approver = frappe.db.get_value("Employee Leave Approver",{"parent":emp},"leave_approver")
	balance_leave = frappe.db.get_value("Employee",emp,"balance_leave")
	#msgprint(leave_approver)
	lst = {"leave_approver": leave_approver,"balance_leave": balance_leave}
	return lst


	
@frappe.whitelist()
def update_employee_leaves(emp):
	date_of_joining = frappe.db.get_value("Employee",emp,"date_of_joining")
	doj=str(date_of_joining)
	doj=datetime.datetime.strptime(doj, "%Y-%m-%d")
	d2=datetime.datetime.strptime(today(),"%Y-%m-%d")
	delta = 0
	while True:
		mdays = monthrange(doj.year, doj.month)[1]
		doj += datetime.timedelta(days=mdays)
		if doj <= d2:
			delta += 1
		else:
			break
			
	leaves_alloc = delta*2.5
	total_leaves_allocated = leaves_alloc
	total_leaves_consumed = frappe.db.get_value("Employee",emp,"total_leaves_consumed")
	balance_leave = leaves_alloc - total_leaves_consumed
	frappe.db.set_value("Employee", emp, "total_leaves_allocated" , total_leaves_allocated)
	frappe.db.set_value("Employee", emp, "balance_leave", balance_leave)
	frappe.db.commit()	
	return True


@frappe.whitelist()
def get_task_approver(doc):
	
	if doc and isinstance(doc, str):
		doc = json.loads(doc)
	reports_to = frappe.db.get_value("Employee", {"user_id": doc.get("assigned_to")}, "reports_to", as_dict=True)
	return frappe.db.get_value("Employee", reports_to.get("reports_to")if reports_to else "", "user_id", as_dict=True)
	
		

@frappe.whitelist()
def get_area_head(name):
	if(name):
		try:
			data = frappe.db.sql(""" select area_head, head_name from `tabArea Head` where parent = %s """,(name), as_dict=True)
			return data
		except Exception as e:
			data = []
			return data


@frappe.whitelist()
def get_boq(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	data = frappe.db.sql("""select boq_profile from `tabQuotation` where name in(select quotation_detail from `tabSales Order Item` where parent =%s) """,(filters.get("order")))
	
	if(data != None):
		return data
