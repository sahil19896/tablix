
import frappe
from frappe.utils import cint, flt, cstr
from frappe import _, msgprint, throw



def update_website_context(context):
	
	context.hide_footer_signup = 1
	context.footer_image = "/assets/boq/images/footer.png"
	context.background = "/assets/boq/images/homepage.jpeg"
	#print context
	update_web_context(context)


def update_web_context(context):
	setting  = frappe.get_doc("Tablix Setting", "Tablix Setting")
	url = setting.get("api_url")
	if url:
		if url.rfind("?") != len(url) -1:
			url += "?"
	key = setting.get("google_client_api")
	script = ''' <script type="text/javascript" src="{url}key={key}"> </script> '''.format(url=url,  key=key)
	context.google = script
