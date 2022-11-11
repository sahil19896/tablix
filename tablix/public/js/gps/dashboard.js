/*
	Developer Sahil Saini
	Email sahil.saini@tabli.ae

*/

frappe.provide("tablix.gps");

tablix.gps.Dashboard = frappe.ui.Page.extend({

	init: function(args){
	
		$.extend(this, args);
		this.set_document_title = true;
                this.buttons = {};
                this.fields_dict = {};
                this.views = {};

                this.make();
                frappe.ui.pages[frappe.get_route_str()] = this;
	},

	make: function(){
		this._super()	
		this.render_tablix_filter()	

	},

	refresh: function(){


	},
	add_main_section: function() {
		console.log(this);
		console.log("sahil Saini");
                $(frappe.render_template("tablix_page", {})).appendTo(this.wrapper);
                if(this.single_column) {
                        // nesting under col-sm-12 for consistency
                        this.add_view("main", '<div class="row layout-main">\
                                        <div class="col-md-12 layout-main-section-wrapper">\
                                                <div class="layout-main-section"></div>\
                                                <div class="layout-footer hide"></div>\
                                        </div>\
                                </div>');
                } else {
                        this.add_view("main", '<div class="row layout-main">\
                                <div class="col-md-12 layout-main-section-wrapper">\
                                        <div class="layout-main-section"></div>\
                                        <div class="layout-footer hide"></div>\
                                </div>\
                        </div>');
                }

                this.setup_page();
        },
	render_tablix_filter: function(){
		
		$(frappe.render_template("tablix_gps_filters", {})).appendTo($(".filters"))
	}
});
