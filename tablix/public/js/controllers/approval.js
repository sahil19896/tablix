
frappe.provide("tablix.approval")


/*
	Send for approval

*/
tablix.approval.send_for_approval = function(doctype, frm,  status, remark){

	console.log(doctype, frm, status, remark);
	frappe.call({
		method: "tablix.whitelisted.send_for_approval",
		args: {"status": status, "doc": frm.doc, "remark": remark},
		callback: function(r) {
			if(r.exc) {
				msgprint(__("There were errors."));
			} 
			else {
				msg = format("Sent Succesfully to {0} Tablix rep !", [status]);
				msgprint(__(msg));
				
				tablix.approval.make_comment("Workflow", status, frm);
			}
		}
	});
}

/*

	Make comment after sending approval

*/
tablix.approval.make_comment = function(doctype, status, frm){
	msg = format("Succesfully send to {0} Tablix Rep !", [status]);
	frm.timeline.insert_comment(doctype, msg);
	frm.refresh(); 
}



tablix.approval.Create = Class.extend({

	init: function(frm){
		this.frm = frm;
		this.doctype = frm.doc.doctype;
		this.make();
		
	},

	make: function(){

		var doctype = this.doctype;
		this.approval = null;
		if(doctype == "Purchase Order"){
			console.log("PO")
			this.approval = new tablix.approval.PurchaseOrderApproval(this.frm)
		}
		else if(doctype == "Sales Order"){
			console.log("SO")
			this.approval = new tablix.approval.SalesOrderApproval(this.frm);
	
		}	

		else if(doctype == "Material Request"){
			this.approval = new tablix.approval.MaterialRequest(this.frm);
		}
		else if(doctype == "Opportunity"){
			console.log("Opp");
			this.approval = new tablix.approval.OpportunityApproval(this.frm);
		}
		
	
	}

});


/*
 Approval for  Purchase Order
*/

tablix.approval.PurchaseOrderApproval = Class.extend({
	
	init: function(frm){

		this.frm = frm;
		this.doctype = frm.doc.doctype;
		this.make();
	},

	make: function(){
		this.make_approval();
	},

	make_approval: function(){
		var me = this;
		var doc = me.frm.doc;
		
		if((doc.approval == "Open" || doc.approval == "Manager Disapproved" || doc.approval == "Finance Disapproved")  && frappe.user.has_role("Purchase User") && !(frappe.user.has_role("Commercial Manager")))
		
			this.frm.add_custom_button(__('Manager Approval'), function(){
				tablix.approval.send_for_approval("Workflow", me.frm, "Manager Approve");
			});

		if(doc.approval == "Open" && frappe.user.has_role("Commercial Manager"))
		{
			me.frm.add_custom_button(__('Approve'),function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "Commercial Manager Approve");
			});
			me.add_custom_button(__('Disapprove'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm,  "Commercial Manager Disapprove");

			});
		}

		if(me.doc.approval == "Manager Approved" && frappe.user.has_role("CFO"))
		{
			me.add_custom_button(__('Approve'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "CFO Approve")
			});
			me.add_custom_button(__('Disapprove'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "CFO Disapprove");
			});
			
		}

		if(me.doc.reason != "")
		{
			me.set_intro(__(me.doc.reason));
		}

	},
	manager_disapproved: function(){
		
		var dialog = new frappe.ui.Dialog({
			title: "Send for Approval with Remark",
			fields: [
				{"fieldtype": "Text", "label": __("Remarks"), "fieldname": "reason",
					"reqd": 1 },
				{"fieldtype": "Button", "label": __("Send"), "fieldname": "finish"},
			]
		});

		dialog.show();
		dialog.fields_dict.finish.$input.click(function() {
			arg = dialog.get_values();
			if(!arg) return;
			var reason = arg.reason;
			return me.call({
				doc: me.doc,
				method: "send_notification",
				args: {"reason": "cm_rejected", "remark": reason},
				callback: function(r) {
					if(r.exc) {
						dialog.hide();
						msgprint(__("There were errors."));
					} else {
						dialog.hide();
						me.timeline.insert_comment("Workflow", "PO disapproved by Commercial Manager");
						msgprint(__("Succesfully Send to Commercial Team !!!!!"));
						location.reload();
					}
				}
			});
		});

	}

});

/*
	End of Purchase Order Approval

/*


Approval for Opportunity

*/


