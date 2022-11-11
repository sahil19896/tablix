/*
	Added By Sahil
*/

frappe.provide("tablix.leave_application");
{% include "tablix/public/js/controllers/hr/hr_controller.js" %}

tablix.leave_application.LeaveApplicationController = tablix.hr.HRController.extend({

	init: function(args){
		this._super(args);
	},
	leave_type: function(args){
		var me = this;
		if(!this.frm.doc.employee){
			frappe.msgprint(__("Please select employee"));
			return false;
		}
		frappe.call({
		
			method: "tablix.whitelisted.update_leave_approver",
			args: {emp:me.frm.doc.employee},
			callback: function(res){
				data = res.message
				me.frm.set_value("leave_approver", data["leave_approver"])
				me.frm.set_value("leave_balance_new", data["balance_leave"])
				
			}
		});


	},
	validate: function(){
		
		if(this.frm.doc.tablix_status == "Approved")
			this.status_updator("Approved", "status");
	
	}
});

cur_frm.script_manager.make(tablix.leave_application.LeaveApplicationController);
