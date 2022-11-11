
frappe.provide("tablix.controllers.opportunity");

cur_frm.add_fetch("lead", "lead_name", "contact_person");
cur_frm.add_fetch("account_manager", "full_name", "account_manager_name");
cur_frm.add_fetch("bdm", "full_name", "bdm_name");

tablix.controllers.opportunity = erpnext.crm.Opportunity.extend({
	init: function(args){
		$.extend(this, args);
	},
	refresh: function(){
		var frm = this.frm;
		var status = frm.doc.tablix_status;
		
		$("div.document-link[data-doctype='Boq'] *").prop('disabled',true);
		if(frm.is_new()) return false;
		this.make_dialog(); // for manual assignment
		if((status=="Approved" || status== "RFQ Approved" || status=="Pre Sales Manager Approved" || status=="Pre Sales Head Approved")){
		
			frm.add_custom_button(__("BOQ Profile"), function() {
				frappe.model.open_mapped_doc({
					method: "tablix.boq.whitelisted.make_boq_profile",
					frm:frm
				})			
			}, __("Make"));

		} 
		
		if(status.search("Rejected") >= 0){
			frm.set_intro(__(frm.doc.reason));
		}
		
		frm.set_df_property("technical_compliance", "read_only", 1, frm.doc.name, "compliance");
		frm.set_df_property("commercial_compliance", "read_only", 1,  frm.doc.name, "compliance");
	},	
	status: function(){
		var frm = this.frm;
		frm.set_value("tablix_status", frm.doc.status);
		frm.save();
	},	
	validate: function() {
		var frm = this.frm;
		if(frm.doc.tender == "Yes"){
			//frm.set_value("is_proposal", 1);
			frm.doc.is_proposal = 1;
		}
		
	},
	zone: function(){
		var me = this;
		me.frm.clear_table("area_head");
		me.frm.refresh_fields("area_head");
		if(me.frm.doc.zone){
			frappe.call({
				"method": "tablix.whitelisted.get_area_head",
				"args": {"name": me.frm.doc.zone},
				"callback": function(r){
					if(r){
						var data = r.message;
						if(data){
							for(var i=0;i<data.length;i++){
								var child=frappe.model.get_new_doc("Area Head", me.frm.doc,"area_head");
								$.extend(child, {
									"area_head": data[i].area_head,
									"head_name": data[i].head_name
								});
							}
							cur_frm.refresh_field("area_head");
						}
					}
				}
			});
	
			if(me.frm.doc.zone == "Area-00"){
				me.frm.toggle_enable("buyer", 1);
				me.frm.toggle_enable("engineer", 1);
				cur_frm.clear_table("area_head");
				cur_frm.refresh_field("area_head");
			}else{
				me.frm.toggle_enable("buyer", 0);
				me.frm.toggle_enable("engineer", 0);
			}
		} else{
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "area", "");
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "engineer", "");
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "buyer", "");
			me.frm.clear_table("area_head");
			me.frm.refresh_fields("area_head");
		}
	},

	onload: function(){
		var me = this;
		me.frm.fields_dict['zone'].get_query = function(doc) {
			return {
				filters: {
					"enable": 1
				}
			}
		}
	},

	before_save: function(){
		var me = this;
		if(me.frm.doc.party_name == "Tablix Technologies Pvt Ltd"){
			frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "naming_series", "OPTY-IND-2021-");
		}
	}
});

var controller = tablix.controllers.opportunity.extend(new tablix.manual_assign.ManualAssign);
cur_frm.script_manager.make(controller);
cur_frm.cscript.lead = function(){
	console.log("override standard lead function");
}
