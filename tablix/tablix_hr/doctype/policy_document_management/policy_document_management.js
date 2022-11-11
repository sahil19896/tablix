// Copyright (c) 2019, Tablix and contributors
// For license information, please see license.txt

frappe.ui.form.on('Policy Document Management', {
	refresh: function(frm) {
		waiting_approval(cur_frm);
		send_document(frm);
	}
});

function send_document(frm){
	if(cur_frm.doc.tablix_status == "Approved"){
		var table = cur_frm.doc.policy_employee || "";
		if(table){
			for(var i=0; i<table.length; i++){
				if(frappe.session.user_email == table[i].email){
					if(frappe.session.user_email != 'prathyoosh.b@tablix.ae'){
						cur_frm.toggle_display("policy_approver", 0);
						cur_frm.toggle_display("policy_description", 0);
						cur_frm.toggle_display("policy_questions", 0);
						cur_frm.toggle_display("policy_employee", 0);
						cur_frm.toggle_display("all_employee", 0);
						cur_frm.toggle_display("dubai_employee", 0);
						cur_frm.toggle_display("bangalore_employee", 0);
						cur_frm.toggle_display("department", 0);
					}
					cur_frm.add_custom_button(__("Read Complete Document"), function() {
						frappe.set_route("view-document", {
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

	if(cur_frm.doc.tablix_status == "Completed"){
		cur_frm.set_df_property("policy_description","read_only",1);
		cur_frm.set_df_property("policy_approver","read_only",1);
	}

	if(cur_frm.doc.tablix_status == "Waiting For Approval"){
		cur_frm.set_df_property("policy_description","read_only",1);
	}
}

frappe.ui.form.on('Policy Document Management', {
	before_save: function(frm) {
		if(frappe.session.user_email == cur_frm.doc.policy_request_by){
			var table = cur_frm.doc.policy_approver;
			for(var i=0; i<table.length; i++){
				if(table[i].decline > 0){
					frappe.model.set_value(table[i].doctype, table[i].name, "decline", 0);
				}
			}
		}
		if(cur_frm.doc.tablix_status == "Waiting For Approval"){
			cur_frm.assign_to.remove(cur_frm.doc.policy_request_by);
		}
	}
});

frappe.ui.form.on('Policy Document Management', {
	onload_post_render: function(frm){
		var approver = ["EMP/0031", "EMP/0035", "EMP/0027", "EMP/0140"];
		var approver_email = ["gopu@tablix.ae", "kartik@tablix.ae", "bala@tablix.ae", "rajesh.k@tablix.ae"];
		if(! cur_frm.doc.policy_request_by){
			cur_frm.set_value("policy_request_by", frappe.session.user_email);
		}

		if(! cur_frm.doc.policy_approver){
			for(var i=0;i<approver.length;i++){
				console.log(approver[i]);
				var child = frappe.model.get_new_doc("Policy Approvers",cur_frm.doc,"policy_approver");
				$.extend(child, {
					"employee": approver[i],
					"email": approver_email[i]
				});
			}
			cur_frm.refresh_field("policy_approver");
		}
	}
});

function check_approval(cur_frm){
	if(cur_frm.doc.tablix_status == "Waiting For Approval"){
		var table = cur_frm.doc.policy_approver;
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
				frappe.model.set_value("Policy Document Management", cur_frm.doc.name, "tablix_status", "Open");
			} else if(accept == table.length){
				frappe.model.set_value("Policy Document Management", cur_frm.doc.name, "tablix_status", "Completed");
			}
		}
	}
}

function waiting_approval(cur_frm){
	var state = cur_frm.doc.tablix_status;
	if(state == "Waiting For Approval"){
		cur_frm.assign_to.remove(cur_frm.doc.policy_request_by);
		var table = cur_frm.doc.policy_approver;
		for(var i=0;i<table.length;i++){
			if(table[i].email == frappe.session.user_email && table[i].accept == 0 && table[i].decline == 0){
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
		var table = cur_frm.doc.policy_approver;
		for(var i=0; i<table.length; i++){
			if(table[i].email == frappe.session.user_email){
				var old_reason = table[i].reason || "";
				frappe.model.set_value(table[i].doctype, table[i].name, "reason", old_reason+msg);
			}
		}
		get_choice(0, cur_frm, frappe.session.user_email, "accept", "decline", 1);
		send_notification(cur_frm, msg);
		d.hide();
	});

	d.show();
}

function send_notification(cur_frm, msg){
	if(msg){
		console.log(msg);	
		frappe.call({
			"method": "tablix.tablix_hr.doctype.policy_document_management.policy_document_management.send_reason",
			"args": {"msg": msg, "user": frappe.session.user_email, "doc": cur_frm.doc.name},
			"calllback": function(r){
				if(r){
					console.log(r);
				}
			}
		});
	}
}

function get_choice(value_1, cur_frm, email, button_1, button_2, value_2){
	var table = cur_frm.doc.policy_approver;
	for(var i=0; i<table.length; i++){
		if(table[i].email == email){
			frappe.model.set_value(table[i].doctype, table[i].name, button_1, value_1);
			frappe.model.set_value(table[i].doctype, table[i].name, button_2, value_2);
		}
	}
	cur_frm.refresh_field("policy_approver");
	cur_frm.assign_to.remove(frappe.session.user_email);
	check_approval(cur_frm);
	cur_frm.save();
}

frappe.ui.form.on("Policy Document Management", "all_employee", function(frm){
	if(cur_frm.doc.all_employee == 1){
		cur_frm.clear_table("policy_employee");
		cur_frm.clear_table("department");
		cur_frm.refresh_field("department");		

		frappe.call({
			method: "tablix.tablix_hr.doctype.policy_document_management.policy_document_management.get_employee_data",
			args: {"department": "ALL"},
			callback: function(r){
				if(r && r.message){
					var emps = r.message;
					for(var i=0;i<emps.length;i++){
						var child = frappe.model.get_new_doc("Policy Employee",cur_frm.doc,"policy_employee");
						$.extend(child, {
							"employee": emps[i].name,
							"employee_name": emps[i].employee_name,
							"email": emps[i].user_id,
						});
					}
					cur_frm.refresh_field("policy_employee");
				}
			}
		});
	} else{
		cur_frm.clear_table("policy_employee");
		cur_frm.refresh_field("policy_employee");
	}
});

frappe.ui.form.on("Policy Document Management", "dubai_employee", function(frm){
	if(cur_frm.doc.dubai_employee == 1){
		cur_frm.clear_table("policy_employee");
		cur_frm.clear_table("department");
		cur_frm.refresh_field("department");

		frappe.call({
			method: "tablix.tablix_hr.doctype.policy_document_management.policy_document_management.get_company_employee",
			args: {"department": "Tablix Technology LLC"},
			callback: function(r){
				if(r && r.message){
					var emps = r.message;
					for(var i=0;i<emps.length;i++){
						var child = frappe.model.get_new_doc("Policy Employee",cur_frm.doc,"policy_employee");
						$.extend(child, {
							"employee": emps[i].name,
							"employee_name": emps[i].employee_name,
							"email": emps[i].user_id,
						});
					}
					cur_frm.refresh_field("policy_employee");
				}
			}
		});
	} else {
		cur_frm.clear_table("policy_employee");
		cur_frm.refresh_field("policy_employee");
	}
});

frappe.ui.form.on("Policy Document Management", "bangalore_employee", function(frm){
	if(cur_frm.doc.bangalore_employee == 1){
		cur_frm.clear_table("policy_employee");
		cur_frm.clear_table("department");
		cur_frm.refresh_field("department");

		frappe.call({
			method: "tablix.tablix_hr.doctype.policy_document_management.policy_document_management.get_company_employee",
			args: {"department": "Tablix Technologies Pvt. Ltd."},
			callback: function(r){
				if(r && r.message){
					var emps = r.message;
					for(var i=0;i<emps.length;i++){
						var child = frappe.model.get_new_doc("Policy Employee",cur_frm.doc,"policy_employee");
						$.extend(child, {
							"employee": emps[i].name,
							"employee_name": emps[i].employee_name,
							"email": emps[i].user_id,
						});
					}
					cur_frm.refresh_field("policy_employee");
				}
			}
		});
	} else {
		cur_frm.clear_table("policy_employee");
		cur_frm.refresh_field("policy_employee");
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
						var child = frappe.model.get_new_doc("Policy Employee",cur_frm.doc,"policy_employee");
						$.extend(child, {
							"employee": emps[i].name,
							"employee_name": emps[i].employee_name,
							"email": emps[i].user_id,
						});
					}
					cur_frm.refresh_field("policy_employee");
				}
			}
		});
	}
}

frappe.ui.form.on("Policy Document Management", "departments", function(frm){
	if(cur_frm.doc.departments == "HR"){
		frappe.model.set_value("Policy Document Management", cur_frm.doc.name, "naming_series", "PDM-HR-");
	} else if(cur_frm.doc.departments == "Finance"){
		frappe.model.set_value("Policy Document Management", cur_frm.doc.name, "naming_series", "PDM-FA-");
	} else if(cur_frm.doc.departments == "Project Management"){
		frappe.model.set_value("Policy Document Management", cur_frm.doc.name, "naming_series", "PDM-PM-");
	} else if(cur_frm.doc.departments == "Pre-Sales"){
		frappe.model.set_value("Policy Document Management", cur_frm.doc.name, "naming_series", "PDM-PS-");
	} else if(cur_frm.doc.departments == "Purchase"){
		frappe.model.set_value("Policy Document Management", cur_frm.doc.name, "naming_series", "PDM-PR-");
	} else if(cur_frm.doc.departments == "Sales"){
		frappe.model.set_value("Policy Document Management", cur_frm.doc.name, "naming_series", "PDM-SL-");
	}
});
