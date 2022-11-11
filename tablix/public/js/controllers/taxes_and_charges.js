
/*
	Developer Sahil
*/

frappe.provide("tablix.taxes");
tablix.taxes.extend_class = function(_class){
	var Controller;
	if(_class){
		Controller = _class.extend(new tablix.taxes.TaxesCharges());
		return Controller;
	}
}
tablix.taxes.TaxesCharges = tablix.manual_assign.ManualAssign.extend({

	init: function(args){
		$.extend(this, args);
	},
	setup: function(){
		this._super();
		var args = {
			frm: this.frm,
			grid: this.frm.fields_dict.items,
		}
		this.duplicate_row = new tablix.duplicate.DuplicateRow(args);
	},
	refresh: function(frm, cdt, cdn){

		this._super(frm, cdt, cdn);
		this.make_services_contracts();
		this.make_dialog();
	},
	taxes_and_charges: function() {
		var me = this;
		if(this.frm.doc.taxes_and_charges) {
			return this.frm.call({
				method: "tablix.whitelisted.get_taxes_and_charges",
				args: {
					"doc": me.frm.doc,
					"master_doctype": frappe.meta.get_docfield(this.frm.doc.doctype, "taxes_and_charges",
						this.frm.doc.name).options,
					"master_name": this.frm.doc.taxes_and_charges,
				},
				callback: function(r) {
					if(!r.exc) {
						me.apply_custom_taxes_and_charges(r);
					}
				}
			});
		}
	},
	apply_custom_taxes_and_charges: function(res){
		if(res && res.message){
			this.frm.set_value("taxes", res.message);

		}
		this.calculate_taxes_and_totals();
		this.calculate_taxes_and_duties();
	},

	is_sales: function(){
		
		var flag = false;
		if(frappe.boot.tablix.tablix_setting.ignore_pricing_rule){	
			if(in_list(this.sales_document, this.frm.doctype)){
				flag = true;
			}
		}
		return flag;
	},
	is_sales_return: function(){	
		
		if(in_list(this.return_ref, this.doctype)){
			if(this.is_return){
				return true;
			}
		}
		return false;
	},
	sales_document: ["Sales Invoice", "Quotation", "Sales Order", "Delivery Note"],
	return_ref: ["Sales Invoice", "Delivery Note", "Purchase Receipt", "Purchase Invoice"],	
	_set_values_for_item_list: function(children){

		if(this.is_sales()){
			console.log("Price List Rule has been ignored");
			return false;
		}
		var me = this;
		
		var price_list_rate_changed = false;
		for(var i=0, l=children.length; i<l; i++) {
			var d = children[i];
			var existing_pricing_rule = frappe.model.get_value(d.doctype, d.name, "pricing_rule");
			for(var k in d) {
				var v = d[k];
				if (["doctype", "name"].indexOf(k)===-1) {
					if(k=="price_list_rate") {
						if(flt(v) != flt(d.price_list_rate)) price_list_rate_changed = true;
					}
					frappe.model.set_value(d.doctype, d.name, k, v);
				}
			}

			// if pricing rule set as blank from an existing value, apply price_list
			if(!me.frm.doc.ignore_pricing_rule && existing_pricing_rule && !d.pricing_rule) {
				me.apply_price_list(frappe.get_doc(d.doctype, d.name));
			}
		}

		if(!price_list_rate_changed) me.calculate_taxes_and_totals();
	},
	
	tablix_price_list_rate: function(doc, cdn, cdt){

		// Do Nothing 	
	},
	currency: function() {

		if(this.is_sales() && this.frm.doc.currency !== this.get_company_currency()){
			this.calculate_currency_exchange();
			this.set_dynamic_labels();
			console.log("Currency Changed");
			return false;
		}
		/* manqala 19/09/2016: let the translation date be whichever of the transaction_date or posting_date is available */
		var transaction_date = this.frm.doc.transaction_date || this.frm.doc.posting_date;
		/* end manqala */

		var me = this;
		this.set_dynamic_labels();

		var company_currency = this.get_company_currency();
		// Added `ignore_pricing_rule` to determine if document is loading after mapping from another doc
		if(this.frm.doc.currency && this.frm.doc.currency !== company_currency
				&& !this.frm.doc.ignore_pricing_rule) {
			this.get_exchange_rate(transaction_date, this.frm.doc.currency, company_currency,
				function(exchange_rate) {
					me.frm.set_value("conversion_rate", exchange_rate);
				});
		} else {
			this.conversion_rate();
		}
	},
	conversion_rate: function() {
		const me = this.frm;
		if(this.is_sales() && this.frm.doc.currency !== this.get_company_currency()){
			this.calculate_currency_exchange();
			this.calculate_margin_and_total();
			console.log("Quotation");
			return false;
		}

		if(this.frm.doc.currency === this.get_company_currency()) {
			this.frm.set_value("conversion_rate", 1.0);
		}
		if(this.frm.doc.currency === this.frm.doc.price_list_currency &&
			this.frm.doc.plc_conversion_rate !== this.frm.doc.conversion_rate) {
			this.frm.set_value("plc_conversion_rate", this.frm.doc.conversion_rate);
		}

		if(flt(this.frm.doc.conversion_rate)>0.0) {
			if(this.frm.doc.ignore_pricing_rule) {
				this.calculate_taxes_and_totals();
			} else if (!this.in_apply_price_list){
				this.set_actual_charges_based_on_currency();
				this.apply_price_list();
			}

		}
		// Make read only if Accounts Settings doesn't allow stale rates
		this.frm.set_df_property("conversion_rate", "read_only", erpnext.stale_rate_allowed() ? 0 : 1);
	},
	calculate_currency_exchange: function(){

		var me = this;
		if(this.frm.doc.items && flt(this.frm.doc.conversion_rate) > 0.0){	
			conversion_rate = this.frm.doc.conversion_rate;
			for(var i=0;i<this.frm.doc.items.length;i++){
				_item = this.frm.doc.items[i];
				_item.price_list_rate = flt(_item.base_price_list_rate)/conversion_rate;
				_item.rate = flt(_item.base_rate)/conversion_rate;
				_item.amount = flt(_item.base_rate)/conversion_rate;
			}
		}
		this.taxes_and_charges();
		this.calculate_taxes_and_totals();
		this.calculate_taxes_and_duties();
	},

	tax_amount: function(doc, cdt, cdn){
		this.calculate_taxes_and_duties();	
	},
	calculate_taxes_and_duties: function(){

		var taxes_items = this.frm.doc.taxes || [];
		for(var i=0;i<taxes_items.length; i++){
			
			var tax_item = taxes_items[i];
			if(in_list(frappe.boot.tablix.tablix_setting.duties_accounts, tax_item.account_head)){
				console.log("Other Charges");
				if(this.frm.fields_dict.other_charges){
					this.frm.set_value("other_charges", tax_item.tax_amount);
				}
				else if(this.frm.fields_dict.duties){
					this.frm.set_value("duties", tax_item.tax_amount);	
				}	
			}
			else if(in_list(frappe.boot.tablix.tablix_setting.taxes_accounts, tax_item.account_head)){
				console.log("Vat Charges");
				if(this.frm.fields_dict.vat){
					this.frm.set_value("vat", tax_item.tax_amount);
				
				}
			}

		}
	},
	make_services_contracts: function(){

		var me = this;
		if(me.frm.doc.doctype=="Sales Order" && me.frm.doc.docstatus==1){
			this.frm.add_custom_button(__("Service Order"), function(){ 
				frappe.model.open_mapped_doc({
					method:"tablix.tablix_project.service_order.make_service_order",
					frm: me.frm
				})	
			}, __("Make"))
		}	
		
	},
});
