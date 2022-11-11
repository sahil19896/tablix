// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("cpm.objective");
cpm.objective.Objective = Class.extend({
	init: function(args){
		$.extend(this, args);
	},
	refresh: function(frm) {
		var field  = this.frm.get_docfield("parent_objective");
		if(!this.frm.doc.is_parent){
			field.read_only = 0;
			frm.reqd = 1;
		}
		this.frm.refresh_field("parent_objective");
	},
	setup: function(){
		var me = this;
		this.frm.set_query("parent_objective", function(){
			return {
				filters:{
					"docstatus": 1
				}
			}
		});	
	}
});

cur_frm.script_manager.make(cpm.objective.Objective);
