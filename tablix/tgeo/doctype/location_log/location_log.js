// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.location_log");
tablix.location_log = tablix.geolocation.Location.extend({
	init: function(args){
		$.extend(args, {
			default_location:me.frm.doc
		});	
		this._super(args);	
	}
});
cur_frm.script_manager.make(tablix.location_log);
