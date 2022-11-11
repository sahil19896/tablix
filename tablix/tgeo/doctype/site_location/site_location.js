// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.site_location");
__cur_frm = null;
tablix.site_location = tablix.geolocation.Location.extend({
	init: function(args){
		$.extend(args, {
			is_searchable:true,
			is_read_only: true,
			default_location: null
		});
		this._super(args);
	},
	callback: function(place){
		var me = this;
		
		var args = place.geometry.location.toJSON();
		args = {
			latitude: args.lat,
			longitude: args.lng
		};
		$.extend(args, {
			location_name: place.formatted_address,
			place_id: place.place_id
		});
		var flag=false;
		if(me.frm.doc.locations){
		
			for(var i=0;i<me.frm.doc.locations.length;i++){
				var temp = me.frm.doc.locations[i]
				if(temp.place_id==place.place_id){
					flag=true;	
					break;	
				}
			}
		}
		if(!flag){
			me.frm.add_child("locations", args, me.frm.doc);
		}
		me.frm.refresh();	
	}
});
cur_frm.script_manager.make(tablix.site_location)
