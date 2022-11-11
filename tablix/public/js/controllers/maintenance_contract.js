
frappe.provide("tablix.maintenance_contract");

tablix.maintenance_contract.MaintenanceContract = tablix.manual_assign.ManualAssign.extend({

	init: function(args){
	
		$.extend(this, args);
	},

	setup: function(){
		var me = this;
		this.frm.set_query("so_number", function(){
			
			return {
				filters:{
					"docstatus":1
				}
			}	

		});	
	},	
	refresh: function(){
	
		this.make_dialog();
	}
	

})

cur_frm.script_manager.make(tablix.maintenance_contract.MaintenanceContract);
