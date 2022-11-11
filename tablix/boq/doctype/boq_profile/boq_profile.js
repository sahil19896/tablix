// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt
frappe.provide("tablix.boq_profile");
tablix.boq_profile.BOQProfile = Class.extend({
	
	init: function(args){
		$.extend(this, args);
	},
	
	refresh: function(){
		var me = this;
		var opp = me.frm.doc.opportunity;
		if(opp){
			frappe.model.get_value("Opportunity", {"name":opp,}, "*", function(r){
				if(r){
					var enquiry = r.opportunity_from;
					frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "enquiry_from", enquiry);
					if(enquiry == "Lead"){
						frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "lead", r.party_name);
					} else{
						frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "customer", r.party_name);
					}
				}
			});
		}
		this.make_quotation();
	},
	is_reactive: function(){
		this.refresh();	
	},
	is_preventive: function(){
			
	},
	is_amc: function(){

		// Make some fields mandatory
		var frm = this.frm;
		this.frm.set_df_property("support_timings", "reqd", frm.doc.is_amc===1); 
		this.frm.set_df_property("type_of_support", "reqd", frm.doc.is_amc===1); 
		this.frm.set_df_property("response_commitment", "reqd", frm.doc.is_amc===1); 
		this.frm.set_df_property("resolution_commitment", "reqd", frm.doc.is_amc===1); 
		this.frm.set_df_property("amc_type", "reqd", frm.doc.is_amc===1);
	},
	is_project: function(){
		
		// Make some fields mandatory
		
		var frm = this.frm;
		this.frm.set_df_property("proposed_project_starting_time", "reqd", frm.doc.is_project===1); 
		this.frm.set_df_property("material_delivery_period", "reqd", frm.doc.is_project===1); 
		this.frm.set_df_property("mobilization_period", "reqd", frm.doc.is_project===1); 
		this.frm.set_df_property("validity_of_proposal", "reqd", frm.doc.is_project===1); 
		this.frm.set_df_property("dlp_period", "reqd", frm.doc.is_project===1); 
	},
	hide_show_sections: function(){
	
		this.frm.fields_dict['amc_detail_sb'].collapse_link.click();
		this.frm.fields_dict['reactive_maintenance_detail_sb'].collapse_link.click();
		this.frm.fields_dict['project_detail_sb'].collapse_link.click();
			
	},
	make_quotation: function(){
		var frm = this.frm;
		if(frm.is_new()) return false;
		this.frm.add_custom_button(__("Quotation"), function(){
			
			frappe.model.open_mapped_doc({
				method: "tablix.boq.whitelisted.make_quotation",
				frm: frm
			});


				
		}, __("Make"));		
	},
	goto_links: function(){
		
		if(this.is_new()) return false;
		
	},
	item_code: function(doc, dt, dn){
		this.calculate_cost();
		
	},
	qty: function(doc, dt, dn){
		
		this.calculate_cost();
	},
	margin_type: function(doc, dt, dn){
		var item = locals[dt][dn];
		if(!item.cost_amount){
			frappe.msgprint(__("Please enter Cost Amount"));
			return false;
		}
		this.calculate_total();	
	},
	selling_amount: function(doc, dt, dn){
		var item = locals[dt][dn];
		if(!item.cost_amount){
			frappe.msgprint(__("Please enter cost amount"));
			return false;
		}
		this.calculate_cost();
	},
	cost_amount: function(doc, dt, dn){
		var item = locals[dt][dn];
		if(!item.selling_amount)
			item.selling_amount = item.cost_amount;	
		this.calculate_cost();	
	},
	calculate_cost: function(){
		var items = this.frm.doc.optional_items;
		for(var i=0;i<items.length;i++){
			let item = items[i];
			if(!item.qty) item.qty = 1;
			if(item.margin_type=="Amount"){
				item.total_margin = item.selling_amount - item.cost_amount;
				item.margin_percentage = item.total_margin/item.selling_amount*100.0;	
			}
			item.total_cost_amount = flt(item.cost_amount)*flt(item.qty);
			item.total_selling_amount = flt(item.selling_amount)*flt(item.qty);
		}
		this.frm.refresh_field("optional_items");
	},


});

cur_frm.script_manager.make(tablix.boq_profile.BOQProfile);
