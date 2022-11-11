/*
	Developer Sahil Saini
	Email sahil.saini@tablix.ae

*/
frappe.provide("tablix.gps");


tablix.gps.ClockAttendance = tablix.gps.Dashboard.extend({

	init:  function(args){
		$.extend(this, args);
		this.args = args;
		this._super()
	},
	make: function(){
		this._super();
		this.handler()
	},

	handler: function(){

		var me = this;
		$("#dashboard-search").on("click", function(event){
			flag = me.tablix_filters.validate_mandatory();
			if(!flag){
				return  false;
			}
			values = me.tablix_filters.get_values();
			frappe.call({
				method: "tablix.whitelisted.clock_in_clock_out_report",
				args: values,
				callback: function(res){

					console.log(res);
				}
			});
		});
	},
	draw_clock_in: function(){
	},

	draw_clock_out: function(){
	},
	
});
