
'''
	Added by Sahil
	Email sahil.saini@tablix.ae
'''

import frappe
from frappe import _, msgprint, throw
from tablix.notifications.notification_controller import NotificationController

class MasterController(NotificationController):

	def __init__(self, doc, doctype, method):
		self.doc = doc
		self.dt =  doctype
		self.doctype = doctype
		self.method = method
		self.setting = frappe.get_doc("Tablix Setting", "Tablix Setting")
	
	def validate(self):
		self.send_notification()


