// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.boq_profile_checklist");
tablix.boq_profile_checklist.Checklist = Class.extend({

	init: function(args){
		$.extend(this, args);
	},
	refresh: function(){
		var me = this;
		if (!this.frm.doc.for_doctype) return false;
		this.update_fields();
	},
	for_doctype: function(){
		
		if(!this.frm.doc.for_doctype){
			frappe.msgprint(__("Select <b>For Doctype</b>"));
			return false;
		}
		this.update_fields();
			
	},
	update_fields: function(){
		var me = this;
		frappe.model.with_doctype(me.frm.doc.for_doctype, function(event){
			let get_select_options = function(field){
				return {value:field.fieldname, label:field.fieldname + "(" + __(field.label) + ")"}
			}
			let docfields = frappe.get_doc('DocType', me.frm.doc.for_doctype).fields;
			let fields = $.map(docfields, function(field){
				console.log(field.fieldtype);
				return in_list(['Text', 'Small Text', 'Long Text', 'Data', 'Text Editor'], 
						field.fieldtype)? get_select_options(field): null;
			});
			me.frm.set_df_property("topic_fieldname", "options", fields);
			me.frm.refresh_field("topic_fieldname");
		});
	}

});


cur_frm.script_manager.make(tablix.boq_profile_checklist.Checklist);
