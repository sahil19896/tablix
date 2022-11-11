
frappe.provide("tablix.controllers");

tablix.controllers.Lead = erpnext.LeadController.extend({
	init: function(args){
		$.extend(this, args);
	},
	refresh: function(doc){
		this._super();
		this.make_dialog();
		var frm = this.frm;
		frm.add_custom_button(__("Contacts"), function() {
			frappe.model.open_mapped_doc({
				method: "tablix.tablix_crm.whitelisted.make_contact",
				frm: frm
			})
				
		}, __("Make"));
	},
	onload: function(doc){
		this._super();
	}

});
var controller = tablix.controllers.Lead.extend( new tablix.manual_assign.ManualAssign);
cur_frm.script_manager.make(controller);
