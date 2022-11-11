// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt
frappe.provide("tablix.services_contracts")

tablix.services_contracts.ServicesContracts = Class.extend({

	init: function(args){
		
		$.extend(this, args);
	},
	
	calculate_total: function(){
		this.frm.doc.grand_total = 0.0;
		this.frm.doc.base_grand_total = 0.0;
		this.calculate_services_total();
		this.calculate_taxes_total();
		this.calculate_shipping_charges();
		this.calculate_grand_total();
		this.calculate_base_total();
	},
	calculate_services_total: function(){
		var me  = this;
		var items = me.frm.doc.items;
		me.frm.doc.services_cost = 0.0;
		me.frm.doc.base_services_cost = 0.0;
		if(!items.length) return false;
		var flag = me.frm.doc.currency == frappe.boot.sysdefaults.currency;	
		for(var i=0;i<items.length; i++){
			item = me.frm.fields_dict.items.grid.grid_rows_by_docname[items[i].name];
			if(!flag){
				item.doc.base_total_amount = flt(item.doc.total_amount) * flt(me.frm.doc.exchange_rate);
			}
			else{
				item.doc.base_total_amount = flt(item.doc.total_amount);
			
			}
			me.frm.doc.services_cost  += flt(item.doc.total_amount);
			me.frm.doc.base_services_cost += flt(item.doc.base_total_amount);
			item.refresh();
		}
		me.frm.doc.grand_total = flt(me.frm.doc.services_cost);	
		this.frm.refresh_fields(["services_cost", "base_services_cost"]);			
	},
	calculate_taxes_total: function(){
		var me = this;
		me.frm.doc.total_taxes = 0.0;
		me.frm.doc.base_total_taxes =  0.0;
		me.frm.doc.custom_duties = 0.0;
		me.frm.doc.base_custom_duties = 0.0;
		me.frm.doc.other_charges = 0.0;
		me.frm.doc.base_other_charges = 0.0;
		var items = me.frm.doc.taxes;
		if(!items.length) return false;	
		for(var i=0;i<items.length; i++){
			tax = me.frm.fields_dict.taxes.grid.grid_rows_by_docname[items[i].name];
			if(tax.doc.select_tax_type == "VAT"){
				me.frm.doc.total_charges += flt(tax.doc.tax_amount);	
			}
			else if(tax.doc.select_tax_type == "Other Charges"){
				me.frm.doc.other_charges += flt(tax.doc.tax_amount);
			}
			else if(tax.doc.select_tax_type == "Duties"){
				me.frm.doc.custom_duties_charges += flt(tax.doc.tax_amount);
			}
			me.frm.doc.grand_total += flt(tax.doc.tax_amount);
		}	
							
	},
	calculate_shipping_charges: function(){
		if(this.frm.doc.shipping_charges){
			this.frm.doc.grand_total += this.frm.doc.shipping_charges;	
		}	
	},
	calculate_grand_total: function(){
		
		if(this.frm.doc.total_discount){
			this.frm.doc.grand_total = this.frm.doc.grand_total - this.frm.doc.total_discount;
		}
	
		this.frm.refresh_fields(["grand_total", "base_grand_total"]);	
				
				
	},
	calculate_base_total: function(){
		var flag = this.frm.doc.currency == frappe.boot.sysdefaults.currency;
		doc  = this.frm.doc;
		if(!flag){
			doc.base_services_cost = doc.services_cost*doc.exchange_rate;
			doc.base_total_discount = doc.total_discount*doc.exchange_rate;
			doc.base_shipping_charges = doc.shipping_charges*doc.exchange_rate;
			doc.base_other_charges = doc.other_charges*doc.exchange_rate;
			doc.base_grand_total = doc.grand_total*doc.exchange_rate;
		}
		else{
			
			doc.base_services_cost = doc.services_cost;
			doc.base_total_discount = doc.total_discount;
			doc.base_shipping_charges = doc.shipping_charges;
			doc.base_other_charges = doc.other_charges;
			doc.base_grand_total = doc.grand_total;
		}

		this.frm.refresh_fields(["base_service_cost", "base_total_discount",
				"base_shipping_charges", "base_other_charges", "base_grand_total"]);
	},
	total_amount: function(){
		this.calculate_total();	

	},
	exchange_rate: function(){
		this.calculate_total();
	},
	total_discount: function(){
		this.calculate_total();
	},
	shipping_charges: function(){
		this.calculate_total();
	}
});


cur_frm.script_manager.make(tablix.services_contracts.ServicesContracts);
