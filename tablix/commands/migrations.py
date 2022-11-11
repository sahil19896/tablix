'''
	Developer Sahil Saini
	Email sahil.saini@tablix.ae
'''

import click
import frappe
from frappe.commands import pass_context, get_site
from frappe.frappeclient import FrappeClient
END_LINE = "\n"

@click.command("migrate-data")
@click.option("--doctype", help="Name of Document")
@click.option("--username", help="Name of  admin user")
@click.option("--password", help="admin password")
@click.option("--ip", help="IP Address of Server")
@click.option("--port", help="Server port number")
@click.option("--namefield", help="hold temp namefield for autoname purpose")
@click.option("--update_name", help="Update name using autoname")
@click.option("--commit", help="To Commit the Data once finished")
@click.option("--site", help="Sitename")
@click.option("--delete_prev_records", help="Delete all previous records")
@pass_context
def migrate_data(context, site, doctype, username, password, ip, port="", update_name=False, 
		namefield="", delete_prev_records=False, commit=False):
	if not site:
		site = context.get("sites")[0]
	frappe.init(site)
	frappe.connect()
	if delete_prev_records:
		_delete_prev_records(doctype)

	print("""{end}{end}Arguments{end}Doctype:{doctype}{end}Username: {username}{end}Password: {password}
		{end}IP Address: {ip}{end}Port Number: {port}{end}Update Name?: {update_name}
		{end}Name Field: {namefield}{end}""".format(**{"doctype": doctype, "username": username, "password":
		len(password)*"*", "ip": ip, "port": port, "update_name": update_name, "namefield":namefield , "end": END_LINE}))

	url = get_full_url(ip, port)
	client = get_frappe_client(url, username, password)
	try:
		data = client.get_list(doctype, limit_page_length=5000)
		for record in data:
			temp = client.get_doc(doctype, record.get("name"))
			try:
				if doctype == "Lead":
					create_lead(temp)
				elif doctype == "Customer":
					create_customer(temp)
				elif doctype == "Contact":
					create_contact(temp)
				elif doctype == "Supplier":
					create_supplier(temp)
				elif doctype == "Opportunity":
					create_opportunity(temp)
				elif doctype == "Boq Checklist":
					create_boq_checklist(temp)
				elif doctype == "Employee":
					create_employee(temp)
				elif doctype == "User":
					create_user(temp)
				else:
					create_other_resources(temp, doctype, update_name)


			except Exception as e:
				print(record.get("name"))
				print(e)
		if commit:		
			frappe.db.commit()
	except Exception as e:
		print(frappe.get_traceback())
		print(e)




def get_full_url(ip, port):
	
	url = ""
	scheme = ""
	if ip.find("http") < 0:
		url = "{scheme}://{url}".format(scheme="http", url=ip)
	else:
		url = ip
	if port:
		url = "{url}:{port}".format(url=url, port=port)
	return url

def get_frappe_client(url, username, password):
	return FrappeClient(url, username, password)


def _delete_prev_records(doctype):
	frappe.db.sql(""" DELETE FROM `tab{doctype} """.format(doctype=doctype))
	frappe.db.commit()
	print("Records Deleted")


def create_lead(lead):
	temp = lead.copy()
	lead.update({"name":  ""})
	doc = frappe.get_doc(lead)
	print(temp.get("name"))
	doc._name = temp.get("name")
	doc.contact_date = ""
	doc.customer = ""
	doc.owner = temp.get("owner")
	doc.save()	
	frappe.db.sql(""" UPDATE `tabLead` SET contact_date=%(date)s WHERE name=%(name)s """, 
			{"name": temp.get("name"), "date": temp.get("contact_date")})

def  create_customer(customer):
	temp  = customer.copy()
	customer.update({"name": "" })
	doc = frappe.get_doc(customer)
	doc._name = temp.get("name")
	doc.customer_primary_contact = ""
	doc.lead_name = ""
	doc.owner = temp.get("owner")
	doc.save()
	frappe.db.sql(""" UPDATE `tabCustomer` SET customer_primary_contact=%(contact)s WHERE name=%(name)s """,
			{"name": temp.get("name"), "contact": temp.get("customer_primary_contact")})	
		

