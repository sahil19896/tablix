// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt
frappe.provide("cpm.indicator");
cpm.indicator.Indicator = Class.extend({
	init: function(args){
		$.extend(this, args);
	},
	refresh: function() {
		var field = this.frm.get_docfield("strategic_objective")
		if(!this.frm.is_new())field.read_only =1;
		this.frm.refresh_fields(["strategic_objective"]);	

	},
	setup: function(){
		this.frm.add_fetch("strategic_objective", "strategic_theme", "strategic_theme");
		this.frm.add_fetch("strategic_objective", "select_series", "select_series");
		
	},
	uom: function(){
		this.frm.doc.target_value = null;
		this.frm.doc.target_percentage = null;
		this.frm.doc.target_data = null;
		this.frm.doc.base_value = null;
		this.frm.doc.base_percentage = null;
		this.frm.doc.base_data = null;
		this.frm.doc.actual_value = null;
		this.frm.doc.actual_percentage = null;
		this.frm.doc.actual_data = null;
		
		this.frm.refresh_fields([
			"target_value", "target_percentage", "target_data",
			"base_data", "base_percentage", "base_data",
			"actual_data", "actaul_percentage", "actual_data"
		]);
	}
});
cur_frm.script_manager.make(cpm.indicator.Indicator);
