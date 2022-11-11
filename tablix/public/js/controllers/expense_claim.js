/*
	Developer Sahil
*/
frappe.provide("tablix.expense_claim");
	
{% include "tablix/public/js/controllers/hr/hr_controller.js" %}

tablix.expense_claim.ExpenseClaimController = tablix.hr.HRController.extend({
	
	init: function(args){
		this._super(args);
	},

	refresh: function(frm){
		this._super();
		var doc = this.frm.doc;
		this.frm.cscript.set_help(doc);	
		this.view_enteries(doc);
		this.make_payment_entry();
	},
	view_enteries: function(doc){
		if(!doc.__islocal) {
			cur_frm.toggle_enable("exp_approver", doc.approval_status=="Draft");
			cur_frm.toggle_enable("approval_status", (doc.exp_approver==frappe.session.user && doc.docstatus==0));
			
			if (doc.docstatus==0 && doc.exp_approver==frappe.session.user && doc.approval_status=="Approved")
				cur_frm.savesubmit();
			
			if (doc.docstatus===1 && doc.approval_status=="Approved") {
				/* eslint-disable */
				// no idea how `me` works here
				var entry_doctype, entry_reference_doctype, entry_reference_name;
				if(doc.__onload.make_payment_via_journal_entry){
					entry_doctype = "Journal Entry";
					entry_reference_doctype = "Journal Entry Account.reference_type";
					entry_reference_name = "Journal Entry.reference_name";
				} else {
					entry_doctype = "Payment Entry";
					entry_reference_doctype = "Payment Entry Reference.reference_doctype";
					entry_reference_name = "Payment Entry Reference.reference_name";
				}
				
				if (cint(doc.total_amount_reimbursed) > 0 && frappe.model.can_read(entry_doctype)) {
					cur_frm.add_custom_button(__('Bank Entries'), function() {
						frappe.route_options = {
							entry_route_doctype: me.frm.doc.doctype,
							entry_route_name: me.frm.doc.name,
							company: me.frm.doc.company
						};
						frappe.set_route("List", entry_doctype);
					}, __("View"));
				}
				/* eslint-enable */
			}
        	}
	},
	make_payment_entry: function(){

		var frm = this.frm;
	
		if((frm.doc.docstatus == 1 && frm.doc.status == "Unpaid" && !frm.doc.journal_entry) || (frm.doc.approval_status == "Approved")){
			cur_frm.add_custom_button(__("Journal Entry"), function(){

				var dialog = new frappe.ui.Dialog({
						title: __("Please select Credit Account"),
						fields: [
							{fieldname: "credit_account", fieldtype: "Link", options: "Account", reqd:1}
						],
						primary_action_label: __("Make"),
						primary_action: function(temp){
							frappe.call({
								method: "tablix.whitelisted.make_expense_je",
								args: {
									frm: cur_frm.doc,
									credit_info: temp
								},
								callback: function(res){
									if(res && !res.message){

										return false;	
									}
									frappe.set_route("Form", "Journal Entry", res.message.name);
								}
							});
						}
					});
				dialog.show();
						
			},__("Make"));
		}
	},
	validate: function(){

		//this.calculate_total();
		if(this.frm.doc.tablix_status == "Approved")
			this.status_updator("Approved", "approval_status");
	}
		
});

cur_frm.script_manager.make(tablix.expense_claim.ExpenseClaimController);
