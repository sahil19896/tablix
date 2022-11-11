frappe.pages['sales-analytics-'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Sales Analytics',
		single_column: true
	});
	var week = [];
	for(var i=1;i<53;i++){
		week.push(i);
	}
	var filters = [
			{
			fieldname: "fiscal_year", fieldtype: "Link", options:"Fiscal Year", "reqd":1, 
			label:__("Fiscal Year"), default: frappe.sys_defaults.fiscal_year
		},
			{
			fieldname: "frequency", fieldtype: "Select", 
			options:["Weekly", "Monthly", "Quarterly"], 
			default:"Monthly",  label: __("Frequency")
		},
			{
			fieldname: "month", fieldtype: "Select", label: __("Select Month"),
			options:["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", 
			"Aug", "Sep", "Oct", "Nov", "Dec"]
		},
			{
			fieldname: "quarter", fieldtype: "Select", options:[1, 2, 3, 4],
			label: __("Select Quarter")
		},
			{
			fieldname: "week", fieldtype: "Select", options:week,
			label: __("Select Week")
		},
			{
			fieldname: "sales_target", fieldtype: "Link", options:"Sales Person Target", 
			label:__("Select Target"), reqd: 1, get_query: function(){
				return {
					filters:{
						docstatus: 1
					}
				}
			}
		}
	];
		
	var args = {
		wrapper: page,
		filters: filters,
		template: "sales_analytics",
		method: "tablix.tdashboard.pages.sales_analytics_.sales_analytics_",
	};
	new cpm.sales_analytics.SalesAnalytics(args);	
}

