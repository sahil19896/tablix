
frappe.provide("tablix._workflow");

tablix._workflow.Workflow = Class.extend({
	
	init: function(args){
		$.extend(this, args);
	},

	refresh: function(doc){
		
	},
	document_type: function(doc, cdt, cdn){

		if(!this.frm.doc.document_type){
			frappe.msgprint(__("Please enter <b>Document Type</b>"));
			return false;
		}		
		this.setup_based_on();
	},
	setup_based_on: function(doc, cdt, cdn){
		
		var me = this;
		
		frappe.model.with_doctype(me.frm.doc.document_type, function(){


			var fields = frappe.get_doc('DocType', me.frm.doc.document_type).fields ||[];
			var user_fields = []	
			var userfields = $.map(fields, function(val){
				if(val.options == "User" || val.options == "Employee" || val.fieldtype=="Select" || val.fieldtype=="Read Only" || val.fieldtype=='Link')
					return {value:val.fieldname, label: val.label};
			});
			
			var default_fields = Array("", 
					{value: "modified_by", label:"Modified By"},
					{value:"owner", label: "Owner"}
				);
			me.frm.set_df_property("select_field", "options",default_fields.concat(userfields), me.frm.doc.name, 'transitions');
			me.frm.refresh();	
		});
	},
	based_on: function(doc, cdt, cdn){
		

		var _frm = this.frm.fields_dict.transitions.grid.grid_rows_by_docname[cdn];
		if(_frm.doc.based_on == "Field"){
			_frm.doc.employee = "";
			_frm.doc.email = "";
		}
		else{
			_frm.doc.select_field = "";
		}
			
		
		this.setup_based_on()
	},
	employee: function(doc, cdt, cdn){
		this.based_on(doc, cdt, cdn);
			
	},

});

cur_frm.script_manager.make(tablix._workflow.Workflow);
