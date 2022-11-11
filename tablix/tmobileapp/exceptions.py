
import frappe
import werkzeug.exceptions
class UnathorizedAccess(werkzeug.exceptions.Unauthorized):
	
	def __init__(self, description=None, response=None, msg=""):
		super().__init__(description, response)
		self.message = "Unathorized Access"