tablix.approval.OpportunityApproval = Class.extend({


	init: function(frm){

		this.frm = frm;
		this.doctype = frm.doc.doctype;
		this.make();
	},

	make: function(){

		console.log(this);
		this.make_approval();
	},


	make_approval: function(){

		/*
			This code copy  from Opportunity and pasted here to make it more clear and readable
		*/

		this.refresh_Count =1;
		var me =this;
		var df = frappe.meta.get_docfield("Compliance", "technical_compliance", me.frm.doc.name);
		df.read_only = 1;
		var df = frappe.meta.get_docfield("Compliance", "commercial_compliance", me.frm.doc.name);
		df.read_only = 1;

		console.log("Sahil");
		if(me.frm.doc.status == "Open")
		{       
			if(me.frm.custom_buttons.hasOwnProperty("Send for Approval"))
				return false;
			me.frm.add_custom_button(__('Send for Approval'), function(event){
				
				
				tablix.approval.send_for_approval("Workflow", me.frm, "Need Approval");
			});
		}

		if((frappe.user.has_role("Security") || frappe.user.has_role("AV") || frappe.user.has_role("BMS") || frappe.user.has_role("Business Automation"))  && (me.frm.doc.status == "Boq" || me.frm.doc.status == "RFQ Approved"))
		{       
			me.frm.add_custom_button(__('BoQ'), function(event){
				me.cscript.create_boq();
			});
			me.frm.add_custom_button(__('Need more info'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm,  "Insufficient Info");
		 
			});
		}
		if((frappe.user.has_role("CEO") || frappe.user.has_role("CBDO")) && (me.frm.doc.status == "Rfq" || me.frm.doc.status == "RFQ"))
		{       
			me.frm.add_custom_button(__('KAM Approve'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "SAM Approval");
			});
			me.frm.add_custom_button(__('Need more info'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "Insufficient Info")
			});
		}
		if(frappe.user.has_role("COO") && me.frm.doc.status == "KAM Approved")
		{       
			me.frm.dd_custom_button(__('COO Approve'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "COO Approval");
			});
			me.frm.add_custom_button(__('Need more info'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "Insufficient Info");
			});
		}
		if(frappe.user.has_role("CBDO") && me.frm.doc.status == "COO Approved")
		{       
			me.frm.add_custom_button(__('CBDO Approve'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "CBDO Approval");
			});
			me.frm.add_custom_button(__('Need more info'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "Insufficient Info");
			});
		}
		if(me.frm.doc.status == "Insufficient Information")
		{       
			me.call({
				doc: me.doc,
				method: "insufficient_info_remark",
				callback: function(r) {
					if(r.exc) {
						msgprint(__("There were errors."));
					} else {
						console.log("success");
						console.log(r.message);
						me.set_intro(__(r.message));
					}
				}
			});
		}


		if((me.frm.doc.status==="Rfq" || me.frm.doc.status==="RFQ")  && (me.frm.doc.prev_status==="Rfq" || me.frm.doc.prev_status==="RFQ") && !(frappe.user.has_role("Sales Master Manager")))
		{       
			//me.timeline.insert_comment("Workflow", "Information Added");
			me.frm.add_custom_button(__('Information Added'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "Send for Approval")
			});
		 
		}
		if(me.frm.doc.status==="KAM Approved" && me.frm.doc.prev_status==="KAM Approved"  && !(frappe.user.has_role("Sales Master Manager")))
		{       
			//me.timeline.insert_comment("Workflow", "Information Added");
			me.frm.add_custom_button(__('Information Added'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "Send for Approval");
			});
		}
		if(me.frm.doc.status==="COO Approved" && me.frm.doc.prev_status==="COO Approved"  && !(frappe.user.has_role("Sales Master Manager")))
		{
			//me.timeline.insert_comment("Workflow", "Information Added");
			me.frm.add_custom_button(__('Information Added'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "Send for Approval");
			});
		}
		if(me.frm.doc.status==="RFQ Approved" && me.frm.doc.prev_status==="RFQ Approved"  && !(frappe.user.has_role("Sales Master Manager")))
		{
			//me.timeline.insert_comment("Workflow", "Information Added");
			me.frm.add_custom_button(__('Information Added'), function(event){
				tablix.approval.send_for_approval("Workflow", me.frm, "Notify D&E");
			});
		}
		if(me.frm.doc.status==="RFQ Approved" || me.frm.doc.status==="Boq" || me.frm.doc.status==="BOQ" || me.frm.doc.status==="Quotation" && !(frappe.user.has_role("Sales Manager")))
		{
			me.frm.add_custom_button(__("Close"), function() {
					me.frm.set_value("status", "Closed");
					me.frm.save();
				});
		}
		if(me.frm.perm[0].write && me.frm.doc.docstatus==0 && !((frappe.user.has_role("Security") || frappe.user.has_role("AV") || frappe.user.has_role("BMS") || frappe.user.has_role("Business Automation"))) && !(frappe.user.has_role("Sales Master Manager"))){
                	if(me.frm.doc.status==="Open") {
                        	me.frm.add_custom_button(__("Close"), function() {
                                	me.frm.set_value("status", "Closed");
                        	        me.frm.save();
                      	  	});
			}
                	else {
                        	me.frm.add_custom_button(__("Reopen"),
                        	me.cscript['Reopen']);
                	}
        	}

        	if(me.frm.doc.status!=="Lost" && !((frappe.user.has_role("Security") || frappe.user.has_role("AV") || frappe.user.has_role("BMS") || frappe.user.has_role("Business Automation"))) && !(frappe.user.has_role("Sales Master Manager"))) {
                	if(me.frm.doc.status!=="Quotation") {
                        	me.frm.add_custom_button(__('Lost'),
                                	me.cscript['Declare Opportunity Lost']);
                	}

		}
	},
	
	insufficient_info: function(){
		var dialog = new frappe.ui.Dialog({
			title: "Need more info",
			fields: [
				{"fieldtype": "Text", "label": __("Remarks"), "fieldname": "reason",
					"reqd": 1 },
				{"fieldtype": "Button", "label": __("Update"), "fieldname": "update"},
			]

		});
		dialog.show();
		dialog.fields_dict.update.$input.click(function() {
			args = dialog.get_values();
			if(!args) return;
			me.set_value("prev_status", me.doc.status)
			me.set_value("status", "Insufficient Information");
			me.set_value("to_discuss", args.reason);
			me.set_intro(__(args.reason));
			me.timeline.insert_comment("Workflow", "Insufficient Information Reason: " + args.reason);
			me.save();
			dialog.hide();

			return me.call({
				doc: me.doc,
				method: "send_notification",
				args:"need_info",
				callback: function(r) {
					if(r.exc) {
						dialog.hide();
						msgprint(__("There were errors."));
					} else {
						dialog.hide();
						//msgprint(__("Succesfully Send for Approval !!!!!"));
						//location.reload();
					}
				}
			});


		});

	}

});

