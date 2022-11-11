frappe.listview_settings['ToDo'] = {
	colwidths: {
		subject: 3,
		indicator: 1
	},
	column_colspan:{
		assigned_by: 1,
		reference_name:1,
		date:1	
	},
	add_columns:[
		{fieldname: "status", fieldtype:"Select", title: "Ref-Type/Ref-Name", type: "Indicator"},
		{fieldname: "assigned_by", fieldtype:"Link", options:"User"},
		{fieldname: "reference_name", fieldtype: "Dynamic Link", options:"reference_type"},
		{fieldname: "date", fieldtype: "Date"}
	],
	
	onload: function(me) {
		var status_column = {type: "Indicator", title: "Ref-Name",}
		//me.list_renderer.add_columns[1] = status_column;
		frappe.route_options = {
			"owner": frappe.session.user,
			"status": "Open"
		};
		me.page.set_title(__("To Do"));

	},
	get_indicator: function(item){
		
		var color = item.status=="Open"?"red":"green";
		status = item.reference_name;
		return [status, color];
	},
	hide_name_column: true,
	refresh: function(me) {
		// override assigned to me by owner
		me.page.sidebar.find(".assigned-to-me a").off("click").on("click", function() {
			var assign_filter = me.filter_list.get_filter("assigned_by");
			assign_filter && assign_filter.remove(true);

			me.filter_list.add_filter(me.doctype, "owner", '=', frappe.session.user);
			me.run();
		});

		// add assigned by me
		me.page.add_sidebar_item(__("Assigned By Me"), function() {
			var assign_filter = me.filter_list.get_filter("owner");
			assign_filter && assign_filter.remove(true);

			me.filter_list.add_filter(me.doctype, "assigned_by", '=', frappe.session.user);
			me.run();
		}, ".assigned-to-me");
	},
	add_fields: ["reference_name", "status", "date", "assigned_by", "reference_type"],
}

