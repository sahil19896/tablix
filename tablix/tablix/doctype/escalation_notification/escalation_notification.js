// Copyright (c) 2017, Tablix and contributors
// For license information, please see license.txt

frappe.ui.form.on('Escalation Notification', {
	refresh: function(frm) {

	}
});

frappe.provide("tablix.escalation");

tablix.escalation.EscalationNotification = Class.extend({

	init: function(args){
	
		$.extend(this, args);
	},
	refresh: function(){
		
		var me = this;
		if(me.frm.is_new()){
			return ;
		}
		this.based_on();
		if(!me.frm.custom_buttons['Send Test Notification']){
			me.frm.add_custom_button(__("Send Test Notification"), function(event){
				
				frappe.call({

					method: "tablix.tablix.doctype.escalation_notification.escalation_notification.send_notification",
					args: {doc: me.frm.doc},
					callback: function(res){
						console.log(res);
					}
				});
			}).addClass("btn-primary");
		}
	},
	based_on: function(){
		
		var me = this;
		if(me.frm.doc.based_on == "ToDo"){
			frappe.call({
				method: "tablix.tablix.doctype.escalation_notification.escalation_notification.get_field_list",
				args: {doctype: me.frm.doc.based_on},
				callback: function(res){
					if(res.message){
						
						tablix.escalation.update_fields(me.frm, res.message)
						me.frm.refresh_fields(["docfield", "datetime_field"]);
					}
				}
			})	
		}
		else{
			tablix.escalation.update_fields();
		}
		
	},
	for_doctype: function(){
		this.based_on();
	},
	
	enable_escalation: function(doc, cdt, cdn){
		
		var _frm = this.frm.fields_dict.users.grid.grid_rows_by_docname[cdn];
		_frm.refresh();	
	}

});

cur_frm.script_manager.make(tablix.escalation.EscalationNotification);

tablix.escalation.update_fields = function(frm, res){

	if(!me.frm.doc.for_doctype){
		frappe.msgprint(__("Please select For Doctype"));
		return false;
	}	
	frappe.model.with_doctype(me.frm.doc.for_doctype, function(){
			let doctype = me.frm.doc.based_on=="ToDo"? "ToDo" :me.frm.doc.for_doctype;
			let fields = res?res:frappe.get_doc("DocType", doctype).fields;
			let datetime_fields = $.map(fields, function(df){
				if(in_list(['DateTime', 'Date'], df.fieldtype)){
					return 	{value: df.fieldname, label: df.fieldname + " (" + __(df.label) + ")"};
				}
			});
			var users = $.map(fields, function(df){
				if((df.fieldtype=="Link" || df.fieldtype=="Select") && in_list(['User', 'Email'], df.options)){
					return 	{value: df.fieldname, label: df.fieldname + " (" + __(df.label) + ")"};
				}
			});
			var options = $.map(fields, function(df){
				if(in_list(frappe.model.no_value_type, df.fieldtype))
					return null;
				return 	{value: df.fieldname, label: df.fieldname + " (" + __(df.label) + ")"};
			});
			me.frm.set_df_property("docfield", "options", [""].concat(options));
			me.frm.set_df_property('datetime_field', 'options', ['', 'modified', 'creation'].concat(datetime_fields));
			frappe.meta.get_docfield("Escalation Notification Item", "user", 
				me.frm.doc.name).options = [""].concat(users)
			
			me.frm.fields_dict.users.grid.refresh();	
		});	
	

}
