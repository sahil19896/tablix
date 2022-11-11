// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.mobile_log");
tablix.mobile_log = tablix.geolocation.Location.extend({
	
	init: function(args){
		
		$.extend(args,{
			is_searchable: false,
			is_read_only: true,
			default_location: cur_frm.doc
		});
		this._super(args);
	}
});


cur_frm.script_manager.make(tablix.mobile_log);
