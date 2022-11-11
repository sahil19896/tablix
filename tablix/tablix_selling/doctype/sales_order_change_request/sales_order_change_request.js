// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

// Item Table auto populate values
cur_frm.add_fetch("sales_order_item", "item_code", "sales_order_item_code");
cur_frm.add_fetch("sales_order_item", "item_name", "sales_order_item_name");
cur_frm.add_fetch("sales_order_item", "amount", "sales_order_item_selling_amount");
cur_frm.add_fetch("sales_order_item", "total_cost_amount", "sales_order_item_cost_amount");
cur_frm.add_fetch("sales_order_item", "site", "site");
cur_frm.add_fetch("sales_order_item", "warehouse", "warehouse");
cur_frm.add_fetch("sales_order_item", "cost_amount", "cost_amount")
cur_frm.add_fetch("sales_order_item", "margin_amount", "margin_amount");
cur_frm.add_fetch("sales_order_item", "qty", "qty");
cur_frm.add_fetch("sales_order_item", "delivery_date", "delivery_date");
cur_frm.add_fetch("sales_order_item", "description", "description");
cur_frm.add_fetch("sales_order_item", "conversion_factor", "conversion_factor");
cur_frm.add_fetch("sales_order_item", "idx", "idx");
// Main Form auto populate values
cur_frm.add_fetch("sales_order", "currency", "currency");
cur_frm.add_fetch("sales_order", "company", "company");
cur_frm.add_fetch("sales_order", "project", "project");

