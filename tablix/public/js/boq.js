/*
	Developer
	Email sahil.saini@tablix.ae
*/

frappe.provide("tablix.boq");

tablix.boq.BoqController = Class.extend({
	
	init: function(frm){
		this.frm = frm;
		this.setup();
	},
	
	setup: function(){
		this.setup_add_fetch();
		this.editable();
		this.setup_filters();
		this.make();
	},
	setup_add_fetch: function(){
		this.frm.add_fetch("item_code", "description", "description");
                this.frm.add_fetch("item_code", "item_name", "item_name");
                this.frm.add_fetch("item_code", "stock_uom", "uom");
                this.frm.add_fetch("item_code", "brand", "brand");
                this.frm.add_fetch("opportunity", "enquiry_from", "quotation_to");
                this.frm.add_fetch("opportunity", "customer", "customer")
                this.frm.add_fetch("opportunity", "lead", "lead")	
	},
	editable: function(){
		if(this.frm.doc.status == "Designing" || this.frm.doc.status == "Costing"){
			this.frm.get_field('items').grid.editable_fields = [
				{fieldname: 'item_code', columns: 2},
				{fieldname: 'brand', columns: 1},
				{fieldname: 'item_group', columns: 2},
				{fieldname: 'stock_uom', columns: 1},
				{fieldname: 'qty', columns: 1},
				{fieldname: 'current_cost', columns: 1},
				{fieldname: 'cost_amount', columns: 1},
				{fieldname: 'check', columns: 1},
			];
		}
		else{   
			this.frm.get_field('items').grid.editable_fields = [
				{fieldname: 'item_code', columns: 2},
				{fieldname: 'stock_uom', columns: 1},
				{fieldname: 'qty', columns: 1},
				{fieldname: 'current_cost', columns: 1},
				{fieldname: 'selling_price', columns: 1},
				{fieldname: 'cost_amount', columns: 1},
				{fieldname: 'sale_amount', columns: 2},
				{fieldname: 'check', columns: 1},
			];
		}
	},
	setup_filters: function(){

	
	},
	make: function(){
	},
	calculate_rm_cost_sale_margin: function(doc){
		var rm = doc.items || [];
		for(var i=0;i<rm.length;i++) {
			var margin = flt(rm[i].margin_percent) / 100;
			margin = flt(1- margin);
			var amt = flt(rm[i].current_cost) / margin;
			var int_amt = parseInt(amt);
			console.log(int_amt);
			var flt_amt = amt.toFixed(2)
			var num_dec = (flt(amt) - int_amt).toFixed(2);
			num_dec = num_dec.toString();
			num_dec = num_dec.slice(2,4);
			if(num_dec != "00") {
				amt = int_amt + 1;
			}
			set_multiple('Boq Item',rm[i].name, {'selling_price': amt}, 'items');
			var sale_amt = amt * rm[i].qty;
			set_multiple('Boq Item',rm[i].name, {'sale_amount': sale_amt}, 'items');
			var margin_amt = flt(sale_amt) - flt(rm[i].cost_amount);
			set_multiple('Boq Item',rm[i].name, {'margin': margin_amt}, 'items');
		}
	},
	calculate_rm_sale: function() {
		var rm = this.frm.doc.items || [];
		var total_rm_sale = 0;
		for(var i=0;i<rm.length;i++) {
			var amt =   flt(rm[i].selling_price) * flt(rm[i].qty);
			set_multiple('Boq Item',rm[i].name, {'sale_amount': amt}, 'items');
			total_rm_sale += amt;

		}
	},
	calculate_rm_margin:  function() {
		var rm = this.frm.doc.items || [];

		for(var i=0;i<rm.length;i++) {
			var margin = flt(rm[i].sale_amount) - flt(rm[i].cost_amount);
			set_multiple('Boq Item',rm[i].name, {'margin': margin}, 'items');
			var margin_perc = flt(flt(margin) / flt(rm[i].sale_amount) * 100, 2);
			set_multiple('Boq Item',rm[i].name, {'margin_percent': margin_perc}, 'items');
		}

	},
	calculate_rm_cost: function() {
		var rm = this.frm.doc.items || [];
		var total_rm_cost = 0;
		for(var i=0;i<rm.length;i++) {
			amt =   flt(rm[i].current_cost) * flt(rm[i].qty);
			set_multiple('Boq Item',rm[i].name, {'cost_amount': amt}, 'items');
			total_rm_cost += amt;
		}
	},
	calculate_site_cost:  function(doc) {
		var site = "";
		var cost_amt =0;
		var sale_amt =0;
		var rm = doc.items || [];
		var total_rm_cost = 0;
		for(var i=0;i<rm.length;i++){
			if(rm[i].site){
				if(site != "" && cost_amt !=0){
					var row = frappe.model.add_child(frm.doc, "Boq Site Costing", "site_costing");
					row.site = rm[i].site
					row.total_cost = cost_amt
					row.total_sale = sale_amt
				}
				site = rm[i].site;
				cost_amt = 0;
				sale_amt = 0;
			}
			cost_amt +=     flt(rm[i].cost_amount);
			sale_amt += flt(rm[i].sale_amount);
		}
	},
	calculate_rate_amount_amc: function(doc) {
		var rm = doc.amc_spare_parts || [];
		var rate = 0.00;
		var qty = 0.00;
		var amt  = 0.00;
		for(var i=0;i<rm.length;i++) {
			rate = rm[i].amc_rate;
			qty = rm[i].qty;
			amt = rate * qty;
			console.log(amt);
			set_multiple('AMC Spare Parts',rm[i].name, {'amount': amt}, 'amc_spare_parts');
		}
	},
	calculate_amount_extended_warranty: function(doc) {
		var rm = doc.amc_extended_warranty || [];
		var rate = 0.00;
		var qty = 0.00;
		var amt  = 0.00;
		for(var i=0;i<rm.length;i++) {
			rate = rm[i].unit_price;
			qty = rm[i].quantity;
			amt = rate * qty;
			console.log(amt);
			set_multiple('Extended Warranty',rm[i].name, {'amount': amt}, 'amc_extended_warranty');
		}
	},
	add_quotation: function(){
		var me = this;
		if(me.frm.doc.status == "Sales Complete"){
			me.frm.add_custom_button(__('Quotation'), function(event){
				me.make_quotation();
			});
		}
	},
	make_quotation: function(){
		var me = this;
	},
	setup_design: function(){
		var me = this;
		if(me.frm.doc.status != "Designing"){
			var df1 = frappe.meta.get_docfield("Boq Item","item_code", me.frm.doc.name);
			df1.read_only = 1;

			var df1 = frappe.meta.get_docfield("AMC","item_code", me.frm.doc.name);
			df1.read_only = 1;

			var df1 = frappe.meta.get_docfield("AMC Preventive","description", me.frm.doc.name);
			df1.read_only = 1;

			var df1 = frappe.meta.get_docfield("AMC Reactive","description", me.frm.doc.name);
			df1.read_only = 1;
		}
	},

	add_boq: function(){
		if(frm.doc.status == "BOQ Approved"){
			frm.add_custom_button(__('Quotation'),function(event){
			frm.timeline.insert_comment("Workflow", "BOQ Converted to Quotation");
				frappe.model.open_mapped_doc({
					method: "tablix.boq.doctype.boq.boq.make_quotation",
					frm: frm
				});
			});
		}
	},
	
	setup_read_only: function(){
		if(frm.doc.status == "Sales Complete"){
			var boqi = ['item_code', 'stock_uom', 'qty', 'current_cost', 'cost_amount', 'sale amount'];
			var boq = ['applied_margin', 'discount', 'special_discount', 'project_discount', 'special_discount'];
			var amcp = ['description', 'uom', 'total'];
			var amcr = ['description', 'uom', 'total'];
			var amcsp = ['item_code', 'uom', 'amc_rate', 'amount'];
			var amcew = ['warranty', 'quantity', 'unit_price', 'amount'];

			if (!frappe.user.has_role("Sales Manager")){
				tablix.read_only(me, "Boq Item",boqi ,1);
				tablix.read_only(me, "Boq",boq,1);
				tablix.make_read(me, "AMC Preventive", amcp, 1);
				tablix.make_read(me, "AMC Preventive", amcr, 1);
				tablix.read_only(me, "AMC Reactive", amcsp, 1);
				tablix.read_only(me, "AMC Spare Parts", amcsp, 1);
				tablix.read_only(me, "Extended Warranty", amcew, 1);
			}
		}
	}	
});
