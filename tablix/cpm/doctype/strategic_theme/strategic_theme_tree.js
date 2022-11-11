/*
	Added By Sahil
	Developer Sahil
	Email sahil.saini@tablix.ae
*/

frappe.provide("frappe.treeview_settings");
frappe.treeview_settings['Strategic Theme'] = {
	show_expand_all: false,
	disable_add_node: true,	
	breadcrumbs: __('Score Cards'),
	title: __('Score Card'),
	get_tree_root: true,
	filters:[
			{
			fieldname: "company", fieldtype: "Link", options: "Company", 
			label: __("Company"), default: frappe.sys_defaults.company
		},
			{
			fieldname: "fiscal_year", fieldtype: "Link", options: "Fiscal Year", 
			label: __("Fiscal Year"), default: frappe.sys_defaults.fiscal_year
		},
		
	],
	root_label: 'Score Cards',
	get_tree_nodes: "tablix.cpm.utils.get_children",
	add_tree_node: "tablix.cpm.utils.add_child",
	onload: function(treeview){
		//console.log(treeview);
		var get_company = function(){
			return treeview.page.fields_dict.company.get_value();
		}
		var get_fiscal_year = function(){
			return treeview.page.fields_dict.company.get_value();
		}
		treeview.page.add_inner_button(__("View Report"), function(){
			frappe.set_route("query-report", "Scorecard", {"fiscal_year": get_fiscal_year, company:get_company()});
		})
		
	},
	onrender: function(node){
		
	},
	get_label: function(node){
		var label = ""
		if(node.is_root)  label= 'Score Card';
		else label=node.data.title;
		return label;
	},
	click: function(node){
		var filters = {};
		var cur_treeview = frappe.views.trees['Strategic Theme'];
		$.extend(node.tree.args, {
			company: cur_treeview.page.fields_dict.company.value,
			fiscal_year: cur_treeview.page.fields_dict.fiscal_year.value
		});
		if(node.data.is_strategic){
			$.extend(node.tree.args, {is_strategic: 1, is_root:true, is_objective:0})
		}
		if(node.data.is_objective){
			$.extend(node.tree.args, {is_objective:1, is_root:true, is_strategic:0})
		
		}
		
	},
	fields:[
		{fieldname: 'select_series', fieldtype: 'Select', options:['F', 'C', 'IP', 'LG'], reqd:1},
		{fieldname: 'title', fieldtype: 'Data', reqd:1},
		{fieldname: 'fiscal_year', fieldtype:'Link', options: 'Fiscal Year',},
		{fieldname: 'description', fieldtype:'Small Text', reqd:1},
	],
	extend_toolbar: false,
	toolbar: [
			{toggle_btn: true},
			{
			condition: function(node){
				return !node.is_root;
			},
			label: __("Edit"),
			click: function(node, btn){
				if(node.is_root) return false;
				frappe.set_route("Form", node.data.doctype, node.data.value);	
			},
			btnClass: "xs-btn"
		},
			{
			condition: function(node){
				return node.data && node.data.expandable===1 || node.is_root;	
			},
			label: __("Add Child"),
			click: function(node, btn){
				var fields = [];
				var title = "";
				if(node.is_root){
					title = "Strategic Theme";
					fields.push({
						fieldname: "perspective", label: __("Select Perspective"), reqd: 1,
						fieldtype: "Link", options:"Perspective"
					});
					
					fields.push({
						fieldname: "select_series", label: __("Select Series"), reqd: 1,
						fieldtype: "Select", options:["F","C","IP","LG"], default: "F"
					});
					fields.push({
						fieldname: "title", label: __("Title"), 
						reqd: 1, fieldtype: "Data"
					});
					fields.push({
						fieldname: "fiscal_year", label: __("Fiscal Year"), reqd: 1,
						fieldtype: "Link", options:"Fiscal Year"
					});
					fields.push({
						fieldname: "company", label: __("Company"), reqd: 1,
						fieldtype: "Link", options:"Company"
					});
					fields.push({
						fieldname: "description", label: __("Description of Objective"), reqd: 1,
						fieldtype: "Small Text"
					});
					fields.push({fieldname: "strategic_owner", label: __("Strategic Owner"), reqd: 1,
						 fieldtype: "Link", options: "Employee", onchange: function(){
									frappe.db.get_value("Employee", dialog.get_value("strategic_owner"), ["user_id", "employee_name"],
										function(res){
											dialog.set_value("strategic_owner_name", res.employee_name);
											dialog.set_value("strategic_owner_email", res.user_id)
											dialog.refresh_fields(["strategic_owner_name", "strategic_owner_email"])
									});
						},
					});
					fields.push({
						fieldname: "strategic_owner_name", label: __("Strategic Owner Name"), reqd: 1,
						 fieldtype: "Read Only", options: 'strategic_owner.employee_name'
					});
					fields.push({
						fieldname: "strategic_owner_email", label: __("Strategic Owner Email"), reqd: 1,
						fieldtype: "Read Only", options: "strategic_owner.user_id"
					});
					
				}
				else if(node.data && node.data.doctype == "Strategic Theme"){
				
					title = "Strategic Objective";
					fields.push({
						fieldname: "select_series", label: __("Select Series"), 
						reqd: 1, fieldtype: "Read Only", default: node.data.select_series
					});
					fields.push({
						fieldname: "strategic_theme", label: __("Strategic Theme"),
						reqd: 1, fieldtype: "Read Only", default: node.data.strategic_theme
					});
					fields.push({
						fieldname: "title", label: __("Title"), 
						reqd: 1, fieldtype: "Data"
					});
					fields.push({
						fieldname: "description", label: __("Description of Objective"),
						reqd: 1, fieldtype: "Small Text"
					});

				}
				else if(node.data && node.data.doctype== "Strategic Objective"){
					title = "Indicator";
					fields.push({
						fieldname: "select_series", label: __("Select Series"), reqd: 1,
						 fieldtype: "Read Only", "default": node.data.select_series,
					});
					fields.push({
						fieldname: "strategic_theme", label: __("Strategic Theme"), reqd: 1,
						 fieldtype: "Read Only", "default": node.data.strategic_theme,
					});
					fields.push({
						fieldname: "strategic_objective", label: __("Strategic Objective"), reqd: 1,
						 fieldtype: "Read Only", "default": node.data.strategic_objective,
					});
					fields.push({
						fieldname: "title", label: __("Title"), reqd: 1,
						 fieldtype: "Data"
					});
					fields.push({
						fieldname: "frequency", label: __("Frequency"), 
						reqd: 1, fieldtype: "Select", options:["", "Monthly", "Yearly"]
					});
					fields.push({
						fieldname: "uom", label: __("UOM"), reqd: 1, fieldtype: "Select", 
						options:["", "Value", "Percentage", "Data"], onchange: function(){
							dialog.set_value("base_value", null);
							dialog.set_value("base_percentage", null);
							dialog.set_value("base_data", null);
							dialog.set_value("target_value", null);
							dialog.set_value("target_percentage", null);
							dialog.set_value("target_data", null);
							dialog.set_value("actual_value", null);
							dialog.set_value("actual_percentage", null);
							dialog.set_value("actual_data", null);
						}
					});
					fields.push({
						fieldname: "base_value", label: __("Base Value"), 
						fieldtype: "Currency", depends_on:"eval:doc.uom=='Value'"
					});
					fields.push({
						fieldname: "base_percentage", label: __("Base Percentage"), 
						fieldtype: "Percent", depends_on:"eval:doc.uom=='Percentage'"
					});
					fields.push({
						fieldname: "base_data", label: __("Base Data"), fieldtype: "Select", 
						options:["Yes", "No"], default:"Yes", depends_on:"eval:doc.uom=='Data'"
					});
					fields.push({
						fieldname: "actual_value", label: __("Actual Value"), 
						fieldtype: "Currency", depends_on:"eval:doc.uom=='Value'"
					});
					fields.push({
						fieldname: "actual_percentage", label: __("Actual Percentage"), 
						fieldtype: "Percent", depends_on:"eval:doc.uom=='Percentage'"
					});
					fields.push({
						fieldname: "actual_data", label: __("Actual Data"), fieldtype: "Select", 
						options:["Yes", "No"], default:"Yes", depends_on:"eval:doc.uom=='Data'"
					});
					fields.push({
						fieldname: "target_data", label: __("Target Data"), 
						fieldtype: "Data", depends_on:"eval:doc.uom==='Data'"
					});
					fields.push({
						fieldname: "target_value", label: __("Target Value"), 
						fieldtype: "Currency", depends_on:"eval:doc.uom==='Value'"
					});
					fields.push({
						fieldname: "target_percentage", label: __("Target Percentage"), 
						fieldtype: "Percent", depends_on:"eval:doc.uom==='Percentage'"
					});
				}
				var dialog = new frappe.ui.Dialog({
					fields:fields,
					title: __(format("Add {0}", [title])),

				});
				dialog.set_primary_action(__("Add"), function(doc){
					var data = node.data;
					if(node.data && node.data.doctype==="Strategic Objective"){
						if(!(doc.base_value || doc.base_percentage || doc.base_data)){
							//frappe.msgprint(__("Please enter <b>Base</b> Value/Data/Percentage"));
							//return false;
						
						}
						if(!(doc.actual_value || doc.actual_percentage || doc.actual_data)){
							//frappe.msgprint(__("Please enter <b>Actual</b> Value/Data/Percentage"));
							//return false;
						
						}
						if(!(doc.target_value || doc.target_percentage || doc.target_data)){
							//frappe.msgprint(__("Please enter <b>Target</b> Value/Data/Percentage"));
							//return false;
						}
					}
					$.extend(doc, {doctype: title});
					frappe.call({
						method: "tablix.cpm.utils.add_child",
						freeze: true,
						args: {data: data, doc: doc},
						freeze_message: __("Adding Child"),
						callback: function(res){
							dialog.hide();
							node.load_all()	
							console.log(res);
						}
					})
				});
				dialog.show();
			},
			btnClass: "xs-btn"
		},
			{
			condition: function(node){
				return !node.is_root;
			},
			label: __("Rename"),
			click: function(node, btn){
				frappe.msgprint(__("Click on Edit Button to Rename"));
				return false;
			},
			btnClass: "xs-btn"
		},
			{
			condition: function(node){
				return !node.is_root;
			},
			label: __("Delete"),
			click: function(node, btn){
				frappe.msgprint(__("Disabled  Deletion from Tree"));
				return false;
			},
			btnClass: "xs-btn"
		}
	],
};

