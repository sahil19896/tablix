# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "Tablix"
app_title = "Tablix"
app_publisher = "Tablix"
app_description = "Customization and Enhancements"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "sahil.saini@tablix.ae"
app_version = "0.0.1"
app_license = "MIT"


fixtures = ["Custom Script", "Workflow"]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"/assets/tablix/libs/jsgrid-min.css",
        "/assets/css/tablix.min.css",
	"/assets/tablix/css/libs/tablix-dashboard-min.css"
]

app_include_js = [
	"/assets/js/tablix.min.js",
	"/assets/tablix/js/libs/metabase-min.js",
        "/assets/tablix/js/libs/geolocation-min.js",
	"https://www.gstatic.com/charts/loader.js",
	"/assets/tablix/libs/chartjs-plugin-datalabels.min.js",
        "/assets/tablix/libs/jsgrid-min.js",
	"/assets/tablix/js/libs/tablix-dashboard-min.js"
]
after_install = "tablix.installation.after_install.after_install"
before_install = "tablix.installation.before_install.before_install"

web_include_css = "/assets/tablix/css/tablix_web.css"

web_include_js = "/assets/tablix/js/tablix-web-min.js"



#on_login = "tablix.auth.verify_user_location"
# notification_config = "tablix.notifications.get_notification_config"
boot_session = "tablix.boot.update_boot"
#update_website_context = "tablix.website.website.update_website_context"
# Home Pages
# ----------


doc_events = {
	"*":{
		"validate": "tablix.controllers.base_controller.validate_controller",
		"on_submit": "tablix.controllers.base_controller.validate_controller",
		"on_cancel": "tablix.controllers.base_controller.validate_controller",
	},
	"User":{
		"after_insert": "tablix.events.update_user_id"
	}
		
}

scheduler_events = {
        #"weekly": [
        #],
	"daily":[
		"tablix.events.expiry_reminder"
	],
	"all":[
		"tablix.tablix.doctype.escalation_notification.escalation_notification._send_notification"
	],
	#"cron": {
	#	"00 01,13 * * *": [
	#		"tablix.tablix_hr.doctype.policy_document_management.policy_document_management.approver_notify",
	#		"tablix.tablix_hr.doctype.policy_document_management.policy_document_management.employee_notify"
	#	],
	#	"*/120 * * * *":[
	#		"tablix.tablix_hr.doctype.policy_document_management.policy_document_management.final_approver_notify",
	#		"tablix.tablix_hr.doctype.policy_document_management.policy_document_management.final_employee_notify"
	#	]
	#}
}

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
 	"erpnext.accounts.doctype.pricing_rule.pricing_rule.apply_pricing_rule": "tablix.whitelisted.apply_pricing_rule",
	"erpnext.controllers.accounts_controller.get_taxes_and_charges": "tablix.whitelisted.calculate_taxes_and_charges",
	"erpnext.selling.doctype.quotation.quotation.make_sales_order": "tablix.tablix_crm.whitelisted.make_sales_order"
}


default_mail_footer = """
        <span>
                Sent via
                <a class="text-muted" href="https://http://www.tablix.ae/" target="_blank">
                        Tablix
                </a>
        </span>
"""

#website_context = {
#        "favicon":      "/assets/tablix/images/tablix.png",
#        "splash_image": "/assets/tablix/images/tablixsplash.jpeg"
#}

doctype_js = {
	
	"Workflow": "public/js/controllers/workflow.js",
	"Lead": "public/js/controllers/lead.js",
	"Quotation": "public/js/controllers/quotation.js",
	"Opportunity": "public/js/controllers/opportunity.js",
	"Sales Order": "public/js/controllers/sales_order.js",
	"Sales Invoice": "public/js/controllers/sales_invoice.js",
	"Company": "public/js/controllers/company.js",
	"Purchase Receipt": "public/js/controllers/purchase_receipt.js",
	"Delivery Note": "public/js/controllers/delivery_note.js",
	"Task": "public/js/controllers/task.js",
	"Expense Claim": "public/js/controllers/expense_claim.js",
	"Contact": "public/js/controllers/contact.js",
	"Material Request": "public/js/controllers/material_request.js",
	"Project": "public/js/controllers/project.js",
	"Journal Entry": "public/js/controllers/journal_entry.js",
	"Leave Application": "public/js/controllers/leave_application.js",
	"Newsletter": "public/js/controllers/newsletter.js",
	"Purchase Order": "public/js/controllers/purchase_order.js",
	"Issue": "public/js/controllers/issue.js",
	"Purchase Invoice": "public/js/controllers/purchase_invoice.js",
	"Maintenance Contract": "public/js/controllers/maintenance_contract.js",
	"Employee": "public/js/controllers/employee.js"
}

load_doctype_meta = {
	"Quotation": "tablix.dashboard_data.quotation_dashboard",
	"Opportunity": "tablix.dashboard_data.opportunity_dashboard",
	"Sales Order": "tablix.dashboard_data.sales_order_dashboard",
}

doctype_list_js = {
	
	"Sales Order": "public/js/doctype_list/sales_order_list.js",
	"Material Request": "public/js/doctype_list/material_request_list.js",
	"Purchase Order": "public/js/doctype_list/purchase_order_list.js",
	"Opportunity": "/assets/tablix/js/doctype_list/opportunity_list.js",
	"ToDo": "public/js/doctype_list/todo_list.js",
	"Task": "public/js/doctype_list/task_list.js",
	"User": "public/js/doctype_list/user_list.js",
	"Employee": "public/js/doctype_list/employee_list.js",
	"Quotation": "public/js/doctype_list/quotation_list.js",
}
dashboard_path = [
	"tdashboard/page"
]

update_website_context = "tablix.website.update_website_context"
