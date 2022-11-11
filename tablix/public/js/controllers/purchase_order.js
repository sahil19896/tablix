cur_frm.add_fetch("item_code", "oem_no", "oem_no");
cur_frm.add_fetch("tablix_rep", "employee_name", "rep_name");
cur_frm.add_fetch("tablix_rep", "contact_no", "rep_phone");
cur_frm.add_fetch("tablix_rep", "user_id", "rep_email");

cur_frm.add_fetch("contact_person", "mobile_no", "contact_mobile");
cur_frm.add_fetch("material_request", "customer_order", "customer_po");
cur_frm.add_fetch("material_request", "project", "project");

cur_frm.add_fetch("delivery_contact", "employee_name", "contact_name");
cur_frm.add_fetch("delivery_contact", "contact_no", "contact_phone_no");
cur_frm.add_fetch("delivery_contact", "user_id", "contact_email_id");


frappe.provide("tablix.tablix_buying");

tablix.tablix_buying.purchase_order = erpnext.buying.PurchaseOrderController.extend({

	onload: function(frm){
		if(this.frm.doc.__islocal){
			this.frm.set_value("approval", "Open");
		}
		this._super(frm);
	},
	init: function(args){
		$.extend(this, args);
		this._super();
	},
	refresh: function(doc, cdt, cdn){
		this._super(doc, cdt, cdn);
	},
	setup: function(){
		tablix.tablix_buying.setup_queries(this.frm);
		this._super();
	},
	supplier: function(){
		var me = this;
		frappe.db.get_value("Supplier", {"name": this.frm.doc.supplier}, "is_black_listed", function(res){
				if(res && res.is_black_listed){
					frappe.msgprint(__("<h6>Black Listed Supplier.</h6"));
					return false;		
				}

		});	
		this._super();		
	},

	before_save: function(){
		var me = this;
		if(me.frm.doc.company == "Tablix Technologies Pvt. Ltd."){
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "naming_series", "PO-IND-2021-");
		}else{
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "naming_series", "PO-2021-");
		}
	}
});

// Write your code here for all the fields Queries
tablix.tablix_buying.setup_queries = function(frm){


	frm.set_query('tc_name', function () {
    		return {
       			filters: {
            			'type': 'Purchase'
        		}
   		 }
	});

}
var Controller = tablix.taxes.extend_class(tablix.tablix_buying.purchase_order)
cur_frm.script_manager.make(Controller);