/*

 End of Oppprtunity Approval

*/
/*

Approval for Sales Order

*/


tablix.approval.SalesOrderApproval = Class.extend({


	init: function(frm){

		this.frm = frm;
		this.doctype = frm.doc.doctype;
		this.make();
	},

	make: function(){

		console.log(this);
		this.make_approval();
	},


	make_approval: function(){

		var me =this;

		if(me.frm.doc.docstatus==0 && me.frm.doc.so_status == "Approved")
			{        
				 me.frm.savesubmit();
			}
			if(frappe.user.has_role("Sales Manager") && me.frm.doc.so_status == "Open")
			{       
				me.frm.add_custom_button(__('Send for Approval'), function(event){
					tablix.approval.send_for_approval("Workflow", me.frm, "Send for Approval")
				});
			}
			if(frappe.user.has_role("Sales Manager") && me.frm.doc.so_status == "Needs Clarification")
			{
				me.frm.add_custom_button(__('Send for Approval'), function(event){
					tablix.approval.send_for_approval("Workflow", me.frm, "Send for Approval");
				});
			}       
		
			if((frappe.user.has_role("CEO") || frappe.user.has_role("CBDO")) && me.frm.doc.so_status == "Open")
			{
				me.frm.add_custom_button(__('KAM Approve'), function(event){
					tablix.approval.send_for_approval("Workflow", me.frm, "KAM Approved");
				});
				
				me.frm.add_custom_button(__('Need Info'), function(event){
					tablix.approval.send_for_approval("Workflow", me.frm, "Need Info");
				});
			}       
			if(frappe.user.has_role("COO") && me.frm.doc.so_status == "KAM Approved")
			{
				me.frm.add_custom_button(__('COO Approve'), function(event){
					tablix.approval.send_for_approval("Workflow", me.frm, "COO Approved");
				});

				me.frm.add_custom_button(__('Need Info'), function(event){
					tablix.approval.send_For_approval("Workflow", me.frm, "Need Info");
				});
			}
			if(frappe.user.has_role("CBDO") && me.frm.doc.so_status == "COO Approved")
			{
				me.frm.add_custom_button(__('CBDO Approve'), function(event){
					tablix.approval.send_for_approval("Workflow", me.frm, "CBDO Approved");
				});

				me.frm.add_custom_button(__('Need Info'), function(event){
					tablix.approval.send_for_approval("Workflow", me.frm, "Need Info");
				})
			}
			if(frappe.user.has_role("CFO") && me.frm.doc.so_status == "CBDO Approved")
			{
				me.frm.add_custom_button(__('CFO Approve'), function(event){
					tablix.approval.send_for_approval("Workflow", me.frm, "CFO Approved");
				});

				me.frm.add_custom_button(__('Need Info'), function(event){
					tablix.approval.send_for_approval("Workflow",me.frm, "Need Info");
				});
			}
			if(me.frm.doc.reason != "")
			{
				me.frm.set_intro(__(me.frm.doc.reason));
			}

		if (this.frm.doc.docstatus===0)
			{
				me.frm.add_custom_button(__('Quotation'),
					function() {
						erpnext.utils.map_current_doc({
							method: "erpnext.selling.doctype.quotation.quotation.make_sales_order",
							source_doctype: "Quotation",
							get_query_filters: {
								docstatus: 1,
								status: ["!=", "Lost"],
								order_type: me.frm.doc.order_type,
								customer: me.frm.doc.customer || undefined,
								company: me.frm.doc.company
							}
						})
					}, __("Get items from"));
			}

			this.order_type();


	},
	order_type: function() {
                this.frm.toggle_reqd("delivery_date", this.frm.doc.order_type == "Sales");
        },

});
/*

	End of Sales Order Approval
*/
/*

Approval for Material Request

*/


tablix.approval.MaterialRequestApproval = Class.extend({


	init: function(frm){

		this.frm = frm;
		this.doctype = frm.doc.doctype;
		this.make();
	},

	make: function(){

		console.log(this);
		this.make_approval();
	},


	make_approval: function(){
		
	},

});

/*
 End of Material Request Approvail

*/
