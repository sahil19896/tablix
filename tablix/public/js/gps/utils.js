/*
	Developer Sahil Saini
	Email sahil.saini@tablix.ae

*/

frappe.provide("tablix.gps.utils");

var watch_list = [];
$.extend(tablix.gps.utils, {

	get_current_location: function(args){
		var options = args.options?args.options:tablix.gps.utils.get_default_args();
		if(navigator.geolocation){
		
			navigator.geolocation.getCurrentPosition(function(data){

					if(!args.callback){
						return data;
					}
					else{
						args.callback(data);	
					}
			}, tablix.gps.utils.current_location_error, options);
		}
		else{
			console.log(__("Geo location is not supported in your browser"));
		}
	},
	watch_location: function(args){
		var options = args.options?args.options:tablix.gps.utils.get_default_args();
		if(navigator.geolocation){
	
			tablix.gps.utils.clear_watch_list();	
			w_id = navigator.geolocation.watchPosition(function(data){

					if(!args.callback){
						return data;
					}
					else{
						args.callback(data);	
					}
			}, tablix.gps.utils.current_location_error, options);
		watch_list.push(w_id);	
		}
		else{
			console.log(__("Geo location is not supported in your browser"));
		}
	},

	clear_watch_list: function(){

		console.log(watch_list);
		for(var i=0; i<watch_list.length; i++){
			navigator.geolocation.clearWatch(watch_list[i]);
		}
	},	
	get_default_args: function(){

		var options = {
			enableHighAccuracy: true,
			timeout: 10000,
			maximumAge: 0
		};
	
		return options
	},
	
	current_location_error: function(data){
			
		frappe.msgprint(__("Error while getting location"));
		console.log(data);
							
	},
	helper_function: function(data){

		var data = data.coords;
		$.extend(data, frappe.user_info());
		frappe.call({
			"method":"tablix.whitelisted.gps_location",
			"args": data,
			"callback": function(res){
			console.log(res);
			}
		});
	},
	
	load_safe_google_map: function(args){
		var callback = args.callback;
	
		if(!frappe.boot.tablix.geo.__map_loaded){
			var ele = document.createElement("script");
			var url = "https://maps.googleapis.com/maps/api/js?key={0}&callback={1}";
			ele.src = format(url, [frappe.boot.tablix.geo.google_api_key, "load_map"]);
			$(ele).appendTo('head');
		}
		else{
			
		}
	}
	
});
