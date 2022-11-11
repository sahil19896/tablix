/*
	Developer Sahil
*/

frappe.provide("tablix.hr");

tablix.hr.HRController = tablix.manual_assign.ManualAssign.extend({

	init: function(args){
		
		$.extend(this, args);
	},
	status_updator: function(_status, fieldname){

		if(this.frm.doc.hasOwnProperty(fieldname) && this.frm.doc.hasOwnProperty("tablix_status")){
			this.frm.set_value(fieldname, _status);	
			
		}
	},
	refresh: function(frm){
		this.make_dialog();
	}
		

});
