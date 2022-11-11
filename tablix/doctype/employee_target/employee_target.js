// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.employee_target");
tablix.employee_target.EmployeeTarget = Class.extend({
	
	init: function(args){
		$.extend(this, args);
	},
	refresh:function(args){
		if(this.frm.is_new())return false;
		if(!this.frm.doc.target_for){
			frappe.msgprint(__("Please select target for[Opporunity, Quotation etc]"));
			return false;
		}
		this.target_for();
	},
	target_for: function(){
		var me = this;
		frappe.model.with_doctype(me.frm.doc.target_for, function(){

			let fields =  frappe.get_doc("DocType", me.frm.doc.target_for).fields;
			let user_fields  = [""];
			let form_fields = [""];
			for(var i=0;i<fields.length; i++){
				let field = fields[i];
				if(in_list(["Float", "Currency", "Int"],  field.fieldtype)){
					form_fields.push({value: field.fieldname, label: field.fieldname + "(" + field.label + ")"});
				}
				else if(in_list(['Link', 'Dynamic Link', 'Read Only'], field.fieldtype)){
					user_fields.push({value: field.fieldname, label: field.fieldname + "(" + field.label + ")"});
				}
			}
			me.frm.set_df_property("select_form_field", "options", form_fields);
			me.frm.set_df_property("select_user_field", "options", user_fields);
			
			me.frm.refresh_field("select_form_field");
			me.frm.refresh_field("select_user_field");
		});	
		
	}
});

cur_frm.script_manager.make(tablix.employee_target.EmployeeTarget);
