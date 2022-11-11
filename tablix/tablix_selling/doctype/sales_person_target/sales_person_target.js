// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.sales_person_target");
tablix.sales_person_target.SalesPersonTarget = Class.extend({
	refresh: function(frm) {
		if(this.frm.doc.docstatus==1 && frappe.user.has_role("System Manager")){
			this.update_quarterly_target();
			this.update_weekly_target();
		}
	},
	setup :function(frm){
		var me = this;
		this.frm.set_query("parent_sales_person", function(){
			return {
				filters: {
					"is_group": true
				}
			}	
		});
		this.frm.set_query("monthly_distribution", function(){
			return {
				filters: {
					"fiscal_year": me.frm.doc.fiscal_year
				}
			}	
		});

	},
	total_amount: function(){
		var me = this;
		var targets = this.frm.doc.targets || [];
		this.frm.doc.total_target = 0.0;
		for(var i=0;i<targets.length;i++){
			this.frm.doc.total_target += flt(targets[i].total_amount);	
		}

		this.frm.refresh_field("total_target");
	},
	update_weekly_target: function(){

		var me = this;
		me.frm.add_custom_button(__("Weekly"), function(){
			frappe.call({
				method: "tablix.tablix_selling.doctype.sales_person_target.sales_person_target.update_targets",
				freeze: true,
				args: {name: me.frm.doc.name, frequency: "Weekly"},
				freeze_message: __("Please wait while we're updating .."),
				callback: function(res){
					me.frm.refresh();
				}
			});
		}, __("Update Targets"));
	},
	update_quarterly_target: function(){
		var me = this;
		me.frm.add_custom_button(__("Quarterly"), function(){
			me.show_quarterly_dialog();
		}, __("Update Targets"));
	},
	show_quarterly_dialog: function(){
		var me = this;
		var dialog = new frappe.ui.Dialog({
			title: __("Enter percentage for each Quarter"),
			fields:[
				{fieldname: "quarter1", fieldtype: "Percent", label: "Quarter 1", reqd:1},
				{fieldname: "quarter2", fieldtype: "Percent", label: "Quarter 2", reqd:1},
				{fieldname: "quarter3", fieldtype: "Percent", label: "Quarter 3", reqd:1},
				{fieldname: "quarter4", fieldtype: "Percent", label: "Quarter 4", reqd:1},
			],
			primary_action_label: __("Update"),
			primary_action: function(frm){
				var data = [];
				data.push(frm.quarter1);
				data.push(frm.quarter2);
				data.push(frm.quarter3);
				data.push(frm.quarter4);
				frappe.call({
					method: "tablix.tablix_selling.doctype.sales_person_target.sales_person_target.update_targets",
					freeze: true,
					args: {name: me.frm.doc.name, frequency: "Quarterly", data: data},
					freeze_message: __("Please wait while we're updating .."),
					callback: function(res){
						me.frm.refresh();
						dialog.hide();
					}
				});
			}
		});	
		dialog.show();
	}
});

cur_frm.script_manager.make(tablix.sales_person_target.SalesPersonTarget)

