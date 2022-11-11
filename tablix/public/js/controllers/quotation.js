
// Adding cur_frm customizations
cur_frm.get_docfield("items").allow_bulk_edit = 1;
cur_frm.add_fetch("tablix_rep", "full_name", "tablix_rep_name");
cur_frm.add_fetch("tablix_rep", "phone", "phone_number");
cur_frm.add_fetch("created_by", "full_name", "created_user_name");
cur_frm.add_fetch("customer", "image", "company_image");
cur_frm.add_fetch("customer", "logo", "logo");
cur_frm.add_fetch("assumption_sel", "terms", "assumptions");
cur_frm.add_fetch("system_type", "system_overview", "system_overview");
cur_frm.add_fetch("system_type", "system_overview", "system_overview");
cur_frm.add_fetch("opportunity", "party_name", "party_name");
cur_frm.add_fetch("lead", "lead_name", "customer_name");
cur_frm.add_fetch("customer", "customer_name", "customer_name");

frappe.provide("tablix.controllers");
tablix.controllers.QuotationController = erpnext.selling.QuotationController.extend({

	refresh: function(doc, dt, dn){
		
		this._super(doc, dt, dn);
		this._make_sales_order();

		var me = this;
		var opp = me.frm.doc.opportunity;
                if(opp && me.frm.doc.docstatus == 0 && !me.frm.doc.zone){
			console.log("sahil is here");
			me.frm.clear_table("area_head");
                        frappe.model.get_value("Opportunity", {"name": opp}, "zone", function(r){
                                if(r){
                                        var zone = r.zone;
                                        if(zone){
                                                frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "zone", zone);
                                        }
                                }
				me.frm.refresh_field("zone");
				me.frm.refresh_field("area_head");
                        });
                }

		if(frappe.session.user_email in ["sajan.shetty@tablix.ae", "sadiq@tablix.ae", "syed.irfan@tablix.ae", "naresh.p@tablix.ae", "smc@tablix.ae", "telesales@tablix.ae"]){
			me.frm.toggle_enable("boq_discount", 0);
			me.frm.toggle_enable("amc_discount", 0);
			me.frm.toggle_enable("discount_amount", 0);
		}
	},
	modify_write_access: function(){
		if(this.frm.doc.tablix_status && this.frm.doc.tablix_status==="Designing"){
			
		}	
	},
	setup: function(){
		
		this.frm.fields_dict.items.grid.editable_fields = [
			{fieldname: "item_code", columns: 2},
			{fieldname: "brand", columns: 1},
			{fieldname: "qty", columns: 1},
			{fieldname: "cost_amount", columns: 2},
			{fieldname: "selling_amount", columns: 2},
			{fieldname: "amount", columns: 2},
			{fieldname: "margin_percent", columns: 2}
		];
		this._super();
		//this.quotation_cost = new tablix.costing.QuotationCosting({frm:this.frm});
	},
	_make_sales_order: function(){
		
		var me = this;
		if(me.frm.doc.doctype=="Quotation" && me.frm.doc.docstatus==1){
			me.frm.add_custom_button(__("Make Sales Order"), function(event){

				frappe.model.open_mapped_doc({
					method: "tablix.tablix_selling.whitelisted.make_sales_order",
					frm: me.frm
				});
			});
		}
	},
	margin_percent: function(){
		this.calculate_margin_and_total();
	},
	cost_amount: function(doc, dt, dn){
		var item = locals[dt][dn];
		item.base_cost_amount = item.cost_amount;
		this.calculate_margin_and_total();
			
	},
	selling_amount: function(doc, dt, dn){
		var item = locals[dt][dn];
		item.base_cost_amount = item.cost_amount;
		this.calculate_margin_and_total();

	},
	select_margin_type: function(doc, dt, dn){
		
		var item = locals[dt][dn];
		if(!item.select_margin_type){
			frappe.msgprint(__("Select Margin Type"));
			return false;
		}
		this.calculate_margin_and_total();		
	},
	calculate_margin_and_total: function(){

		this.frm.doc.total_cost_amount = 0.0;
		this.frm.doc.total_margin_amount = 0.0;
		this.frm.doc.base_total_cost_amount = 0.0;
		this.frm.doc.base_total_margin_amount = 0.0;
		this.frm.doc.total_margin_percent = 0.0;

		var items = this.frm.doc.items|| [];
		for(var i=0;i<items.length;i++){
			var item = items[i];
			var margin = flt(this.frm.doc.margin_percent)||0.0;
			var margin_percent = 1-(margin/100.0);
			if(item.select_margin_type=="Percentage" && item.cost_amount > 0.0  && margin_percent > 0.0){
				item.selling_amount = flt(item.cost_amount)/margin_percent;
				this.add_fractional_value(item, "selling_amount");
				item.margin_amount = item.selling_amount-item.cost_amount;
				item.margin_percent = item.margin_amount/item.selling_amount*100.0;
			}
			else if(item.select_margin_type=="Amount" && item.selling_amount > 0.0){
				item.margin_amount = item.selling_amount-item.cost_amount;
				item.margin_percent = item.margin_amount/item.selling_amount*100.0;
			}
			else{
				item.selling_amount = item.cost_amount;
				item.margin_amount = 0.0;
				item.margin_percent = 0.0;
			}
			item.amount = item.selling_amount * item.qty;
			item.total_cost_amount  = item.cost_amount *  item.qty;
			this.update_base_currency_costing(item);
			this.calculate_price_list_and_margin(item);
			this.update_cost_and_margin(item);
		}
		this.frm.refresh_field("items");
		this.calculate_taxes_and_totals();
		this.calculate_grand_margin_and_total();
		if(this.frm.doc.company != "Tablix Technologies Pvt. Ltd.") this.set_taxes();
	},
	add_fractional_value: function(item, field){
		var val = item[field];
	
		if(val){
			if(val % 1 != 0){
				item[field] = cint(item[field])+1;	
			}	
		}
	},
	update_base_currency_costing: function(item){
		var conversion_rate = flt(this.frm.doc.conversion_rate) || 0.0;
		if(this.frm.doc.currency != frappe.boot.sysdefaults.currency && conversion_rate >0.0){
			item.base_cost_amount = item.cost_amount*conversion_rate;
			item.base_total_cost_amount = item.total_cost_amount*conversion_rate;
			item.base_margin_amount = item.cost_amount*conversion_rate;
			item.base_selling_amount = item.selling_amount*conversion_rate;
			item.base_amount = item.amount * conversion_rate;
		}
		else{
			item.base_amount = item.amount;
			item.base_cost_amount = item.cost_amount;
			item.base_margin_amount = item.margin_amount;
			item.base_selling_amount = item.selling_amount;
			item.base_total_cost_amount = item.total_cost_amount;
		}	
	},
	calculate_price_list_and_margin: function(item){
		item.rate = item.selling_amount;
	
		if(item.price_list_rate && item.price_list_rate > 0.0){
			item.margin_type = "Percentage";
			item.rate_with_margin = item.selling_amount;
			let margin = item.selling_amount-item.price_list_rate;
			item.margin_rate_or_amount = margin/item.price_list_rate*100.0;
		}
			
	},
	update_cost_and_margin: function(item){
		var doc = this.frm.doc;
		this.frm.doc.total_cost_amount += flt(item.total_cost_amount);
		this.frm.doc.total_margin_amount += flt(item.amount)-flt(item.total_cost_amount);
		this.frm.doc.base_total_cost_amount += flt(item.base_total_cost_amount);
		console.log(item);
		this.frm.doc.base_total_margin_amount += flt(item.base_amount)-flt(item.base_total_cost_amount);
	},
	calculate_grand_margin_and_total: function(){
	
		var doc = this.frm.doc;
		if(doc.total_margin_amount){
			doc.total_margin_percent = doc.total_margin_amount/doc.total*100.0;	
		}
		
		this.frm.refresh_fields(["total_margin_percent", "total_margin_amount", "base_total_margin_amount",
				"total_cost_amount", "base_total_cost_amount",]);		
	},

	
	zone: function(){
                var me = this;
		var zone = me.frm.doc.zone;
		me.set_zone(zone);
	},
	set_zone: function(zone) {
		me.frm.clear_table("area_head");
                me.frm.refresh_fields("area_head");
                if(me.frm.doc.zone){
                        frappe.call({
                                "method": "tablix.whitelisted.get_area_head",
                                "args": {"name": zone},
                                "callback": function(r){
                                        if(r){  
                                                var data = r.message;
                                                if(data){
                                                        for(var i=0;i<data.length;i++){
                                                                var child=frappe.model.get_new_doc("Area Head", me.frm.doc,"area_head");                                                               
                                                                $.extend(child, {
                                                                        "area_head": data[i].area_head,
                                                                        "head_name": data[i].head_name
                                                                });
                                                        }
                                                        cur_frm.refresh_field("area_head");
                                                }
                                        }
                                }
                        });
                } else{ 
                        frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "area", "");
                        frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "engineer", "");
                        frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "buyer", "");
                        me.frm.clear_table("area_head");
                        me.frm.refresh_fields("area_head");
                }
        },

	onload: function(){
		var me = this;
		me.frm.fields_dict['zone'].get_query = function(doc) {
			return {
				filters: {
					"enable": 1
				}
			}
		}
	},

	before_save: function(){
		var me = this;
		if(me.frm.doc.company != "Tablix Technologies Pvt. Ltd.") {
			me.set_taxes();
			me.set_payment();
		}
		
		if(me.frm.doc.discount_amount){
			me.set_tax();
		}

		if(me.frm.doc.company == "Tablix Technologies Pvt. Ltd."){
			if(me.frm.doc.__is_local == 1){
				frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "naming_series", "QTN-IND-2021-");
			}
		}

		var opp = me.frm.doc.opportunity;
		if(opp){
			frappe.model.get_value("Opportunity", {"name": opp}, "*", function(r){
				if(r){
					if(!me.frm.doc.contact_person){
						var contact = r.contact_email;
						var mobile = r.contact_mobile;
						var contact_person = r.contact_person;
						frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "contact_person", contact_person);
						frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "contact_email", contact);
						frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "contact_mobile", mobile);
					}
				}
			});
		}
	},

	boq_discount: function(){
		var me = this;
		if(me.frm.doc.company != "Tablix Technologies Pvt. Ltd.") me.set_taxes();
	},

	amc_discount: function(){
		var me = this;
		if(me.frm.doc.company != "Tablix Technologies Pvt. Ltd.") me.set_taxes();
	},

	discount_amount: function(){
		var me = this;
		if(me.frm.doc.company != "Tablix Technologies Pvt. Ltd.") me.set_tax();
	},

	set_tax: function(){
		var me = this;
		if(me.frm.doc.taxes_and_charges == "VAT OUT 5%" && me.frm.doc.taxes.length > 1){
			var net_total = me.frm.doc.discount_amount ? me.frm.doc.total-me.frm.doc.discount_amount : me.frm.doc.total-0;
			frappe.model.set_value(me.frm.doc.taxes[1].doctype, me.frm.doc.taxes[1].name, "tax_amount", net_total*5/100);
		}
	},

	set_taxes: function(){
		var me = this;
		if(me.frm.doc.taxes_and_charges == "VAT OUT 5%" && me.frm.doc.taxes.length > 1){
			var net_total = me.frm.doc.boq_discount ? me.frm.doc.total-me.frm.doc.boq_discount : me.frm.doc.total-me.frm.doc.amc_discount;
			frappe.model.set_value(me.frm.doc.taxes[1].doctype, me.frm.doc.taxes[1].name, "tax_amount", net_total*5/100);
		}
	},

	set_payment: function(){
		var me = this;
		if(me.frm.doc.payment_schedule.length > 1){
			var schedule = me.frm.doc.payment_schedule;
			for(var j=0;j<schedule.length;j++){
				var grand = me.frm.doc.grand_total;
				frappe.model.set_value(schedule[j].doctype, schedule[j].name, "payment_amount", grand*schedule[j].invoice_portion/100);
			}
		}
	}

});
var Controller = tablix.taxes.extend_class(tablix.controllers.QuotationController);
cur_frm.script_manager.make(Controller);
cur_frm.cscript['Make Sales Order'] = function(){
	frappe.msgprint(__("Please use <b>Make Sales Order</b> button to create Sales Order. "));
	return false;
}
