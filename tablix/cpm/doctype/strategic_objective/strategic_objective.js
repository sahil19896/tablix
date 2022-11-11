// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt
frappe.provide("cpm.strategic_objective");
cpm.strategic_objective.StrategicObjective = Class.extend({
	init: function(args) {
		$.extend(this, args);
	},
	refresh :function(){
		var field = this.frm.get_docfield("strategic_theme");
		if(!this.frm.is_new()) field.read_only =1;
		this.frm.refresh_field("strategic_theme");
	},
	setup: function(){
		this.frm.add_fetch("strategic_theme", "select_series", "select_series");
	}	
});

cur_frm.script_manager.make(cpm.strategic_objective.StrategicObjective);
