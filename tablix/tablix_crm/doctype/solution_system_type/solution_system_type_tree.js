
frappe.provide("frappe.treeview_settings");
frappe.treeview_settings['Solution System Type'] = {

	show_expand_all: false,
	disable_add_node: true,
	breadcrumbs: __("Solution Systems"),
	title: __("Solution Systems"),
	get_tree_root: true,
	root_labels: "Systems",
	get_tree_nodes: "tablix.tablix_crm.doctype.solution_system_type.solution_system_type_tree.get_tree_nodes",
	add_tree_node: "tablix.tablix_crm.doctype.solution_system_type.solution_system_type_tree.add_tree_node",
	onload: function(treeview){
		console.log(treeview);
	},
	onrender: function(node){
		console.log(node);
	},
	get_label: function(node){
		var label = "";
		if(node.is_root && !node.parent_label){
			label = __("ELV");
		}
		else if(node.data.name){
			label = node.data.name;
		}
		
		return label;
	},
	click: function(node){
		if(node.is_root){
			return false;
		}
		if(node.data && node.data.expandable){
			$.extend(node.tree.args, {parent: node.data.name}); 
		}
		console.log(node);
	},
	fields:[
		{fieldname: "system_type", fieldtype: "Data", reqd:1, label: __("System Type") },
		{fieldname: "abbreviation_of_system", fieldtype: "Small Text", reqd: 1, label: __("System Type")},
		{fieldname: "description", fieldtype: "Small Text", reqd:1, label:__("Description of System")},
		{fieldname: "system_overview", fieldtype: "Text", reqd:1, label: __("System Overview") }
	],
	toolbar:[
			{
			toggle_btn: true
		},
			{
			condition: function(node){
				console.log(node);
				return node.is_root?false:true;
			},
			label: __("Edit"),
			click: function(node, btn){
				frappe.set_route("Form", "Solution System Type", node.data.name);
			},
			btnClass: "btn-xs"
		},
			{
			condition: function(node){
				var flag = "";
				if(node.is_root || node.data && node.data.expandable)flag = true;
				else flag = false;
				return flag;
				
			},	
			label: __("Add Child"),
			click : function(node, click){
				var parent_g = "";
				if(node.is_root){
					parent_g = "ELV";
				}
				else{
					parent_g = node.data.name;
				}
				var dialog = new frappe.ui.Dialog({
					title: "Create Solution System Type",
					fields:[
							{
							fieldname: "is_group", fieldtype:"Check",
							label: "Is Group", default: 1
						},
							{
							fieldname: "parent_system", fieldtype: "ReadOnly", default:parent_g,
							options: "Solution System Type",  label: __("Parent System Type"),
						},
							{
							fieldname: "system_type", fieldtype: "Data", 
							reqd:1, label: __("System Type") 
						},
							{
							fieldname: "abbreviation_of_system", fieldtype: "Data",
							reqd: 1, label: __("Abbreviation of System")
						},
							{
							fieldname: "description", fieldtype: "Small Text", 
							reqd:1, label:__("Description of System")
						},
							{
							fieldname: "system_overview", fieldtype: "Text", reqd:1,
							label: __("System Overview") 
						}
								
					],
					primary_action_label: __("Save"),
					primary_action: function(doc){
						console.log(doc);
						frappe.call({
							method: "tablix.tablix_crm.doctype.solution_system_type.solution_system_type_tree.add_tree_node",
							args: {frm: doc},
							freeze: true,
							freeze_message: __("Wait while we're adding new node in systems"),
							callback: function(res){
								dialog.hide();
								cur_tree.rootnode.reload();
							}	
						})
					},
					only_input:true,
				});
				dialog.get_field("parent_system").set_custom_query = function(args){
						console.log(args);
						args.filters = {};
						$.extend(args.filters, {
							is_group: 1,
							enabled: 1
						});
				
				}
				dialog.show();
			},
			btnClass: "btn-xs"
		}
		
		
	]
}
