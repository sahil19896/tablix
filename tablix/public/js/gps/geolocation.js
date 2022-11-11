/*
	Developer Sahil
	Email sahil.saini@tablix.ae
	License Tablix LLC Dubai
*/
frappe.provide("tablix.geolocation");

tablix.geolocation.Location  = Class.extend({

	init :function(args){
		$.extend(this, args);
		this.map  = null;
		this.markers = [];
		this.info_windows = [];
		this.current_location = null;
		this.make();
	},

	make: function(){
		this.set_field();
		this.init_div();
		this.load_google_map();
		
	},

	set_field: function(){
		if (!this.map_field){
			this.map_field = this.frm.get_field("google_map");
			this.$wrapper = this.map_field.$wrapper;
		}
	},

	create_search_field: function(){

		if(!this.is_searchable){
			return false;
		}
		var me = this;
		if(this.frm.doc.docstatus == 1 || !me.map){
			return false;
		}
		if(!this.map_search){
		 	me.search_input = "<input id='google-map-search' class='form-control' type='text' placeholder='Search Box'>";
			me.$wrapper.prepend(this.search_input);
			me.ele  = document.getElementById("google-map-search");
			me.search_box = new google.maps.places.SearchBox(this.ele);
			me.map.controls[google.maps.ControlPosition.TOP_LEFT].push(this.ele);
			me.map.addListener('bounds_change' , function(){
				me.search_box.setBounds(map.getBounds());
			});
			me.search_box.addListener('places_changed', function(){
					me.handle_places();
			});
			
		}
	},
	
	handle_places: function(){

		var me  = this;
		places = me.search_box.getPlaces();
		if(!places){
			frappe.msgprint("Select location has no coordinates");
			return false;
		}
		place = places[0];
		args = {}
		$.extend(args, {
			latitude: place.geometry.location.lat(),
			longitude: place.geometry.location.lng(),
			location_name: place.name,
			place_id: place.place_id
		});	
		me.draw_marker(args);
		if(me.callback){
			me.callback(place);
		}
	},
	init_div: function(){

		this.map_div = `<div class='container'>
					<div class='row'>
						<div id='google-map' style='width:100%; height:500px;' ></div>
					</div>
				</div>`;
		this.$wrapper.append(this.map_div);
			
	},
	load_google_map: function(){
		var me = this;
		_frm = cur_frm;
		load_map = me.create_map;	
		if(!window.google.maps){
                        ele = document.createElement("script");
                        lib = "libraries=places";
                        url = "https://maps.googleapis.com/maps/api/js?key={0}&callback=load_map&{1}";
                        ele.src = format(url, [frappe.boot.tablix.geo.google_api_key,lib ]);
                        $(ele).appendTo('head');

                }

	},
	create_map: function(flag){
		console.log(flag);	
		ele = document.getElementById("google-map");
		options = {}
		if(!_frm.doc.__islocal  == 1){
			locations = _frm.doc.locations;
			if(!locations|| locations.length == 0 || locations == undefined){
				_frm.cscript.setup_default_location();
				return false;
			}
			for(var i=0;i<locations.length;i++){
				var temp = locations[i];
				if(i==0){
					
					options = { 
						center:{
							lat: flt(temp.latitude),
							lng: flt(temp.longitude)
						},
						zoom:1
					};
					_frm.map = new google.maps.Map(ele, options);
					_frm.cscript.draw_marker(temp);
				}
				else{
					_frm.cscript.draw_marker(temp);
				}
				
			}
			_frm.cscript.create_search_field();
		}
		else{
			_frm.cscript.setup_default_location();
		}
	},
	draw_marker: function(args){
		if(!this.map){
			if(this.frm.map){
				this.map =  this.frm.map;
			}
			else if(!this.frm.map || !this.map){
				ele = document.getElementById("google-map");
				this.map = new google.maps.Map(ele, {});
			}
		}
		var me = this;
		var formatted_address = args.location_name?args.location_name:"No Address found";
		var place_id = null;
		var marker = new google.maps.Marker({
					position:{
						lat:flt(args.latitude),
						lng: flt(args.longitude),
					},
					map: me.map,
					title: formatted_address
		});
		var info =  new google.maps.InfoWindow({content: formatted_address || "No Info"})
		marker.addListener("click", function(){
			info.open(me.map, marker);
		});
		var position = new google.maps.LatLng(flt(args.latitude), flt(args.longitude));
		var bounds = new google.maps.LatLngBounds();
		this.markers.push(marker);
		this.info_windows.push(info);
		bounds.extend(position);
		me.map.fitBounds(bounds);
	},
	clear_markers: function(){

		var me = this;
		if(me.markers){
			$.each(me.markers, function(idx, val){
				val.setMap(null);
			});
		}
	},

	load_current_location: function(data){
		var me = this;
		me.draw_marker(data);
		if(!me.search_box){
			me.create_search_field();
		}
	},
	
	setup_default_location: function(){

		var args = {};
		var me = this;
		if(!this.default_location || this.frm.doc.__islocal==1){
			$.extend(args, {
				latitude: frappe.boot.tablix.geo.latitude,
				longitude: frappe.boot.tablix.geo.longitude,
				location_name: frappe.boot.tablix.geo.location_name,
			});
		}
		else{
			$.extend(args, {
				latitude: me.default_location.latitude,
				longitude: me.default_location.longitude,
				location_name: me.default_location.location_name,
			});	
		}
		_frm.cscript.draw_marker(args);
		_frm.cscript.create_search_field();
		
		return false;
	}
});
