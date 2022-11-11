'''
	Added by Sahil Saini
	Email sahil.saini@tablix.ae
'''
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, cstr

class CPMController(Document):
	
	def get_next_number(self):
		num = 1
		condition = ""

		filters = {"series": self.select_series}
		if self.meta.get("name") == "Strategic Objective":
			filters.update({"theme": self.strategic_theme})
			condition += " AND strategic_theme=%(theme)s "	
		if self.meta.get("name") == "Indicator":
			filters.update({"objective": self.strategic_objective})
			condition += " AND strategic_objective=%(objective)s "	

		last_num = frappe.db.sql(""" SELECT name FROM `tab{0}` WHERE \
			select_series=%(series)s {1} ORDER BY creation  DESC LIMIT 1 \
			""".format(self.meta.get("name"), condition), filters,
			as_dict=True)

		if last_num:
			name = last_num[0].get("name")
			num = name.split(".")
			if len(num) == 2:
				num = cint(num[1])+1
			elif len(num) == 3:
				num = cint(num[2])+1
	
		return num
