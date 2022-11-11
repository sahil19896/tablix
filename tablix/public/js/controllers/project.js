/*
	Added by Sahil
	Email sahil.saini@tablix.ae
*/

frappe.provide("tablix.controllers");
tablix.controllers.ProjectController = Class.extend({


	init: function(args){
		$.extend(this, args);
	},
	
	refresh: function(){
		if(this.frm.is_new()) return false;
	
	},
	setup: function(){

		console.log(this);
	},

});

cur_frm.script_manager.make(tablix.controllers.ProjectController);
