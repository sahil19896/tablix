

frappe.listview_settings['Opportunity'] = {
	colwidths: {
		subject:2,
	},
	add_fields: ["customer_name", "opportunity_type", "enquiry_from", "status"],
	get_indicator: function(doc) {
		console.log(doc);
		var indicator = [__(doc.tablix_status), frappe.utils.guess_colour(doc.tablix_status), "tablix_status,=," + 
												doc.tablix_status];
		if(doc.tablix_status=="Quotation") {
			indicator[1] = "green";
		}
		else{
			indicator  = [__(doc.tablix_status), tablix.get_status_color(doc.tablix_status)]
		}
		return indicator;
	},
	onload: function(listview) {
		var method = "erpnext.crm.doctype.opportunity.opportunity.set_multiple_status";

		listview.page.add_menu_item(__("Set as Open"), function() {
			listview.call_for_selected_items(method, {"status": "Open"});
		});

		listview.page.add_menu_item(__("Set as Closed"), function() {
			listview.call_for_selected_items(method, {"status": "Closed"});
		});
		tablix.add_export_button(listview, null);
	}
};
