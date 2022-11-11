// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.sales_order_summary");

tablix.sales_order_summary.SalesOrderSummary = Class.extend({

	init: function(args){
		$.extend(this, args);
	},

	sales_order: function(){
			var me = this;
			var so = me.frm.doc.sales_order;
			frappe.call({
				"method": "tablix.tablix_selling.doctype.sales_order_summary.sales_order_summary.get_so_data",
				"args": {"name": so},
				"callback": function(r){
					if(r){
						console.log(r);
						var data = r.message;
						var sos = me.frm.doc;
						for(i=0;i<data.length;i++){
							$.extend(sos, {
								"account_manager": data[i].account_manager,
								"margin_amount": data[i].total_margin_amount,
								"selling_price": (data[i].total_cost_amount+data[i].total_margin_amount),
								"cost_price": data[i].total_cost_amount,
								"margin_percentage": data[i].total_margin_percent,
								"bdm": data[i].bdm,
								"area": data[i].area,
								"customer": data[i].customer,
								"expected_end_date": data[i].delivery_date,
								"expected_start_date": data[i].transaction_date,
								"project": data[i].title,
								"po_no": data[i].po_no,
								"project_manager": data[i].manager_service_delivery					
							});
						}
						me.frm.refresh();
					}
				}
			});
	},

	onload: function(){
		var me = this;
		this.frm.set_query("project", function(){
			return {
				filters:{
					"sales_order": me.frm.doc.sales_order
				}
			}
		});

		this.frm.set_query("boq_profile", function(){
			return {
				"query" : "tablix.whitelisted.get_boq",
				"filters": {
					"order": me.frm.doc.sales_order
				}
			}	
		});
	},
});

cur_frm.script_manager.make(tablix.sales_order_summary.SalesOrderSummary);
 
