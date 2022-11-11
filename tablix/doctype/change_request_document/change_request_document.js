// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.change_request");
tablix.change_request.ChangeRequest = Class.extend({
	init: function(args){
		$.extend(this, args);	
	},
	refresh: function(frm){
		this.for_document();
		var me = this;
		if(!this.frm.is_new()){
			var name = format("{0}-{1}", [this.frm.doc.for_document, this.frm.doc.for_document_name]);
			this.frm.add_custom_button(name, function(){
				frappe.set_route("Form", me.frm.doc.for_document, me.frm.doc.for_document_name);
			}).addClass("btn btn-info");
		}
		if(this.frm.doc.tablix_status= "Approved" && this.frm.doc.docstatus==0){
			cur_frm.savesubmit();
		}
	},
	for_document: function(){
		var me = this;
		if(!me.frm.doc.for_document){
			frappe.msgprint(__("Please select <b>For Document</b>"));
			return;
		}
		frappe.model.with_doctype(me.frm.doc.for_document, function(){

			let fields =  frappe.get_doc("DocType", me.frm.doc.for_document).fields;
			let temp  = [""];
			for(var i=0;i<fields.length; i++){
				let field = fields[i];
				if(in_list(["Section Break", "Colum Break", "Image", "Text", "Text Editor",
				 	"Password", "Attach Image", "Attach", "Table"],  field.fieldtype)){
					continue;
				}
				temp.push({value: field.fieldname, label: field.fieldname + "(" + field.label + ")"});
					
			}
			me.frm.set_df_property("ref_field", "options", temp);
			me.frm.refresh_field("ref_field");
		});	
	},
	change_value: function(){
		var me = this;
		if(this.frm.is_new()){
			frappe.msgprint(__("Please save the changes"));
			return false;
		}
		
		frappe.model.with_doctype(me.frm.doc.for_document, function(){
		
			let fields = frappe.get_doc("DocType", me.frm.doc.for_document).fields.filter(function(val){
											
											return val.fieldname == me.frm.doc.ref_field;			
											});
			let field = fields?fields[0]:null;
			if(!field){
				frappe.mgsprint(__("Please select the <b>Field to be change</b>"));
				return false;
			}
			let dialog  = new frappe.ui.Dialog({
					title: __("Please change the desired value"),
					fields:[{fieldname:field.fieldname, label: field.label, reqd: field.reqd, options:field.options, fieldtype: field.fieldtype}],
					primary_action: function(frm){
						
						me.frm.doc.revised_value = frm[me.frm.doc.ref_field];
						me.frm.save();
						dialog.hide();	
					},
					primary_action_label: __("Change")
		
			});
			dialog.show();
		});
	}
});

cur_frm.script_manager.make(tablix.change_request.ChangeRequest);