frappe.provide("tablix.sales_order_change_request");
tablix.sales_order_change_request.OrderChangeRequest = Class.extend({
	init: function(args){
		$.extend(this, args);
	},
	refresh: function(){
		var me = this;
		this.set_dynamic_labels();		
	},
	setup: function(){
		this.setup_queries();
	},
	cost_amount: function(frm, cdt, cdn){
		this.calculate_total();
	},
	qty: function(frm, cdt, cdn){
		this.calculate_total();
	},
	margin_percentage: function(doc, cdt, cdn){
		var item  = locals[cdt][cdn];
		var _frm = this.frm.fields_dict.items.grid.grid_rows_by_docname[cdn];
		if(item.margin_percentage == "Percentage"){
			this.frm.set_df_property("margin_amount", "read_only", 1, cdn, "items");
			this.frm.set_df_property("margin_percentage", "read_only", 0, cdn, "items");
		}
		else if(item.select_margin_type=="Fixed"){
			this.frm.set_df_property("margin_amount", "read_only", 0, cdn, "items");
			this.frm.set_df_property("margin_percentage", "read_only", 1, cdn, "items");
			
		}
		else{
			this.frm.set_df_property("margin_amount", "read_only", 1, cdn, "items");
			this.frm.set_df_property("margin_percentage", "read_only", 1, cdn, "items");
		
		}
		_frm.refresh_field("margin_amount");
		_frm.refresh_field("margin_percentage");
		this.calculate_total();
	},
	margin_amount: function(frm, cdt, cdn){	
		this.calculate_total();
	},
	calculate_total: function(){
		var me = this;
		this.frm.doc.cost_amount = 0.0;
		this.frm.doc.selling_amount = 0.0;
		var items = this.frm.doc.items;
		for(var i=0;i<items.length; i++){
			var item = items[i];
			if(this.validate_item_margin(item))
				this.update_item_total(item);
			var selling_diff = 0.0;
			var cost_diff = 0.0;
			if(item.cr_type == "Addition"){
				var cost_diff = flt(item.cost_amount);
				var selling_diff = flt(item.selling_amount);	
			}
			else if(item.cr_type == "Subtraction" || item.cr_type=="Modification"){
				var cost_diff = item.cost_amount - item.sales_order_item_cost_amount;
				var selling_diff = item.selling_amount - item.sales_order_item_selling_amount;
				
			}
			this.frm.doc.cost_amount += cost_diff;
			this.frm.doc.selling_amount += selling_diff;
		}
		this.frm.refresh_field("items");
	},
	update_item_total(item){
		if(item.select_margin_type=="Percentage"){
			item.margin_amount  = item.cost_amount/(1.0-(item.margin_percentage/100.0));	
		}
		else{
			item.margin_percentage = flt(item.margin_amount)/item.selling_amount*100.0;
		}
		item.selling_amount  = item.cost_amount + item.margin_amount;
		item.rate = item.selling_amount;
		item.amount  = item.selling_amount * item.qty;
		item.total_cost_amount = item.cost_amount*item.qty;
	},

	update_price_list_rate: function(){
	},
	validate_item_margin: function(item){	
		if(!item.cost_amount){
			frappe.msgprint(__("Please enter Cost Amount"));
			return false;
		}
		if(item.select_margin_type=="Percentage" && !item.margin_percentage){
			frappe.msgprint(__("Please enter Margin Percent."));
			return false;
		}
		if(item.select_margin_type=="Fixed" && !item.margin_amount){
			frappe.msgprint(__("Please enter Margin Amount."));
			return false;
		}
		if(item.margin_percentage && cint(item.margin_percentage) > 99){	
			item.margin_percentage = 0.0;
			frappe.msgprint(__("Margin/Markup Percentage can't be greater than 99."));
			return false;
		}
		return true;
		
	},	
	cr_type: function(frm, cdt, cdn){
		var me = this;
		var flag = null;
		var _frm = this.frm.fields_dict.items.grid.grid_rows_by_docname[cdn];
		flag = _frm.doc.cr_type==="Deletion"||_frm.doc.cr_type==="Modification"? true: false;
		if(!flag){
			_frm.doc.sales_order_item = "";
			_frm.doc.sales_order_item_code = "";
			_frm.doc.sales_order_item_name = "";
			_frm.doc.sales_order_item_parent = "";	
		}
		_frm.refresh();
		
	},
	select_margin_type: function(doc, cdt, cdn){
		var _frm = this.frm.fields_dict.items.grid.grid_rows_by_docname[cdn];
	},
	setup_queries: function(){
		
		var me = this;
		this.frm.set_query("sales_order", function(){
			return {
				filters: {
					docstatus:1
				}
			}
		});
		this.frm.set_query("sales_order_item", "items", function(){
			return {
				filters:{
					parent: me.frm.doc.sales_order
				}
			}	
		});
		this.frm.set_query("warehouse", "items", function(){
			return {
				filters:{
					company: me.frm.doc.company
				}
			}
		});
		this.frm.set_query("project", function(){
			return {
				filters:{
					sales_order: me.frm.doc.sales_order
				}
			}
		});
	
	},
	item_code: function(doc, cdt, cdn){
		var  me = this;
		var _frm = this.frm.fields_dict.items.grid.grid_rows_by_docname[cdn];
		if(!_frm.doc.item_code || !this.frm.doc.sales_order) {
			frappe.msgprint(__("Please select <b>Sales Order</b> and <b>Item Code</b> for current item. "));
			return false;
		}
		frappe.call({
			method: "tablix.tablix_selling.doctype.sales_order_change_request.get_item_detail.get_item_detail",
			args: {"item_code": _frm.doc.item_code, "sales_order": me.frm.doc.sales_order},
			callback: function(res){
				console.log(res);
				if(res && res.message){
					let data = res.message;
					_frm.doc.price_list_rate = data.price_list_rate;
					_frm.doc.uom = data.uom;
					//_frm.doc.qty = data.qty;
					_frm.base_price_list_rate = data.base_price_list_rate;
					_frm.doc.item_group =  data.item_group;
					_frm.doc.rate = data.rate;
					_frm.doc.amount = data.amount;
					_frm.doc.net_rate = data.net_rate;
					_frm.doc.net_amount = data.net_amount;
					me.calculate_total()	
	
				}
			}
		});	
			
	},
	set_dynamic_labels: function(){
		var me = this;
		
		this.frm.set_currency_labels(["base_cost_amount", "base_selling_amount", 
				"base_after_margin_amount", "base_before_margin_amount", "base_before_cost_amount",
				"base_after_cost_amount", "base_after_selling_amount", "base_before_selling_amount",
		], frappe.sys_defaults.currency);
		this.frm.set_currency_labels(["cost_amount", "before_cost_amount", "after_cost_amount", 
				"selling_amount", "before_selling_amount", "after_selling_amount",
				"before_margin_amount", "after_margin_amount"
		], me.frm.doc.currency);
		
		this.frm.set_currency_labels(["base_amount", "base_selling_amount", "base_cost_amount", 
				"base_margin_amount", "base_total_cost_amount","base_net_amount", 
		"base_net_rate", "base_rate"], frappe.sys_defaults.currency, "items");
		
		this.frm.set_currency_labels(["amount", "selling_amount", "cost_amount", "rate",
				"margin_amount", "total_cost_amount","net_amount", "net_rate"
		], me.frm.doc.currency, "items");
	}

});

cur_frm.script_manager.make(tablix.sales_order_change_request.OrderChangeRequest);
