
frappe.provide("tablix.accounts");

tablix.accounts.AmountInWords = Class.extend({
	
	init: function(args){
		$.extend(this, args);
	},
	update_totals: function(doc){
		var td=0.0; var tc =0.0;
		var amt_in_words= "";
		var amt_2_words = "";
		var accounts = doc.accounts || [];
		for(var i in accounts) {
			td += flt(accounts[i].debit, precision("debit", accounts[i]));
			tc += flt(accounts[i].credit, precision("credit", accounts[i]));
		}
		var doc = locals[doc.doctype][doc.name];
		doc.total_debit = td;
		doc.total_credit = tc;
		doc.difference = flt((td - tc), precision("difference"));
		refresh_many(['total_debit','total_credit','difference']);
		var amt = td;
		var currency = "AED"
		this.get_amount_in_words(doc, amt, currency);
	},
	get_amount_in_words: function(doc, amt, currency){
		var me = this;
		doc.amount_in_words = ""
		if(!(amt && currency)){
			frappe.msgprint(__("Please Enter <b>Debit</b> & <b>Currency</b>"));
			return false;
		}
		frappe.call({
			
			method: "boq.whitelisted.amount_to_words",
			args: {amt:amt, currency: currency},
			callback: function(res){
				doc.amount_in_words = res.message;
				me.frm.refresh();
			}
		});
		me.frm.refresh();
	}
});
