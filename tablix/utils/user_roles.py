
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, flt, cstr 



def has_role(user, role):
	
	if frappe.db.sql("""SELECT name FROM `tabHas Role` WHERE parent=%(user)s AND role=%(role)s AND parenttype='User'""", \
			{"user": user, "role": role}):
		return True
	else:
		return False


def get_user_with_role(role):
	
	filters = {"role": role}
	return frappe.db.sql(""" SELECT role, parent AS user, parenttype FROM `tabHas Role` \
		WHERE role=%(role)s AND parenttype='User' GROUP BY parent""", filters, as_dict=True)