frappe.provide("cpm.sales_analytics");
cpm.sales_analytics.SalesAnalytics = tablix.dashboard.Dashboard.extend({
	init: function(args){
		this._super(args);
	},
	make: function(){
		this._super();
		this.share_page();
		this.template = frappe.templates.sales_card;
		this.header = frappe.templates.sales_card_header;
	},
	share_page: function(){
		var me = this;
		$(".share-page").on("click", function(event){
			frappe.msgprint(__("Working on it."));	
		});
	},
	show_more_data: function(){
		$(".prev-month-data").on("click", function(event){
			console.log($(this).attr("data-doctype"));
			return false;
		});
	},
	render_header: function(title, labels){
		var me = this;
		var sep = "";
		var cur_label = "", prev_label = "";
		if(labels.length == 2){
			cur_label = labels[0];
			prev_label = labels[1];
			sep = ": ";
		}
		else{
			cur_label = labels[0];
		}
		$(frappe.render_template(me.header, {
			prev_label: prev_label, 
			cur_label: cur_label, 
			sep:sep, title: title
		})).appendTo(".sales-analytics");
	},
	view_more_card_info: function(){
		var me = this;
		window.me = me;
		$(".sales-card").on("click", function(){
			var cur_label = $(this).attr("data-cur");
			var prev_label = $(this).attr("data-prev");
			var doctype = $(this).attr("doctype");
			frappe.call({
				method: "tablix.tdashboard.page.sales_analytics_.sales_analytics_.get_more_data",
				args: {"prev": prev_label, "cur": cur_label, "doctype": doctype},
				freeze:true,
				freeze_message: "Wait while fetching more detail from database",
				callback:function(res){
					console.log(res);
				}	
			});
		});
	},
	render_card: function(labels, data, field, title, type, doctype, targets){

		var me = this;
		var cur = 0.0, prev = 0.0;
		var prev_label = "", cur_label = "";
		var flag = data.length == 2?true:false;
		if(flag){
			if(typeof(field) == "object"){
				cur = flt(data[0][field[0]]/data[0][field[1]]*100, 2);	
				prev = flt(data[1][field[0]]/data[1][field[1]]*100, 2);	
			}	
			else{
				cur  = data[0][field];
				prev = data[1][field];
			}
		}
		else if(!flag && data.length){
			if(typeof(field) == "object"){
				cur = flt(data[0][field[0]]/data[0][field[1]]*100, 2);	
			}
			else{
				cur  = data[0][field];
			}
		}
		if(labels.length == 2){
			cur_label = labels[0];
			prev_label = labels[1];
		}
		else if(labels.length == 1){
			cur_label = labels[0];
		}
		
		if(type == "currency") cur = cur?format_currency(cur):0.0;
		if(type == "currency") prev = prev?format_currency(prev):0.0;
		var temp = frappe.render_template(me.template, {
			cur: cur||0.0, prev: prev || 0.0,
			title:title, prev_label: prev_label,
			cur_label: cur_label, doctype: "", target: targets
		});
		$(temp).appendTo(".sales-analytics");
		
			
	},
	handle_response: function(res, filters){
		var me = this;
		console.log(res);
		$(".sales-analytics").empty();
		google.charts.setOnLoadCallback(function(){
			me.display_target_vs_value(res, filters);
			me.display_leads_data(res, filters);
			me.display_opps_data(res, filters);
			me.display_forcast_data(res, filters);
			me.display_revenue_data(res, filters);
			me.show_more_data();
			me.view_more_card_info();
		});
	},
	display_leads_data: function(res, filters){
		var me = this;
		if(!(res && res.results.leads))return false;
		var labels = res.results.leads.labels;
		var data = res.results.leads.data;
		this.render_header("Leads Overview", labels);
		this.render_card(labels, data, "total_leads", "Total Leads Count", null, "Lead");
		this.render_card(labels, data, "lead_to_opp", "Leads to Opportunities", null, "Opportunity");
		this.render_card(labels, data, ["lead_to_opp", "total_leads"], "Conversion Rate", null);
		this.render_card(labels, data, "lead_to_quotes", "Won Leads Count", null, "Quotation");
		this.render_card(labels, data, "lead_to_so", "Won Deals Count", null, "Sales Order");
		this.render_card(labels, data, "lost_deals", "Lost Deals Count", null);
	},
	
	display_opps_data: function(res, filters){
		var me = this;
		if(!res.results.opps) return false;
		var labels = res.results.opps.labels;
		var data  = res.results.opps.data;
		this.render_header("Opportunities Overview", labels);
		this.render_card(labels, data, "total_opps", "Total Opportunities", null, "Opportunity");
		this.render_card(labels, data, "opp_to_quotes", "Opportunities to Quotes", null, "Quotation");
		this.render_card(labels, data, ["opp_to_quotes", "total_opps"], "Conversion Rate", null);
		this.render_card(labels, data, "quotes_value", "Quotation Value", "currency", "Quotation");
		this.render_card(labels, data, "opp_to_so", "Won Deals Count", null, "Sales Order");
		this.render_card(labels, data, "lost_opps", "Lost Deals Count", null);
	},
	display_forcast_data: function(res, filters){
		if(res && res.results.so_booking) this.display_booking_data(res, filters);
		if(res && res.results.so_closure) this.display_closure_data(res, filters);
		if(res && res.results.quotes) this.display_quotes_data(res, filters);
	},
	display_booking_data: function(res, filters){
		var me= this;
		var labels = res.results.so_booking.labels;
		var data = res.results.so_booking.data;
		var targets  = res.results.so_booking.targets;
		this.render_header("Forcasting Overview", labels);
		this.render_card(labels, data, "so_booking", "Sales Order Booking", "currency", "Sales Order", targets);	
	},
	display_closure_data: function(res, filters){
		var me = this;
		var labels = res.results.so_closure.labels;
		var data = res.results.so_closure.data;
		this.render_card(labels, data, "closure_total", "Expected Closure Count", null, "Sales Order");
		this.render_card(labels, data, "closure_value", "Expected Closure Value", "currency", "Sales Order");

	},
	display_quotes_data: function(res, filters){
		var me = this;
		var labels = res.results.quotes.labels;
		var data = res.results.quotes.data;
		this.render_card(labels, data, "quotes_total", "Open Quotation Count", null, "Quotation");
		this.render_card(labels, data, "quotes_value", "Open Quotation Value", "currency", "Quotation");

	},
	display_revenue_data: function(res, filters){
		if(!res.results.revenue) return false;
		var me = this;
		var labels = res.results.revenue.labels;
		var data = res.results.revenue.data;
		this.render_header("Revenue Overview", labels);
		this.render_card(labels, data, "revenue", "Revenue Overview", "currency", "Sales Invoice");
	},

	display_target_vs_value: function(res, filters){
		console.log(res);
		if(!res.results.target_vs_value) return
		var targets = {};
		var orders = {};
		var options = {};
		var color = Chart.helpers.color;
		$.extend(options, {
			title: {
				text: (String(filters.frequency)+"Target"),//format("{0}-{1}", [filters.frequency, "Target"]),
			},
			tooltips: {
				callbacks:{
					label: function(item, data){
						let target = data.datasets[0].data[item.index];
						let value  = data.datasets[1].data[item.index];
						var c = format("{0}:{1}, ",["Target",format_currency(target)]);
						var d = format("{0}:{1}",["Achieved", format_currency(value)]);
						return	c + d;
					}
				}
			}
			
		});
		$.extend(targets, {
			label: __("Targets"),
			borderColor:"green",
			backgroundColor: color("green").alpha(0.5).rgbString(),
			data: res.results.target_vs_value.targets,	
		});
		$.extend(orders, {
			label: __("Achieved"),
			borderColor:"red",
			backgroundColor: color("red").alpha(0.5).rgbString(),
			data: res.results.target_vs_value.orders,	
		});
		var config = {};
		$.extend(config, {
			type: "line",
			data:{
				labels: res.results.target_vs_value.labels,
				datasets: [targets, orders],
			},
			options: options
		});
		$(".target-vs-value").empty();
		var ele = this.create_and_get_element("canvas", "col-lg-11", "300px");
		$(ele).appendTo(".target-vs-value");	
		ele = document.getElementById(ele.id);
		var chart  = new Chart(ele, config)
	}
	
});
