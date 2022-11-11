
import frappe
import json
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr
import googlemaps

KEYS_TO_DISCARD  = ['modified', 'owner', 'creation', 'doctype', 'docname']
def get_client():
	
	setting  = get_geo_setting()
	if not setting.get("google_api_key"):
		throw(_("Please add <b>API-Key</b> in <b>Geo Setting</b> to enable this feature"))

	return googlemaps.Client(key=setting.get("google_api_key"))


def get_geo_setting():
	
	setting = frappe._dict()
	for key, val in frappe.get_doc("Geo Setting", "Geo Setting").as_dict().items():
		
		if key not in KEYS_TO_DISCARD:
			setting[key] = val
	return setting
