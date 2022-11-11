
frappe.provide("tablix.whitelisted");

$.extend(tablix.whitelisted, {
	
	send_for_approval: function(frm, method, agrs, doctype, send_to){
		var me = this;
		frappe.call({
			method: method,
			args: {"doc":frm.doc, "info":args},
			callback: function(res) {
				if(res.exc) {
					msgprint(__("There were errors."));
				} else {
					var msg = format("Succesfully sent to {0} for approval", [send_to])
					msgprint(__(msg));
					me.insert_comment(doctype, send_to);
					frm.refresh();
				}
			}
		});
	},

	insert_comment: function(doctype, send_to){
		var msg = format("Approval succesfully sent to {0}, Ref Date: {1}", [send_to, frappe.datetime.now_datetime()]);
		frm.timeline.insert_comment(doctype, msg);
		
	}

});