def create_contact(contact):
	temp  = contact.copy()
	contact.update({"name": ""})
	doc = frappe.get_doc(contact)
	try:
		doc._name =  temp.get("name")
		doc.save()
	except Exception as e:
		print(e)
		doc.links = []
		doc.save()

def create_opportunity(opportunity):
	temp = opportunity.copy()
	opportunity.update({"name": ""})
	if opportunity.get("compliance") and len(opportunity.get("compliance")) >= 1:
		opportunity['compliance'] =  []
		compliance = temp.get("compliance")[0]
		compliance.update({"doctype": "Opportunity Compliance Item", "name": ""})
		opportunity['compliance'].append(frappe.get_doc(compliance).as_dict())
	try:
		doc = frappe.get_doc(opportunity)
		doc.owner = temp.get("owner")
		doc._name = temp.get("name")
		doc.flags.ignore_mandatory = True
		doc.save()
	except Exception as e:
		print(e)
		doc.customer = ""
		doc.owner = temp.get("owner")
		doc._name = temp.get("name")
		doc.lead = ""
		doc.contact_person = ""
		doc.status = "Open"
		doc.flags.ignore_mandatory = True
		doc.save()
		frappe.db.sql(""" UPDATE `tabOpportunity` SET customer=%(customer)s, lead=%(lead)s, status=%(status)s \
				 , contact_person=%(contact)s WHERE name=%(name)s """, {"name": temp.get("name"), \
				"customer": temp.get("customer"), "contact": temp.get("contact_person"), \
				"lead": temp.get("lead"), "status": temp.get("status")})		

def create_supplier(supplier):
	temp = supplier.copy()
	supplier.update({"name": ""})
	doc = frappe.get_doc(supplier)
	doc._name = temp.get("name")
	doc.save()

def create_other_resources(other, doctype, update_name=False):
	temp = other
	other.update({"name": ""})
	doc = frappe.get_doc(other)
	if update_name:
		doc.name = temp.get("name")
	doc.save()
	
			
def create_boq_checklist(checklist):
	
	temp = checklist
	checklist.update({"name": "", "doctype": "BOQ Profile Checklist"})
	if temp.get("for_doctype")=="Boq":
		checklist['for_doctype'] = "BOQ Profile"
	doc  = frappe.get_doc(checklist)

	doc.save()

# Create Employee and skip the records which have already been created.
def create_employee(emp):
	temp = emp.copy()
	if not frappe.db.get_value("Employee", {"name": emp.get("name")}):
		emp['name'] = ""
		doc = frappe.get_doc(emp)
		doc.status = "Active"
		doc._name = temp.get("name")
		try:
			doc.save()
		
		except Exception as e:
			frappe.db.sql("""UPDATE `tabUser` SET enabled=1 WHERE name=%(name)s """,
			{"name": temp.get("user_id")})
			doc.save()
			frappe.db.sql("""UPDATE `tabUser` SET enabled=0 WHERE name=%(name)s """,
			{"name": temp.get("user_id")})
			
	
		frappe.db.sql(""" UPDATE `tabEmployee` SET status=%(status)s WHERE name=%(name)s """,
			{"status": temp.get("status"), "name": temp.get("name")})
		
		
# Create User and skip the records which have already been created.
def create_user(user):
	temp = user.copy()
	if not frappe.db.get_value("User", {"name": user.get("name")}):
		user['name'] = ""
		doc = frappe.get_doc(user)
		doc.enabled = True
		doc.save()
		frappe.db.sql(""" UPDATE `tabEmployee` SET enabled=%(enabled)s WHERE name=%(name)s """,
			{"enabled": temp.get("enabled"), "name": temp.get("name")})
		
