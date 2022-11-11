
tablix.dashboard.SellingDashboard = tablix.dashboard.Dashboard.extend({


	init: function(args){
		
		this._super(args);
	},
	make: function(){
		
		this._super();
	},
	handle_response: function(res, filters){
		var me = this;
		var res = res;
		console.log(res);
		$("#sales_dashboard").empty();
		if(res && res.results){
			google.charts.setOnLoadCallback(function(){
				me.display_data(res, filters);
			});
		}
	},
	
	display_data: function(res, filters){
		this.render_total_data(res, filters);
		var me = this;
		var managers_labels = res.results.labels.managers;
		var bdms_labels = res.results.labels.bdms;
		var data = res.results.data|| {};
		
		var qt_managers_data = [managers_labels];
		var qt_bdms_data = [bdms_labels];
		var so_managers_data = [managers_labels];
		var so_bdms_data = [bdms_labels];
		// Travesing entire results
		$.each(data, function(report_type, bdms_managers){
			// Dataset Container
			managers_qt_temp = new Array(managers_labels.length);
			managers_so_temp = new Array(managers_labels.length);
			bdms_qt_temp = new Array(bdms_labels.length);
			bdms_so_temp = new Array(bdms_labels.length);
			managers_qt_temp[0]= report_type;
			managers_so_temp[0] = report_type;
			bdms_so_temp[0] = report_type;
			bdms_qt_temp[0] = report_type;
			$.each(bdms_managers, function(type, obj){
				if(type=="bdms"){
					$.each(obj, function(user, so_qt){
						console.log(user);
						if(user){
						bdms_so_temp[bdms_labels.indexOf(user)]=so_qt.so;
						bdms_qt_temp[bdms_labels.indexOf(user)]=so_qt.qt;
						}
					});
					so_bdms_data.push(bdms_so_temp);
					qt_bdms_data.push(bdms_qt_temp);		
					
				}
				if(type=="managers"){
					$.each(obj, function(user, so_qt){
						if(user){
						managers_so_temp[managers_labels.indexOf(user)]=so_qt.so;
						managers_qt_temp[managers_labels.indexOf(user)]=so_qt.qt;
						}
					});
					so_managers_data.push(managers_so_temp);
					qt_managers_data.push(managers_qt_temp);
				}
			});
						
		});
		me.draw_chart(res, "Quotation|&|Managers", qt_managers_data, filters);
		me.draw_chart(res, "Sales Order|&|Managers", so_managers_data, filters);
		me.draw_chart(res, "Quotation|&|BDMS", qt_bdms_data, filters);
		me.draw_chart(res, "Sales Order|&|BDMS", so_bdms_data, filters);

	},
	draw_chart: function(res, title, data, filters){

			
		var datatable = google.visualization.arrayToDataTable(data);
		ele = this.create_and_get_element("div", "col-lg-12", "450px");
		$(ele).appendTo("#sales_dashboard");
		ele = document.getElementById(ele.id);
		var chart  = new google.visualization.ComboChart(ele);
		chart.draw(datatable, this.get_options(res, title, filters, data));	

	},
	get_options: function(res, title, filters, data){
		
		lines = data[0].length-1;
		title = format("{0} {1}", [title, filters.report_type])	
		var default_options = this.get_combo_chart_options(title, lines, 'line', res);
		return default_options;
	},
	render_total_data: function(res, filters){
		var total = res.results.total;
		amount = total.amount;
		number = total.number;
		this.render_total_amount(amount);
		this.render_total_number(number);
			
	},
	render_total_amount: function(amount){
		var me = this;
		data = google.visualization.arrayToDataTable([
			['Documents', 'Quotation', "Sales Order"],
			['Amount', amount.qt, amount.so],
		]);
		ele = me.create_and_get_element('div', 'col-lg-6', '300px');
		$(ele).appendTo("#sales_dashboard");
		ele = document.getElementById(ele.id);
		
		var chart = new google.charts.Bar(ele);
		chart.draw(data, {
			title:"Sales Order |&| Quotation Amount",
		})
		
	},

	render_total_number: function(number){
		var me =  this;
		var data = google.visualization.arrayToDataTable([
			['Documents', 'Opportunity', 'Quotation', 'Sales Order'],
			['Numbers', number.opp, number.qt, number.so],
		]);
		ele = me.create_and_get_element("div", "col-lg-6", "300px"),
		$(ele).appendTo("#sales_dashboard");
		ele = document.getElementById(ele.id);
		var chart = new google.charts.Bar(ele);
		chart.draw(data, {
			title: 'Sales Order |&| Quotation Number',
		});			
	}
	
});
