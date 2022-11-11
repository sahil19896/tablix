// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("cpm.strategic_theme");
cpm.strategic_theme.StrategicTheme = Class.extend({

	init: function(args){
		$.extend(this, args);	
	},
	refresh: function(){
		var field = this.frm.get_docfield("select_series");
		if(!this.frm.is_new()){
			field.read_only = 1;
		}
		this.frm.refresh_field("select_series");
	}	

});
cur_frm.script_manager.make(cpm.strategic_theme.StrategicTheme);
