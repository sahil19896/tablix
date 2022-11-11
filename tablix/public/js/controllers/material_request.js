cur_frm.add_fetch("project", "project_name", "project_name");
cur_frm.set_query('tc_name', function () {
	return {
		"filters": {
			'type': 'Purchase'
		}
	}
});
frappe.provide("tablix.material_request");
var Controller = erpnext.buying.MaterialRequestController.extend({
	init: function(args){
		$.extend(this, args);
		$.extend(this, new tablix.manual_assign.ManualAssign());	
	},
	validate: function() {

		var total = 0;
		return false;
		$.each(frm.doc.items, function(i, d) {

			d.estimated_line_amount = flt(d.estimated_unit_price) * flt(d.qty);
			total += flt(d.estimated_line_amount);
		});

			frm.doc.estimated_total = total;
			frm.doc.request_by = frm.doc.owner;
	},
	refresh: function(frm){
		this._super(frm);
		this.make_dialog();
		this.make_purchase_order();	
	},
	setup_substitute_item: function(){
	},
	setup: function(){
		this._super();
                var args = {
                        frm: this.frm,
                        grid: this.frm.fields_dict.items,
                }
                this.duplicate_row = new tablix.duplicate.DuplicateRow(args);
	},
	
	make_purchase_order: function(){
		var me = this;
		me.frm.remove_custom_button(["Purchase Order"], 'Make');
		if(flt(me.frm.doc.per_ordered, 2) < 100) {
			if(me.frm.doc.docstatus==1){
				me.frm.add_custom_button(__("Make Purchase Order"), function(event){
					frappe.model.open_mapped_doc({
						method: "erpnext.stock.doctype.material_request.material_request.make_purchase_order",
						frm: cur_frm,
						run_link_triggers: true
					});
				});
			}
		}
	},

	before_save: function(){
		var me = this;
		if(me.frm.doc.company == "Tablix Technologies Pvt. Ltd."){
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "naming_series", "MREQ-IND-2020-");
		}
	},

	company: function(){
		var me = this;
		if(me.frm.doc.company == "Tablix Technologies Pvt. Ltd."){
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "internal_approver", "binu.c@tablix.ae");
		} else{
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "internal_approver", "bhavish@tablix.ae");
		}
	},

	is_internal: function(){
		var me = this;
		if(me.frm.doc.company == "Tablix Technologies Pvt. Ltd."){
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "internal_approver", "binu.c@tablix.ae");
		} else{
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "internal_approver", "bhavish@tablix.ae");
		}
	}
});

cur_frm.cscript['Purchase Order'] = function(){
	frappe.msgprint(__("Please use <b>Make Purchase Order</b> button to create Purchase Order. "));
	return false;
}
cur_frm.script_manager.make(Controller);
