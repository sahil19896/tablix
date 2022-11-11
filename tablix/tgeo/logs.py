
import frappe
from frappe import _, msgprint, throw
from frappe.utils import flt, cint, cstr


class MobileLog:
	
	def __init__(self,  login_manager):
		self.login_manager = login_manager
		self.info = frappe._dict()
		self.update_info()
		self.create_new_log()		
		self.save_logs()
	
	def update_info(self):
	
		self.info.update(self.login_manager.get_location_info())
		self.info.update(self.login_manager.get_user_info())
		self.info.update(self.login_manager.get_employee_info())
		self.info.update(self.login_manager.get_device_info())


	def create_new_log(self):
	
		self.mobile_log = frappe.get_doc({
			"doctype": "Mobile Log", "user": self.info.get("email"),
			"session_id": self.info.get("user_id"), "phone": self.info.get("phone"),
			"location_name": self.info.get("addresslines"), "url": self.info.get("url"),
			"latitude": self.info.get("latitude"),"longitude": self.info.get("longitude"),
			"feature": self.info.get("feature"), "extras": self.info.get("extras"),
			"admin": self.info.get("admin"), "locality": self.info.get("locality"),
			"device_name": self.info.get("device"), "device_type": self.info.get("phone"),
			"device_imei": self.info.get("imei"),	"full_name": self.info.get("full_name")
		})

	def save_logs(self):
	
		try:
			self.mobile_log.save(ignore_permissions=True)
		except Exception as e:
			print(frappe.get_traceback())
			print("\n\n")
