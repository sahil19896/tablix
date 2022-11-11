
import frappe
from frappe import _, msgprint, throw
from frappe.utils import now_datetime, cint, cstr, flt
import json
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_boq_profile(source_name, target_doc=None):
	
	doclist = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "BOQ Profile",
			"field_map": {
				"account_manager": "account_manager",
				"account_manager_name": "account_manager_name",
				"account_manager_email": "account_manager_email",
				"bdm": "bdm", "is_proposal": "is_proposal",
				"is_proposal": "is_proposal",
				"bdm_name": "bdm_name",
				"bdm_email": "bdm_email",
				"name": "opportunity",
				"quotation_to":"quotation_to",
				"system_type":"system_type",
			},
		},
		"Opportunity System Item":{
			"doctype": "BOQ Profile System Type Item"
		}
	})

	return doclist

@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	
	doclist = get_mapped_doc("BOQ Profile", source_name, {
		
		"BOQ Profile":{
			"doctype": "Quotation",
			"field_map":{
				"enquiry_from": "quotation_to",
				"lead": "party_name",
				"customer": "party_name",
				"owner": "estimation_engineer"
			}
		}
	})	
	return doclist

