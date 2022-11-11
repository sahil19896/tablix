
frappe.provide("tablix.dashboard.IssueDashboard");

tablix.dashboard.IssueDashboard = tablix.dashboard.Dashboard.extend({


	init: function(args){

		this._super(args);
	},
	make: function(){
		this._super();
	},
	handle_response: function(res, filters){
		var me = this;
		$("#issue_dashboard").empty();
		if(res && res.results){
			google.charts.setOnLoadCallback(function(){
                        	        me.display_data(res, filters);
			});
		}
	},
	display_data: function(res, filters){

		var me = this;
		// Month wise data
		var monthly_headers = ["Months", "Total Value"];
		var monthly_map_data = [monthly_headers];
		
		// Hourly Data
		var hourly_headers = ['Months', 'Less than two hours', '2-4',
				'4-16', '16-24', 'More than 24 hours', 'Others'
			];
		var hourly_map_data = [hourly_headers];
		
		$.each(res.results, function(idx, val){
			monthly_map_data.push([val.month, val.total]);
			
			var hourly = val.hourly;
			hourly_map_data.push([val.month, hourly['Less than two hours'], hourly['2-4'], 
					hourly['4-16'], hourly['16-24'], hourly['>24'], hourly['null']]);
			me.display_total_issue_category(val);	
		});

		this.display_total_issue_monthly(monthly_map_data);
		this.display_total_issue_hourly(hourly_map_data);
	},
	display_total_issue_monthly: function(monthly_map_data){
			ele = this.create_and_get_element("div", "col-lg-12", "300px")
			$(ele).appendTo("#issue_dashboard");
			datatable = new google.visualization.arrayToDataTable(monthly_map_data);
			ele = document.getElementById(ele.id);
			chart = new google.charts.Bar(ele);
			chart.draw(datatable, {title: "Monthly Total Issue Resolved", colors: frappe.boot.tablix.tdashboard.colors});	
	},

	display_total_issue_hourly: function(hourly_map_data){
			ele = this.create_and_get_element("div", "col-lg-12", "300px")
			$(ele).appendTo("#issue_dashboard");
			datatable = new google.visualization.arrayToDataTable(hourly_map_data);
			ele = document.getElementById(ele.id);
			chart = new google.charts.Bar(ele);
			chart.draw(datatable, {title: "Monthly&Hourly Total Issue Resolved"});	
			
	},
	display_total_issue_category: function(item){

			var category_headers = ["Month"]
			var category_data = [item.month];
			var category_data_map = [null, null];
			var flag = false;
			$.each(item.category, function(key, val){
				category_headers.push(key=='' || key == ' ' || key==null? "Others": key )
				category_data.push(val);
				flag = true;
			});
			if(!flag){
				return 
			}
			category_data_map[0]=category_headers;
			category_data_map[1] = category_data;
			ele = this.create_and_get_element("div", "col-lg-6", "400px")
			$(ele).appendTo("#issue_dashboard");
			datatable = new google.visualization.arrayToDataTable(category_data_map);
			ele = document.getElementById(ele.id);
			chart = new google.charts.Bar(ele);
			chart.draw(datatable, {title: "Monthly&Hourly Total Issue Resolved"});	
		
	}
}) 
