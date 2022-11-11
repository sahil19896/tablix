// Copyright (c) 2018, Tablix and contributors
// For license information, please see license.txt

frappe.provide("tablix.project_team");
tablix.project_team.ProjectTeam = Class.extend({
	init: function(args){
		$.extend(this, args);
	},
	refresh: function(frm){
	},
	setup: function(frm){
	
		var me = this;
		this.frm.add_fetch("project_manager", "employee_name", "project_manager_full_name");
		this.frm.add_fetch("project_manager", "user_id", "project_manager_user_id");
		this.frm.add_fetch("employee", "employee_name", "employee_name", "items");
		this.frm.add_fetch("employee", "user_id", "user_id", "items");
	}
});

cur_frm.script_manager.make(tablix.project_team.ProjectTeam);
