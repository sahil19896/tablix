/*
	
	Developer Sahil
	License MIT/Tablix/Frappe

*/

frappe.provide("tablix.taxes_and_charges");

tablix.taxes_and_charges.TaxesAndCharges = tablix.manual_assign.ManualAssign.extend({

	init: function(args){
	
		$.extend(this, args);
		this._flr = tablix.add_fraction_value;
	},
	calculate_total: function(){
		this.calculate_boq_total();
		this.calculate_amc_total();
		this.calculate_discount_total();
		this.calculate_grand_total();
	},
	calculate_boq_total: function(){
		var me = this;
		this.frm.doc.total_cost = 0.0;
		this.frm.doc.total_sale = 0.0;
		this.frm.doc.service_cost =  0.0;
		this.frm.doc.material_cost = 0.0;
		this.frm.doc.total_margin = 0.0;
		this.frm.doc.total_percent = 0.0;
		if(!this.frm.doc.boq){
			return false;
		}
		this.frm.clear_table("site_costing");
		this.frm.refresh_field("site_costing");
		this.calculate_boq_items_total();	
	},

	calculate_boq_items_total: function(){
		var me = this;
		
		var _margin  = this.frm.doc.boq_desired_margin;
		var items  = this.frm.doc.items || [];
		var _site = null;
		for(var i=0;i<items.length;i++){
			_frm = me.frm.fields_dict.items.grid.grid_rows_by_docname[items[i].name];
			if(_frm.doc.margin_type=="Percentage"){
				if(_frm.doc.current_cost){
					_frm.doc.selling_price = flt(_frm.doc.current_cost)/(flt(1.0)-flt(_margin/100));
				}
			}
			else if(_frm.doc.margin_type == "Amount"){
				if(!_frm.doc.selling_price){
					_frm.doc.selling_price = flt(_frm.doc.current_cost);
				}
				else{
					_frm.doc.margin_percent = _frm.doc.margin/_frm.doc.selling_price*100.0
				}
				
			}
			else{
				_frm.doc.selling_price = _frm.doc.current_cost;		
			}
		
			_frm.doc.cost_amount = this._flr(_frm.doc.current_cost * _frm.doc.qty || 1);
			_frm.doc.sale_amount = this._flr(_frm.doc.selling_price * _frm.doc.qty || 1);
			_frm.doc.margin = this._flr(_frm.doc.sale_amount-_frm.doc.cost_amount);
			_frm.doc.margin_percent = _frm.doc.margin/_frm.doc.sale_amount*100;

			if(in_list(['Services', 'Professional Services'], _frm.doc.item_group)){
				me.frm.doc.service_cost = flt(_frm.doc.cost_amount);	
			}
			this.calculate_sitewise_total(_frm);
			me.frm.doc.total_cost += _frm.doc.cost_amount;
			me.frm.doc.total_sale += _frm.doc.sale_amount;
			
			_frm.refresh();
		}
		
		me.frm.doc.material_cost = me.frm.doc.total_cost - me.frm.doc.service_cost;
		me.frm.doc.total_margin = me.frm.doc.total_sale - me.frm.doc.total_cost;
		me.frm.doc.margin_percent = me.frm.doc.total_margin/me.frm.doc.total_sale*100 
		me.frm.refresh();	
		
	},
	calculate_sitewise_total: function(_frm){
			
		var items = this.frm.doc.site_costing || [];
		if(items.length===0) return this._add_site_costing(_frm, null);
			
		sites = items.filter(function(val){ 
			if(val.site == _frm.doc.site_name) return val;	
		});
		if(sites.length === 0) return this._add_site_costing(_frm, null);

		site = this.frm.fields_dict.site_costing.grid.grid_rows_by_docname[sites[0].name];
		this._add_site_costing(_frm, site)
			
	},
	_add_site_costing: function(_frm, site){

		
		if(!site ){
			this.frm.add_child("site_costing", {
				site: _frm.doc.site_name,
				total_sale: _frm.doc.sale_amount,
				total_cost: _frm.doc.cost_amount,
			});
		}
		else{
			site.doc.total_sale += _frm.doc.sale_amount;
			site.doc.total_cost += _frm.doc.cost_amount;
		}
		this.frm.refresh_field("site_costing");
	},
	calculate_amc_total: function(){
		this.frm.doc.amc_total_cost = 0.0;
		this.frm.doc.amc_total_sale_ =  0.0;
		this.frm.doc.amc_margin = 0.0;
		this.frm.doc.amc_margin_percent = 0.0;
		this.frm.doc.cost_for_ppm = 0.0;
		this.frm.doc.one_year_maintenance =  this.frm.doc.one_year_maintenance?this.frm.doc.one_year_maintenance:1.0;
		this.frm.doc.total_cost_preventive_maintenance = 0.0;
		this.frm.doc.cost_for_rm = 0.0;
		this.frm.doc.no_of_call = this.frm.doc.no_of_calls?this.frm.doc.no_of_calls:1.0;
		this.frm.doc.total_cost_for_reactive_maintenance = 0.0;
		this.frm.doc.total_cost_for_spare_parts = 0.0;
		this.frm.doc.extended_warranty_cost = 0.0;
		this.frm.doc.total_charges_of_maintenance = 0.0;
			
		if(!this.frm.doc.is_amc) return false;	
		
		this.calculate_service_total();
		this.calculate_preventive_total();
		this.calculate_reactive_total();
		this.calculate_extended_warranty_total();
		this.calculate_spare_parts_total();
		this.calculate_one_time_total();
		this.calculate_amc_yearly_total();

	},
	calculate_service_total: function(){

		if(this.frm.doc.amc_service_items) return false;
	

		var items = this.frm.doc.amc_service_items || [];
		for(var i=0;i<items.length; i++){
			this.frm.doc.cost_for_ppm += items[i].qty || 1;	
		}
		
	},
	
	calculate_preventive_total: function(){
		
		if(!this.frm.doc.amc_preventive) return false;
	
		var items = this.frm.doc.amc_preventive ||[];
		var day_uom = items.filter(function(val){if(val.uom && val.uom =="Days") return val});
		if(day_uom.length === 0){
			frappe.msgprint(__("Please enter <b>Days UOM</b> in Preventive Items"));
			return false;
		}
		day_uom = day_uom[0];
		for(var i=0;i<items.length;i++){
			item = items[i];
			if(item.uom != day_uom.uom){
				if(item.uom == "rate/day") this.frm.doc.cost_for_ppm += flt(item.total)*flt(day_uom.total);	
				else this.frm.doc.cost_for_ppm += flt(item.total);	
			}
		}
	
	},
	calculate_reactive_total: function(){
	
		if(!this.frm.doc.amc_reactive) return false;	
		
		var items  = this.frm.doc.amc_reactive || [];
		for(var i=0;i<items.length;i++){
			this.frm.doc.cost_for_rm += flt(items[i].total);	
		}
	},
	calculate_extended_warranty_total: function(){

		if(!this.frm.doc.amc_extended_warranty) return false;
		var items = this.frm.doc.amc_extended_warranty || [];
		for(var i=0;i<items.length; i++){
			_item = items[i];
			if(_item.quantity){
				_item.amount = flt(_item.unit_price) * flt(_item.quantity);
			}
			
			this.frm.doc.extended_warranty_cost += flt(_item.amount);

		}	
	},

	calculate_spare_parts_total: function(){
		if(!this.frm.doc.amc_spare_parts) return false;
		
		var items = this.frm.doc.amc_spare_parts || [];
		for(var i=0; i<items.length; i++){
			_item = items[i];
			if(_item.qty){
				_item.amount = flt(_item.amc_rate) * flt(_item.qty);
			}
			
			this.frm.doc.total_cost_for_spare_parts += flt(_item.amount);
		}
	},

	calculate_one_time_total: function(){
		
		var _default = 1.0;
		this.frm.doc.total_cost_preventive_maintenance = this._flr(this.frm.doc.cost_for_ppm*this.frm.doc.one_year_maintenance);
		this.frm.doc.total_cost_reactive_maintenance = this._flr(this.frm.doc.cost_for_rm*this.frm.doc.no_of_calls);
		this.frm.doc.total_charges_of_maintenance += this._flr(this.frm.doc.total_cost_preventive_maintenance);
		this.frm.doc.total_charges_of_maintenance += this._flr(this.frm.doc.total_cost_reactive_maintenance);
		this.frm.doc.total_charges_of_maintenance += this._flr(this.frm.doc.total_cost_for_spare_parts);
		this.frm.doc.total_charges_of_maintenance += this._flr(this.frm.doc.extended_warranty_cost);

	},
	calculate_amc_yearly_total: function(){

		if(!this.frm.doc.maintenance_required_for){
			frappe.msgprint("Please select <b>Maintenance Required For</b>");
			return false;
		}
		if(this.frm.doc.amc_yearly.length === 0){
			this.add_default_yearly_item();
			return false;
		}
		
		var items = this.frm.doc.amc_yearly || [];
		for(var i=0;i<items.length;i++){
			_frm = this.frm.fields_dict.amc_yearly.grid.grid_rows_by_docname[items[i].name];
			_frm.doc.reactive_cost =  this.frm.doc.total_cost_reactive_maintenance;
			_frm.doc.preventive_cost = this.frm.doc.total_cost_preventive_maintenance;
			_frm.doc.spare_parts_cost = this.frm.doc.total_cost_for_spare_parts;
			_frm.doc.extended_warranty_cost = this.frm.doc.extended_warranty_cost;
			_frm.doc.amc_yearly_total = this.frm.doc.total_charges_of_maintenance;
				
			if(flt(_frm.doc.percentage)> 0.0 && _frm.doc.select_year =="First Year"){
				_frm.doc.percentage = 0.0;
				
			}
			this.update_yearly_percentage_and_margin(_frm);	
		
		}
		
	},
	add_default_yearly_item: function(){
		var doc = this.frm.doc;
		doc = this.frm.add_child("amc_yearly", {
			percentage: 0.0, select_year: "First Year",
			reactive_cost: doc.total_cost_reactive_maintenance,
			preventive_cost: doc.total_cost_preventive_maintenance,
			spare_part_cost: doc.total_cost_for_spare_parts,
			extended_warranty_cost: doc.extended_warranty_cost,
			amc_yearly_total: doc.total_charges_of_maintenance,
			am_reactive_cost: doc.total_cost_reactive_maintenance,
			am_preventive_cost: doc.total_cost_preventive_maintenance,
			am_spare_part_cost: doc.total_cost_for_spare_parts,
			am_extended_warranty_cost: doc.extended_warranty_cost,
			am_amc_yearly_total: doc.total_charges_of_maintenance
			
				
		});
		if(this.frm.doc.amc_desired_margin){
			doc.adm_amc_yearly_total = this._flr(flt(doc.am_amc_yearly_total)/flt(1.0-(this.frm.doc.amc_desired_margin/100)))
		}
		else{
			doc.adm_amc_yearly_total = this._flr( doc.am_amc_yearly_total);
		}	
		
	},
	update_yearly_percentage_and_margin: function(_frm){

		var _margin = this.frm.doc.amc_desired_margin;
		var _percentage = _frm.doc.percentage;
		if(!_percentage){
			_frm.doc.am_reactive_cost = _frm.doc.reactive_cost;
			_frm.doc.am_preventive_cost = _frm.doc.preventive_cost;
			_frm.doc.am_spare_parts_cost = _frm.doc.spare_parts_cost;
			_frm.doc.am_extended_warranty_cost = _frm.doc.extended_warranty_cost;
			_frm.doc.am_amc_yearly_total = _frm.doc.amc_yearly_total;	 		
		}	
		else{
			_frm.doc.am_reactive_cost = flt(_frm.doc.reactive_cost)/(1.0-(_percentage/100));
			_frm.doc.am_preventive_cost = flt(_frm.doc.preventive_cost)/(1.0-(_percentage/100));
			_frm.doc.am_spare_part_cost = flt(_frm.doc.spare_parts_cost)/(1.0-(_percentage/100));
			_frm.doc.am_extended_warranty_cost = flt(_frm.doc.extended_warranty_cost)/(1.0-(_percentage/100));
			_frm.doc.am_amc_yearly_total = flt(_frm.doc.amc_yearly_total)/(1.0-(_percentage/100));	 		
		}
		if(_margin){
			_frm.doc.adm_amc_yearly_total = this._flr(flt(_frm.doc.am_amc_yearly_total)/(1.0-(_margin/100)));
		}
		else{
			_frm.doc.adm_amc_yearly_total = this._flr(flt(_frm.doc.am_amc_yearly_total));
		}

		this.frm.doc.amc_total_cost += flt(_frm.doc.am_amc_yearly_total);
		this.frm.doc.amc_total_sale_ += flt(_frm.doc.adm_amc_yearly_total);
			
	},
	calculate_discount_total: function(){
		this.frm.doc.boq_total_discount = 0.0;
		this.frm.doc.amc_total_discount = 0.0;
		this.frm.doc.net_discount = 0.0;
	
		if(!this.frm.doc.boq_discount_item) return false;

		var items = this.frm.doc.boq_discount_item||[];
		
		for(var i=0;i<items.length; i++){
			_item = items[i];
			_item.boq_total_discount = flt(_item.boq_discount) + flt(_item.boq_special_discount);
			_item.boq_total_discount += flt(_item.boq_project_discount) + flt(_item.boq_special_project_discount);
			if(_item.discount_type == "BOQ" && this.frm.doc.boq===1) 
				this.frm.doc.boq_total_discount += _item.boq_total_discount;
			else if(_item.discount_type =="AMC" && this.frm.doc.is_amc===1)
				this.frm.doc.amc_total_discount += _item.boq_total_discount;
		}
		
		this.frm.doc.net_discount = this.frm.doc.amc_total_discount + this.frm.doc.boq_total_discount;	
	},
	calculate_grand_total: function(){
		// Including Discount margin, AMC, and BOQ total
		if(this.frm.doc.boq){
			if(this.frm.doc.boq_total_discount) 
				this.frm.doc.total_cost += this.frm.doc.boq_total_discount;
			this.frm.doc.total_margin = this.frm.doc.total_sale - this.frm.doc.total_cost;
			this.frm.doc.margin_percent = this.frm.doc.total_margin/this.frm.doc.total_sale*100;
		}
		if(this.frm.doc.is_amc){
			if(this.frm.doc.amc_total_discount) 
				this.frm.doc.amc_total_cost += this.frm.doc.amc_total_discount;	
			this.frm.doc.amc_margin = this.frm.doc.amc_total_sale_ - this.frm.doc.amc_total_cost;
			this.frm.doc.amc_margin_percent = this.frm.doc.amc_margin/this.frm.doc.amc_total_sale_*100;	
		}	

		this.frm.doc.total_cost_amt = this.frm.doc.total_cost+this.frm.doc.amc_total_cost;
		this.frm.doc.total_amt = this.frm.doc.total_sale+this.frm.doc.amc_total_sale_
		
		this.frm.doc.grand_margin_total  = this.frm.doc.total_amt - this.frm.doc.total_cost_amt;		
		this.frm.doc.grand_margin_percent = this.frm.doc.grand_margin_total/this.frm.doc.total_amt*100;
		this.frm.refresh();
	},
	items_remove: function(){
		this.calculate_total();
	},
	current_cost: function(doc, cdt, cdn) {
		// BOQ Item table field
		item = this.frm.fields_dict.items.grid.grid_rows_by_docname[cdn];
		if(flt(item.doc.current_cost) <= 0.0){
			item.doc.current_cost = 0;
			item.doc.selling_price = 0;
			item.doc.margin = 0;
			item.doc.margin_percent = 0;
			item.doc.cost_amount = 0;
			item.doc.sale_amount = 0;	
		}
		item.refresh();
		this.calculate_total();
	},
	selling_price: function(doc, cdt, cdn) {
		// BOQ Item table field
		this.calculate_total();
	},
	margin: function(doc, cdt, cdn){
		// BOQ Item Table Field
		this.calculate_total();
	},	
	margin_type: function(doc, cdt, cdn){
		// BOQ Item Table Field
		_frm = this.frm.fields_dict.items.grid.grid_rows_by_docname[cdn];
		if(_frm.doc.margin_type =="Percentage"){
			if(!this.frm.doc.boq_desired_margin){
				return ;
			}
			this.calculate_total();
		}
		else{
			this.calculate_total();	
		}			
		
			
	},
	boq_desired_margin: function(){	
		// BOQ Margin Field Master Form	
		this.calculate_total();
	},
	total: function(){
		// AMC Preventive and Reactive Item Total Field
		this.calculate_total();
	},
	
	qty: function(){
		// BOQ Item and AMC Spare Partsi and Service Item Field
		this.calculate_total();
	},
	amc_rate: function(){
		//  AMC Spare Parts Item Field
		this.calculate_total();
	},
	select_year: function(){
		// AMC Yearly Item and AMC Extended Warranty
		this.calculate_total();
	},
	unit_price: function(){
		// AMC Extended Warranty Item Table Field
		this.calculate_total();
	},
	quantity: function(){
		// AMC Extended Warranty Item Table Field
		this.calculate_total();
	},
	amc_desired_margin: function(){	
		// AMC desired Margin
		this.calculate_total();
	},
	one_year_maintenance: function(){
		// AMC PPM Required in Per Year
		this.calculate_total();
	},
	percentage: function(){
		// AMC Yearly Percentage
		this.calculate_total();
	},
	no_of_calls:function(){
		// AMC No Of calls Per Year
		this.calculate_total();
	},
	discount_type: function(){
		// Discount Item Table
		this.calculate_total();
	},
	boq_discount: function(){
		// Discount Item Table
		this.calculate_total();
	},
	boq_special_discount: function(){
		// Discount Item Table
		this.calculate_total();
	},
	boq_project_discount: function(){
		// Disocunt Item Table
		this.calculate_total();
	},
	boq_special_project_discount: function(){
		// Discout Item Table
		this.calculate_total();
	},
	maintenance_required_for: function(){
		// Discount Item Table
		this.calculate_total();
	},
	calculate_proposed_time: function(doc){
		
		var proposed_time = flt(this.frm.doc.proposed_project_completion_time);
		var delivery_period  = flt(this.frm.doc.material_delivery_period);
		this.frm.doc.proposed_project_completion_time_ = proposed_time + delivery_period;
		this.frm.refresh();
	},
	proposed_project_completion_time: function(doc){
		this.calculate_proposed_time();
	},
	material_delivery_period: function(doc){
		this.calculate_proposed_time();
	},
});

