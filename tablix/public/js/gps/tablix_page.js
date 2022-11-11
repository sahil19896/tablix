/*
	Developer Sahil Saini
	Email sahil.saini@tablix.ae

*/
frappe.provide("tablix.gps");
tablix.gps.make_page =  function(args){

	if(tablix.gps[args.cls_name]){
		return new tablix.gps[args.cls_name](args);
	}
	else{
		console.error(__("Invalid Class Name"));
	}

}

/*
	Base Dashboard class to init some default values and filters for every page
*/
tablix.gps.Dashboard = frappe.ui.Page.extend({

	init: function(){
	
		this.set_document_title = true;
                this.buttons = {};
                this.fields_dict = {};
                this.views = {};
                this.make();
                frappe.ui.pages[frappe.get_route_str()] = this;
	},
	make: function(){
		this._super();
		this.render_template();
		this.init_filters();
	},
	add_main_section: function() {
		var me = this;
                $(frappe.render_template("tablix_page", {"title":__(me.title)})).appendTo($("#body_div"));
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
	init_filters: function(){
		var me = this;
		if(this.include_filters){
			this.tablix_filters = new tablix.gps.Filters(this.args);
		}
		window.form  = this;
	},
	render_template: function(){
		var me =this;
		if(me.template){
			var args = me.template.args? me.template.args: {};
			var name =  me.template.name;
			$(frappe.render_template(name, args)).appendTo($(".tablix-page"));		
		}
	
	},

});

