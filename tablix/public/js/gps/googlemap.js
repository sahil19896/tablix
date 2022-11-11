/*
	Developer Sahil Saini
	Email sahil.saini@tablix.ae

*/
frappe.provide("tablix.gps");

tablix.gps.GoogleMap = Class.extend({

	init: function(args){

		$.extend(this, args);
		$("#"+this.map_id).empty();
		this.make();
	},

	make: function(){
		this.map_div = document.getElementById(this.map_id);
		this.markers = [];
		this.info_windows = [];
		this.init_map();
		
	},
	
	init_map: function(){

		var me = this;
		if(this.default_location){
			this.display_default_location();
		}
		else{
			this.display_locations(null);
			this.display_user_info();
		}
	},

	display_locations: function(loc){
		if(this.default_location){
			loc = loc.coords;
		}
		var locations = loc?[loc]:this.message.results;
		this.map = new google.maps.Map(this.map_div, {"zoom":18});
		this.create_markers(locations);
	},

	create_markers: function(locations){
		var me = this;
		$.each(locations, function(idx, val){

			var args = {
				position:{
					lat:flt(val.latitude),
					lng:flt(val.longitude),
				},
				map: me.map,
				title: val.detail? val.detail: "Current Location"
			};
			marker = new google.maps.Marker(args);
			me.set_info_window(marker, val);
			me.markers.push(marker);
		});
		temp = locations.length>= 1? locations[0]:null;
		if(temp){
			latlng = new google.maps.LatLng({lat: flt(temp.latitude), lng: flt(temp.longitude)});
			this.map.setCenter(latlng);
		}


	},
	display_default_location: function(){
		
		var args =  {}
		var me = this;
		args.callback = function(loc){
			me.display_locations(loc);
		}
		tablix.gps.utils.get_current_location(args);
	},

	display_user_info: function(){
		
		$(".user-emp-info").empty();	
		if(!this.default_location){
			$(frappe.render_template("user_info",{
				"user_info":this.message.user_info,
				"emp_info": this.message.emp_info
			})).appendTo($(".user-emp-info"));
		}
	},
	
	set_info_window: function(marker,val){
		me = this;
		var infowindow = new google.maps.InfoWindow({content: val.detail});
		marker.addListener('click', function() {
    			infowindow.open(me.map, marker);
  		});
	}

	
});


