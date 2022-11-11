// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.solution_system");
tablix.solution_system.SolutionSystem = Class.extend({
	init: function(args){
		$.extend(this, args);	
	},
	refresh: function(frm){
		this.frm.set_df_property("parent_solution_system_type", "reqd", me.frm.doc.is_group===0);
			
	},
	is_group: function(){
		if(!this.frm.doc.is_group){
			this.frm.doc.parent_solution_system_type = "";
		}
		this.frm.refresh();
	}	
});

cur_frm.script_manager.make(tablix.solution_system.SolutionSystem);
