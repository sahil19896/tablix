
/*
	Developer Sahil Saini
	email sahil.saini@tablix.ae

*/
frappe.provide("tablix.metabase");


tablix.metabase.Metabase = Class.extend({

	init: function(args){
	
		$.extend(this, args);
		this.make();

	},
	
	make: function(){

		this.create_iframe();

	},
	
	create_iframe: function(){

		src = frappe.boot.tablix.metabase.server_url;
		height = frappe.boot.tablix.metabase.height;
		width = frappe.boot.tablix.metabase.width;
		if(!src){
			frappe.msgprint("Please setup <b>Metabase Seting</b>");
			return;
		}
		
		this.iframe = document.createElement("iframe");
		this.iframe.id = frappe.utils.get_random(10);
		this.iframe.setAttribute("src", "https://google.com");
		this.iframe.style.width = width || "100%";
		this.iframe.style.height = height || "100%";
		var me = this;
		$(me.iframe).appendTo(me.page.wrapper);
	}

});
