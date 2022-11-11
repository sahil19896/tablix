// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.ui.form.on('Escalation Logs', {
	refresh: function(frm) {

		
		frm.add_custom_button(__(frm.doc.document_name), function(event){

			frappe.set_route("Form", frm.doc.document_type, frm.doc.document_name);

		}).addClass("btn-primary");

	}
});
