cur_frm.get_docfield("accounts").allow_bulk_edit = 1;

frappe.provide("tablix.accounts");

frappe.ui.form.on("Journal Entry Account",{
	
	credit_in_account_currency: function(frm){
		update_amount(frm);
	},
	debit_in_account_currency: function(frm){
		update_amount(frm);
	}
});


function update_amount(frm){

	var td=0.0; var tc =0.0;
	var amt_in_words= "";
	var amt_2_words = "";
	var accounts = frm.doc.accounts || [];
	for(var i in accounts) {
		td += flt(accounts[i].debit, precision("debit", accounts[i]));
		tc += flt(accounts[i].credit, precision("credit", accounts[i]));
	}
	var currency = "AED"
	amt = tc?tc:td
	if(!(amt && currency)){
		frappe.msgprint(__("Please Enter <b>Currency</b>"));
		return false;
	}

	frappe.call({
		
		method: "tablix.whitelisted.amount_to_words",
		args: {amt:amt, currency: currency},
		callback: function(res){
			frm.doc.amt_words = res.message;
			frm.refresh();
		}
	});

}
