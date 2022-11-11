
frappe.provide("tablix.dashboard");


tablix.dashboard.Dashboard = Class.extend({
	
	init: function(args){
		$.extend(this, args);
		this.page = this.wrapper.parent.page;
		$("body").css("background-color", "#ebeff2");
		this.page_name = this.wrapper.parent.page_name;
		this.make();
	},
	make: function(){
		this.values = {};
		this.flags = {};
		this.setup_filters();
		this.render_dashboard_template();
	},
	setup_filters: function(){

		if(this.setting_filters) return;
                this.clear_filters();
                var me = this;
                $.each(me.filters || [], function(i, df) {
                        if(df.fieldtype==="Break") {
                                me.page.add_break();
                        } else {
                                var f = me.page.add_field(df);
                                $(f.wrapper).addClass("filters pull-left");
                                me.filters.push(f);

                                if(df["default"]) {
                                        f.set_input(df["default"]);
                                }
                                if(df.fieldtype=="Check") {
                                        $(f.wrapper).find("input[type='checkbox']");
                                }

                                if(df.get_query) f.get_query = df.get_query;

			if(df.on_change) f.on_change = df.on_change;
                                df.onchange = () => {
                                        if(!me.flags.filters_set) {
                                                // don't trigger change while setting filters
                                                return;
                                        }
                                        if (f.on_change) {
                                                f.on_change(me);
                                        } else {
                                                me.trigger_refresh();
                                        }
                                }
                        }
                });

                // hide page form if no filters
                var $filters = $(this.parent).find('.page-form .filters');
                $(this.parent).find('.page-form').toggle($filters.length ? true : false);

                //  set the field 'query_report_filters_by_name' first as they can be used in
                //     setting/triggering the filters
		this.setting_filters = true;
                this.setting_filters = false;

                this.flags.filters_set = true;	
		this.trigger_refresh();
	},
	clear_filters: function(){
	},
	render_dashboard_template: function(){
		var me = this;
		if(this.template){
			$(frappe.render_template(me.template, {dashboard:me})).appendTo(me.page.wrapper.find(".page-content"));	
		}
	},
	set_values: function(){
		
		var me = this;
		$.each(me.page.fields_dict, function(key, val){
				me.values[key] = val.value;
		});
		
	},
	_refresh: function(val){
		var me = this;
		if(!this.request_refresh){
			this.request_refresh = setTimeout(() => {
				me.get_data();
				me.request_refresh=null;	
			}, 300);	
		}
	},	
	trigger_refresh: function(){
		this.set_values();
		this._refresh();
		
	},
	get_data: function(){
		var me = this;
		frappe.call({
			method: "tablix.tdashboard.dashboard.get_data",
			args: {filters: me.values, page_name: me.page_name},
			callback: function(res){
				if(me.handle_response){
					me.handle_response(res, me.values);
				}
			}
		
		})
	},
	get_combo_chart_options: function(title, lines, type, res){

		var options = {};

		$.extend(options, {
			title: title,
			seriesType: 'bars',
			series:{
				lines:{type: type}
			},
			vAxis: res.results.vaxis|| {},
			hAxis: res.results.haxis||{},
		});	
	
		return options;
	},
	get_gauge_options :function(title, redarr, yellowarr){
			
		var options = {};
		$.extend(options, {
			title: title,
			redFrom: redarr[0], redTo: redarr[1],
			yellowFrom: yellowarr[0], yellowTo: yellowarr[1],
		});
		return options;

	}, 
	create_and_get_element: function(ele_name, cls, height){
	
		var me = this;
		var ele = document.createElement(ele_name);
		ele.id = frappe.utils.get_random(10);
		if(cls){
			ele.setAttribute("class", cls);
		}
		ele.setAttribute("style", "margin-bottom:5px;");
		if(height){
			ele.style.height = height || "600px";
		}
		return ele;
	}
	
});
