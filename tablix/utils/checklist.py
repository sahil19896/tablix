
import frappe
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt

STANDARD_FIELDS = ['topic_fieldname', 'check']
def update_checklist(doc, condition, filters={}, fields={}):

	#msgprint("test")
	#msgprint("fields = {0}".format(fields))
	for checklist in frappe.db.sql("""SELECT * FROM `tabBoq Checklist` WHERE enable=1 {0} ORDER BY index_of_topic ASC \
			""".format(condition), filters, as_dict=True):
		item = {}
		topic = checklist.get("topic")
		if checklist.get("topic_filters"):
			temp = {}
			filters = checklist.get("topic_filters").splitlines()
			#msgprint("filters ={0}".format(filters))
			for fltr in filters:
				temp.update({fltr:doc.get(fltr)})
			topic = topic.format(**temp)
		
		for key, val in fields.iteritems():
			item.update({key: checklist.get(val)})

		
		item.update({checklist.get("topic_fieldname"): topic, "check": checklist.get("check")})
		doc.append(checklist.get("fieldname"), item)


