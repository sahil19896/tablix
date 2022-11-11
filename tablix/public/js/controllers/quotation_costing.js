/*
	Added By sahil.saini@tablix.ae
	Email sahil.saini@tablix.ae	
*/
frappe.provide("tablix.costing");
tablix.costing.QuotationCosting = Class.extend({

	init: function(args){

		$.extend(this, args);
		this.make();
			
	},
	make: function(){
		$(frappe.render_template("quotation_dashboard", {})).appendTo(".form-dashboard-wrapper");
		this.get_costing();
		this.refresh_button = $("#dashboard_refresh");
		this.make_refresh_button();
	},
	get_costing: function(){
	
		if(this.frm.doc.docstatus!=1) return false;
		var me = this;
		frappe.call({
			method: "tablix.tablix_crm.whitelisted.get_qt_cost",
			args:{
				quotation: me.frm.doc.name
			},
			callback: function(res){
				me.add_information_to_dashboard(res);
			}
		
		});
	},
	add_information_to_dashboard(res){
		var me= this;
		if(res && res.message){
			
			var purchase_info = res.message.purchase_detail.cost;
			var quotation_info = res.message.quotation_detail;
			var invoice_info = res.message.invoice_detail.sale;
			var data = {};
			var q_l = format("{0}", ["Project Cost(BOQ)",quotation_info]);
			var p_l = format("{0}", ["Purchase Cost", purchase_info]);
			var i_l = format("{0})", ["Invoice Sale", invoice_info]);
			data.labels= [q_l, p_l, i_l];
			data.datasets = [{
				label: __("Documents"),
				data:[quotation_info.cost, purchase_info, invoice_info],
				backgroundColor:["#0184A4", "#d9534f", "#5cb85c"],
				borderColor: ["white"],
				datalabels:{
					anchor: "top"
				}
			}];
			var options = {};
			options.plugins = {
				datalabels: this.get_datalabels_options()
			}
			options.legend = this.get_legend_options();

			var ctx  = document.getElementById("quotation_dashboard");
			var chart = new Chart(ctx, {
				type: "bar",
				data:data,
				options: options
			});				
		}	
	},
	make_refresh_button: function(){
		var me = this;
		this.refresh_button.on("click", function(event){
			event.preventDefault();
			$("#quotation_dashboard").empty();
			me.get_costing();	
		});
			
	},
	display_datalabel: function(context){
		let dataset = context.dataset;
		let count = context.dataset.length;
		let value = dataset.data[context.dataIndex];
		return format("{0}({1})",[value, frappe.sys_defaults.currency]);;	
	},
	get_datalabels_options: function(){
	
		var options = {
			color: 'black',
			font:{
				weight: 'bold',
			},
			borderWidth: 2,
			formatter: function(value, context){
				return format("{0}({1})", [value, frappe.sys_defaults.currency]);
			},
			display: this.display_datalabel
		};
		return options;
		
	},
	get_legend_options: function(){
		var options = {
			position: "bottom",	
		}
		return options;
	}
});
