// Copyright (c) 2019, Tablix and contributors
// For license information, please see license.txt

frappe.ui.form.on('Memos', {
	refresh: function(frm) {
		waiting_approval(cur_frm);
		send_document(frm);
	}
});

function send_document(frm){
	if(cur_frm.doc.tablix_status == "Approved"){
		var table = cur_frm.doc.memo_employee || "";
		if(table){
			for(var i=0; i<table.length; i++){
				if(frappe.session.user_email == table[i].email){
					cur_frm.toggle_display("memo_approvers");
					cur_frm.toggle_display("memo_description");
					cur_frm.toggle_display("memo_employee");
					cur_frm.add_custom_button(__("Read Memo"), function() {
						frappe.set_route("memo", {
							"name": cur_frm.doc.name
						});
					});
				}
			}
		}
		if(cur_frm.doc.all_employee == 0){
			cur_frm.toggle_display("all_employee");
		}
	}
}

frappe.ui.form.on('Memos', {
	before_save: function(frm) {
		if(frappe.session.user_email == cur_frm.doc.memo_request_by){
			var table = cur_frm.doc.memo_approvers;
			for(var i=0; i<table.length; i++){
				if(table[i].decline > 0){
					frappe.model.set_value(table[i].doctype, table[i].name, "decline", 0);
				}
			}
		}
		if(cur_frm.doc.tablix_status == "Waiting For Approval"){
			cur_frm.assign_to.remove(cur_frm.doc.memo_request_by);
		}
	}
});

frappe.ui.form.on('Memos', {
	onload_post_render: function(frm){
		var approver = ["EMP/0031", "EMP/0035", "EMP/0027", "EMP/0088", "EMP/0140"];
		var approver_email = ["gopu@tablix.ae", "kartik@tablix.ae", "bala@tablix.ae", "satyajith.ashokan@tablix.ae", "rajesh.k@tablix.ae"];
		if(! cur_frm.doc.memo_request_by){
			cur_frm.set_value("memo_request_by", frappe.session.user_email);
		}

		if(! cur_frm.doc.memo_approvers){
			for(var i=0;i<approver.length;i++){
				var child = frappe.model.get_new_doc("Policy Approvers",cur_frm.doc,"memo_approvers");
				$.extend(child, {
					"employee": approver[i],
					"email": approver_email[i]
				});
			}
			cur_frm.refresh_field("memo_approvers");
		}
	}
});

function check_approval(cur_frm){
	if(cur_frm.doc.tablix_status == "Waiting For Approval"){
		var table = cur_frm.doc.memo_approvers;
		var accept = 0;
		var decline = 0;
		for(var i=0;i<table.length;i++){
			if(table[i].accept > 0){
				accept += 1;
			}else if(table[i].decline > 0){
				decline += 1;
			}
		}
		if(accept+decline == table.length){
			if(decline > 0){
				frappe.model.set_value("Memos", cur_frm.doc.name, "tablix_status", "Open");
			} else if(accept == table.length){
				frappe.model.set_value("Memos", cur_frm.doc.name, "tablix_status", "Completed");
			}
		}
	}
}

function waiting_approval(cur_frm){
	var state = cur_frm.doc.tablix_status;
	if(state == "Waiting For Approval"){
		cur_frm.assign_to.remove(cur_frm.doc.memo_request_by);
		var table = cur_frm.doc.memo_approvers;
		for(var i=0;i<table.length;i++){
			if(table[i].email == frappe.session.user_email && table[i].accept == 0){
				cur_frm.add_custom_button(__("Approve"), function() {
					get_choice(1, cur_frm, frappe.session.user_email, "accept", "decline", 0);
				});

				cur_frm.add_custom_button(__("Decline"), function() {
					get_reason(cur_frm);
				});
			}
		}
	}
}

function get_reason(cur_frm){
	var d = new frappe.ui.Dialog({
		title: __('Reason For Declined'),
		fields: [
			{fieldtype:'Small Text', fieldname:'reason', reqd:1, label:'Reason'},
		],
	});
	
	d.set_primary_action(__('Save'), function() {
		var data = d.get_values();
		var msg = data.reason+"\n \n";
		var table = cur_frm.doc.memo_approvers;
		for(var i=0; i<table.length; i++){
			if(table[i].email == frappe.session.user_email){
				var old_reason = table[i].reason || "";
				frappe.model.set_value(table[i].doctype, table[i].name, "reason", old_reason+msg);
			}
		}
		get_choice(0, cur_frm, frappe.session.user_email, "accept", "decline", 1);
		d.hide();
	});

	d.show();
}

function get_choice(value_1, cur_frm, email, button_1, button_2, value_2){
	var table = cur_frm.doc.memo_approvers;
	for(var i=0; i<table.length; i++){
		if(table[i].email == email){
			frappe.model.set_value(table[i].doctype, table[i].name, button_1, value_1);
			frappe.model.set_value(table[i].doctype, table[i].name, button_2, value_2);
		}
	}
	cur_frm.refresh_field("memo_approvers");
	cur_frm.assign_to.remove(frappe.session.user_email);
	check_approval(cur_frm);
	cur_frm.save();
}

frappe.ui.form.on("Memos", "all_employee", function(frm){
	if(cur_frm.doc.all_employee == 1){
		cur_frm.clear_table("memo_employee");
		cur_frm.clear_table("department");
		cur_frm.refresh_field("department");		

		frappe.call({
			method: "tablix.tablix_hr.doctype.policy_document_management.policy_document_management.get_employee_data",
			args: {"department": "ALL"},
			callback: function(r){
				if(r && r.message){
					var emps = r.message;
					for(var i=0;i<emps.length;i++){
						var child = frappe.model.get_new_doc("Policy Employee",cur_frm.doc,"memo_employee");
						$.extend(child, {
							"employee": emps[i].name,
							"employee_name": emps[i].employee_name,
							"email": emps[i].user_id,
						});
					}
					cur_frm.refresh_field("memo_employee");
				}
			}
		});
	} else{
		cur_frm.clear_table("memo_employee");
		cur_frm.refresh_field("memo_employee");
	}
});

cur_frm.cscript.department = function(doc, cdt, cdn) {
	var department = frappe.get_doc(cdt, cdn);
	if(department.department){
		frappe.call({
			method: "tablix.tablix_hr.doctype.policy_document_management.policy_document_management.get_employee_data",
			args: {"department": department.department},	
			callback: function(r){
				if(r && r.message){
					var emps = r.message;
					for(var i=0;i<emps.length;i++){
						var child = frappe.model.get_new_doc("Policy Employee",cur_frm.doc,"memo_employee");
						$.extend(child, {
							"employee": emps[i].name,
							"employee_name": emps[i].employee_name,
							"email": emps[i].user_id,
						});
					}
					cur_frm.refresh_field("memo_employee");
				}
			}
		});
	}
}

