
/*
 * 	Added By Sahil
 * 	
 */
frappe.provide("tablix.manual_assign")

tablix.manual_assign.ManualAssign = Class.extend({
	make_dialog: function(){

		var me = this;
		var user_info = frappe.user_info();
		var user = user_info.name;
		var title = frappe.utils.format("Assign {0} - {1}", [me.frm.doc.doctype, me.frm.doc.name]);
		this.dialog = new frappe.ui.Dialog({
			title: __(title),
			fields:[
				{reqd: 1, fieldname: "assign_to", fieldtype:"Link", options: "User",label:"Assign To"},
				{reqd: 1, fieldname: "assign_by", fieldtype: "Link", options:"User", default:user, label:"Assign By"},
				{reqd: 1, fieldname: "comment", fieldtype:"Small Text", label:"Add Comment",},
				{fieldname: "change_status", fieldtype: "Check", label: "Change Status"},
				{fieldname: "status", fieldtype: "Link", options: "Workflow State"},
				{fieldname: "is_notify", fieldtype: "Check", label: __("Notify Employee"), default:1},
				{fieldname: "doctype", fieldtype: "Data", read_only:1, default:me.frm.doctype}
			],
			primary_action_label: __("Assign"),
			primary_action: function(frm){
				var doc = me.frm.doc;
				if(me.frm.is_dirty() || me.frm.is_new()){
					frappe.msgprint("Please save the change and try again");
					return false;
				}
				me.validate_mandatory(frm);
				me.dialog.hide();
				$.extend(frm, {frm:doc});
				frm.status_field = doc.tablix_status?"tablix_status": null
				frappe.call({
					method: "tablix.whitelisted.manual_assign",
					args: frm,
					callback: function(res){
						if(res && res.message){
							frappe.msgprint("Assignment Successfull");
							me.make_comment(frm);
							me.frm.refresh();
						}
						else{
							frappe.msgprint("Something went wrong");
							return;
						}
					}
				});
			}
		});
		this.frm.add_custom_button(__("Manual Assignment"), function(){
	
			if(me.frm.doctype==="Task"){
				frappe.msgprint(__("You can't assign <b>Task</b> Manually, Please use <b>Action Button</b>"));
				return false;
			}	
			if(me.frm.is_dirty()===1){
				frappe.msgprint(__("Please save the document before <b>Manual Assignment </b>"));
				return false;
			}
			me.dialog.show();

		}).addClass("btn-secondary");	
	},
	make_comment: function(args){
		var msg  = frappe.utils.format("Assign By {0}, Assign to {1} for {2}", [1, args.assign_by, args.assign_to, args.comment]);
		this.frm.timeline.insert_comment("Assigned",  msg);
	},
	validate_mandatory: function(args){

		if(args.change_status && ! args.status){
			frappe.msgprint(_("Please select the Valid Status"));
			return false;
		}
	},

	get_status: function(){
		var doctype  = this.frm.doctype;
		var docname = this.frm.docname;
		var states = [];
		if(doctype == "Boq"){
		}
	},
});
