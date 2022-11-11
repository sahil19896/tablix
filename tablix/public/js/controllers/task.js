

frappe.provide("tablix.task");
tablix.task.TaskController =  Class.extend({

	refresh: function() {
		
		var frm = this.frm;
		if(frm.doc.status == "Rejected"){ 
			cur_frm.set_intro(__(frm.doc.reason));
		}

		if(!frm.doc.assigned_by){
                        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "assigned_by", frappe.session.user_email);
                }

		var roles = frappe.user_roles;
		if(frm.doc.assigned_to != frappe.session.user_email && !frappe.user_roles.includes("Task Creator") == true){
			frappe.msgprint("You are not eligible to view this From.");
			window.history.back();
		}
	},
	validate: function(){
		var frm = this.frm;
		var user = [frm.doc.owner, frm.doc.assigned_to];
		console.log(user);
		if(frm.doc.status == "Assigned"){
			for(var i=0;i<user.length;i++){
				if(user[i] != undefined){
					frappe.call({
						method: "frappe.share.add",
						args: {
							doctype: "Task",
							name: frm.doc.name,
							user: user[i],
							read: 1,
							write: 1,
							share: 1,
							everyone: 0
						},
						callback: function(r) {
							if(r.message) {
								// document is shared with user
							}
						}
					});
				}
			}
		}
	},
	assigned_to: function(){
		//this.update_task_approver();	
	},
	update_task_approver: function(){
		
		var me = this;
		if(!this.frm.doc.assigned_to){
			frappe.msgprint(__("Please select <b>Assigned To Rep</b>"));
			return false;
		}
		frappe.call({

			method: "tablix.whitelisted.get_task_approver",
			args: {doc: me.frm.doc},
			callback: function(res){
				if(res && res.message){
					if(!res.message.user_id){
						frappe.msgprint(__("Please update the <b>Reports To</b> for <b>Assigned to Rep</b>,in Employee, Coordinate with HR, "));
						return false;
					}
					me.frm.set_value("task_approver", res.message.user_id);
					me.frm.refresh();
				}
				else{
					frappe.msgprint(__("Please update the <b>Reports To</b> for <b>Assigned to Rep</b>,in Employee, Coordinate with HR, "));
					return false;
			
				}
			}
		})
	},

});

cur_frm.script_manager.make(tablix.task.TaskController);