/*
tablix.boq.qty = function(doc, cdt, cdn){
	var me = cur_frm;
	_frm = cur_frm.fields_dict.items.grid.grid_rows_by_docname[cdn];       
                if(!_frm.doc.qty){
                        frappe.msgprint(__("Please enter Quantity"));
                        return false;
                }       
                if(_frm.doc.qty <= _frm.doc.max_qty){

                        if(!_frm.doc.current_cost || !_frm.doc.selling_price){
				msg = format("You need to setup <b>Current/Selling Cost</b> For Item {0}", [_frm.doc.item_code]);
                                frappe.msgprint(__(msg));
                                return false;
                                
                        }
                        s_rate = flt(_frm.doc.selling_price);
                        b_rate = flt(_frm.doc.current_cost); 
                        _frm.doc.cost_amount = b_rate * flt(_frm.doc.qty);
                        _frm.doc.sale_amount = s_rate * flt(_frm.doc.qty);
                        _frm.doc.margin  = _frm.doc.sale_amount - _frm.doc.cost_amount;
                        _frm.doc.margin_percent = (_frm.doc.margin/_frm.doc.sale_amount)*100;
                        
                        }
                else{
                        erpnext.boq.update_price_list(me, _frm);     
                }       
                _frm.refresh();
                        

}

tablix.boq.update_price_list = function(frm, _frm){

	if(!frm.doc.quotation_to){
		frappe.msgprint("Please To [Lead/Customer]");
		return false;
	}
	if(frm.doc.customer && frm.doc.customer_code == "MAF"){
		
		frappe.call({
			method: "boq.whitelisted.get_price_list",
			args: {doc: frm.doc, item: _frm.doc},
			callback: function(res){
				if(res && res.message){
					prices = res.message.length >= 1? res.message[0] : null;
					if(!prices){
						frappe.msgprint(_("No Active Price List found for this particular item"));
						return
					}
					_frm.doc.current_cost = prices.buying_price;
					_frm.doc.selling_price = prices.selling_price;
					_frm.doc.margin = prices.margin_amount;
					_frm.doc.margin_percent = prices.margin_percent;
					_frm.doc.cost_amount = prices.cost_price;
					_frm.doc.sale_amount = prices.sales_price;
					_frm.doc.max_qty = prices.maximum_quantity;
				
				}
				_frm.refresh();
			}
		});
	 
	}

}
*/
