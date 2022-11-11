
/*

	Developer Varna Manoj
	Email sahil.saini@tablic.ae
*/

frappe.provide("tablix");
frappe.provide("tablix.info");

$(document).bind('toolbar_setup', function() {
        frappe.app.name = "boq";
	$(".dropdown-help").empty();
        $('.navbar-home').html('<span  style=color:white"> Home </span>');
});

$(document).ready(function(){

	$(".dropdown-help").empty();
	if(window.google && google.charts){
		google.charts.load("current", {packages: ['corechart','bar']});
	}
	if(!frappe.utils.format){
	
		frappe.utils.format = format;
	}
});

$.extend(tablix, {

	create_boq: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.opportunity.opportunity.make_boq",
			frm: cur_frm
                });
                cur_frm.timeline.insert_comment("Workflow", "Converted to BOQ");
	},
	update_leave: function(frm){
		
		frappe.call({
			method: "tablix.whitelisted.get_remaining_leaves",
			args: {"doc": frm.doc},
			callback: function(res){
				if(res && res.message){
					balance_leave = res.message.balance_leave;
					frm.set_value("total_leaves_left", balance_leave);
					frm.refresh();
				}
			}
		});
	},
	read_only: function(frm, doctype, fields, val){
		
		if(typeof fields == 'string'){
			field = frappe.meta.get_docfield(doctype, fields, frm.doc.name);
			if(field)
				field.read_only = 1;
		 
		}
		else if($.isArray(fields)){
			for(var i=0; i<fields.length; i++){
				field = frappe.meta.get_docfield(doctype, fields[i], frm.doc.name);
				if(field)
					field.read_only = 1;
			}
		}
	},
	calculate_rm_cost_sale_margin:function(doc){
		var rm = doc.items || [];
		for(var i=0;i<rm.length;i++) {
			margin = flt(rm[i].margin_percent) / 100;
			margin = flt(1- margin);
			amt = flt(rm[i].current_cost) / margin;
			int_amt = parseInt(amt);
			flt_amt = amt.toFixed(2)
			num_dec = (flt(amt) - int_amt).toFixed(2);
			console.log(num_dec);
			num_dec = num_dec.toString();
			num_dec = num_dec.slice(2,4);
			if(num_dec != "00") {
				amt = int_amt + 1;
			}
			set_multiple('Boq Item',rm[i].name, {'selling_price': amt}, 'items');
			sale_amt = amt * rm[i].qty;
			set_multiple('Boq Item',rm[i].name, {'sale_amount': sale_amt}, 'items');
			margin_amt = flt(sale_amt) - flt(rm[i].cost_amount);
			set_multiple('Boq Item',rm[i].name, {'margin': margin_amt}, 'items');
		}
	},
	
	update_price_list: function(frm, item){

		if(!frm.doc.is_project || frm.doc.is_amc){
			return false;
		}
		if(!frm.doc.boq_from){
			frappe.msgprint("Please To [Lead/Customer]");
			return false;
		}
		if(frm.doc.customer && frm.doc.customer_code == "MAF"){
			
			frappe.call({
				method: "tablix.whitelisted.get_price_list",
				args: {doc: frm.doc, item: item},
				callback: function(res){
					console.log(res);
					if(res && res.message){
						var _frm = frm.fields_dict.items.grid.grid_rows_by_docname[item.name];
						var prices = res.message.length >= 1? res.message[0] : null;
						if(!prices){
							frappe.msgprint(_("No Active Price List found for this particular item"));
							return
						}
						_frm.doc.current_cost = prices.buying_price;
						_frm.doc.selling_price = prices.selling_price;
						_frm.doc.margin = prices.margin_amount;
						_frm.doc.margin_percent = prices.margin_percent;
						_frm.doc.cost_amount = prices.cost_price;
						_frm.doc.sale_amount = prices.sales_price;
						_frm.doc.max_qty = prices.maximum_quantity;	
					
					}
					_frm.refresh();
				}
			});
			
		}
	},
	get_status_color: function(status){

		var color = "brown";
		if(frappe.boot.tablix.approved_states.indexOf(status) >= 0){
			color = "green";
		}
		else if(frappe.boot.tablix.rejected_states.indexOf(status) >= 0){
			color = "red";
		}
		else{
			color = "orange";
		}
		return color;
	},
	
	add_export_button: function(listview, fields){
		
		listview.page.add_menu_item(__("Export Selected"), function(){
			
			selected = listview.get_checked_items()
			if (selected.length == 0){
				frappe.msgprint(__("Please select <b>Items</b> to be export"));
				return false;
			}
			else{
				frappe.prompt({fieldtype:"Select", label: __("Select File Type"), fieldname:"file_format_type",
                        	options:"Excel\nCSV", default:"Excel", reqd: 1},
                        	function(data) {
					var view_data = [fields, selected];
					var result = view_data.map(row => row.splice(1));
					
					console.log(result);
					// to download only visible rows
					var visible_idx = view_data.map(row => row[0]).filter(sr_no => sr_no !== 'Sr No');

					if (data.file_format_type == "CSV") {
						frappe.tools.downloadify(result, null, listview.doctype);
					}

					else if (data.file_format_type == "Excel") {
						var args = {
							cmd: 'frappe.desk.query_report.export_query',
							report_name: listview.doctype,
							file_format_type: data.file_format_type,
							filters: {},
							visible_idx: visible_idx,
						}

						open_url_post(frappe.request.url, args);
					}
				}, __("Export Report: "+ me.title), __("Download"));
			}
		return false;
		});
	},
	set_intro: function(frm, doc, fieldname){

		if(frappe.boot.tablix.rejected_states.indexOf(frm.doc[fieldname]) >= 0){
			frm.set_intro(doc.reason|| "");
			console.log("Intro setup Successfully");
		}
	},
	add_fraction_value: function(value){
		
		if(!value  || value == 0.0){
			return value;
		}	
		flag = value -  Math.floor(value);
		
		if(flag > 0){
			value  = Math.floor(value) + 1;
		}
		return value;
		
	}
});


tablix.info.MoreInfo = Class.extend({
	
	init: function(args){
		
		$.extend(this, args);
		this.doctype = this.frm.doc.doctype;
		this.make();
	},

	make: function(){
		
		this.create_dialog();
	},
	
	flag: function(){

		return frappe.boot.tablix.states.indexOf(this.frm.doc.tablix_status)
			
	},
	validate: function(){

		return this.frm.doc.tablix_prev_status == this.frm.doc.tablix_status;
	},
	create_dialog: function(){
	
		var me = this;
		this.dialog = new  frappe.ui.Dialog({
			title: "Need More Information about " + me.frm.doc.name,
			fields:[
				{
					label: __("Reason for Rejection"), fieldname: "reason", fieldtype: "Small Text", reqd: 1
				},
			],
			primary_action_label: __("Submit"),
			primary_action: function(){

				me.send_email();			
			}
		
		});
		this.dialog.no_cancel();
		this.dialog.show();
	},

	send_email: function(){
		
		var me = this;
		var reason = this.get_reason();
		if(!reason){
			msg = format(__("Kindly enter reason for why are you rejecting {0} documnet", [me.frm.doc.name]))
			frappe.msgprint(msg);
			return
		}
		me.frm.set_value("reason", reason);
		//me.frm.timeline.insert_comment("Info", reason);
		me.save();
	},
	get_reason: function(){
		return this.dialog.get_value("reason");
	},
	
	save: function(){
		var me = this;
		
		frappe.workflow.get_transitions(me.frm.doc, me.get_state()).then(transitions =>
			$.each(transitions, function(i, d) {
				if(d.action == me.action){
					var next_state = d.next_state;
					var doc_before_action = copy_dict(me.frm.doc);
					var new_docstatus = cint(next_state.new_docstatus);

					var on_error = function() {
						// reset in locals
						frappe.model.add_to_locals(doc_before_action);
						me.frm.refresh();
					}
					// success - add a comment
					var success = function() {
						console.log("sahil is here");
						//me.frm.timeline.insert_comment("Workflow", next_state);
					}

					var new_state = frappe.workflow.get_document_state(me.frm.doctype, next_state);
					me.frm.doc[me.frm.state_fieldname] = next_state;

					if(new_state.update_field) {
						//me.frm.set_value(new_state.update_field, new_state.update_value);
						frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "tablix_status", new_state.update_value);
						me.frm.refresh_field("tablix_status");
						console.log(me.frm);
						me.frm.refresh();
					}

					if(new_docstatus==1 && me.frm.doc.docstatus==0) {
						me.frm.savesubmit(null, success, on_error);
					} else if(new_docstatus==0 && me.frm.doc.docstatus==0) {
						me.frm.save("Save", success, null, on_error);
					} else if(new_docstatus==1 && me.frm.doc.docstatus==1) {
						me.frm.save("Update", success, null, on_error);
					} else if(new_docstatus==2 && me.frm.doc.docstatus==1) {
						frappe.model.set_value(me.frm.doc.doctype, me.frm.doc.name, "tablix_status", "Cancel");
						me.frm.savecancel(null, success, on_error);
					} else {
						frappe.msgprint(__("Document Status transition from ") + me.frm.doc.docstatus + " "
							+ __("to") +
								new_docstatus + " " + __("is not allowed."));
						frappe.msgprint(__("Document Status transition from {0} to {1} is not allowed", [me.frm.doc.docstatus, new_docstatus]));
						return false;
					}
				}
			})
		);
		me.dialog.hide();
	},
	
	get_state: function() {
		if(!this.frm.doc[this.state_fieldname]) {
			this.set_default_state();
		}
		return this.frm.doc[this.state_fieldname];
	},

})
frappe.provide("tablix.workflow");
frappe.ui.form.States = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		this.state_fieldname = frappe.workflow.get_state_fieldname(this.frm.doctype);

		// no workflow?
		if(!this.state_fieldname)
			return;

		this.update_fields = frappe.workflow.get_update_fields(this.frm.doctype);

		var me = this;
		$(this.frm.wrapper).bind("render_complete", function() {
			me.refresh();
		});
	},

	setup_help: function() {
		var me = this;
		this.frm.page.add_action_item(__("Help"), function() {
			frappe.workflow.setup(me.frm.doctype);
			var state = me.get_state();
			var d = new frappe.ui.Dialog({
				title: "Workflow: "
					+ frappe.workflow.workflows[me.frm.doctype].name
			})
			var next_html = $.map(frappe.workflow.get_transitions(me.frm.doctype, state),
				function(d) {
					return d.action.bold() + __(" by Role ") + d.allowed;
				}).join(", ") || __("None: End of Workflow").bold();

			$(d.body).html("<p>"+__("Current status")+": " + state.bold() + "</p>"
				+ "<p>"+__("Document is only editable by users of role")+": "
					+ frappe.workflow.get_document_state(me.frm.doctype,
						state).allow_edit.bold() + "</p>"
				+ "<p>"+__("Next actions")+": "+ next_html +"</p>"
				+ (me.frm.doc.__islocal ? ("<div class='alert alert-info'>"
					+__("Workflow will start after saving.")+"</div>") : "")
				+ "<p class='help'>"+__("Note: Other permission rules may also apply")+"</p>"
				).css({padding: '15px'});
			d.show();
		}, true);
	},

	refresh: function() {
		// hide if its not yet saved
		if(this.frm.doc.__islocal) {
			this.set_default_state();
			return;
		}
		// state text
		var state = this.get_state();

		if(state) {
			// show actions from that state
			this.show_actions(state);
		}
		
	},

	show_actions: function(state) {
		var added = false,
			me = this;

		this.frm.page.clear_actions_menu();

		// if the loaded doc is dirty, don't show workflow buttons
		if (this.frm.doc.__unsaved===1) {
			return;
		}

		frappe.workflow.get_transitions(this.frm.doc, state).then(transitions => {
			$.each(transitions, function(i, d) {
				if(frappe.user_roles.includes(d.allowed)) {
					added = true;
					me.frm.page.add_action_item(__(d.action), function() {
						var action = d.action;
						// capture current state
						if(d.action  == "Reject"){
							me.frm.doc.__tran_state = d;
							me.more_info =  new tablix.info.MoreInfo({frm:me.frm, new_docstatus: new_docstatus, action:action, state_fieldname: me.state_fieldname});
						}
						else{

							var doc_before_action = copy_dict(me.frm.doc);
							// set new state
							var next_state = d.next_state;//frappe.workflow.get_next_state(me.frm.doctype,
									//me.frm.doc[me.state_fieldname], action);
							me.frm.doc[me.state_fieldname] = next_state;
							var new_state = frappe.workflow.get_document_state(me.frm.doctype, next_state);
							var new_docstatus = cint(new_state.doc_status);

							if(new_state.update_field) {
								console.log(new_state);
								me.frm.set_value(new_state.update_field, "");
								frappe.model.set_value(cur_frm.doc.doctype, cur_frm.doc.name, "tablix_status", new_state.update_value);
								cur_frm.refresh_field("tablix_status");
							}

							// revert state on error
							var on_error = function() {
								// reset in locals
								frappe.model.add_to_locals(doc_before_action);
								me.frm.refresh();
							}
							// success - add a comment
							var success = function() {
								console.log("sahil is here");//me.frm.timeline.insert_comment("Workflow", next_state);
							}

							me.frm.doc.__tran_state = d;

							if(new_docstatus==1 && me.frm.doc.docstatus==0) {
								me.frm.savesubmit(null, success, on_error);
							} else if(new_docstatus==0 && me.frm.doc.docstatus==0) {
								me.frm.save("Save", success, null, on_error);
							} else if(new_docstatus==1 && me.frm.doc.docstatus==1) {
								me.frm.save("Update", success, null, on_error);
							} else if(new_docstatus==2 && me.frm.doc.docstatus==1) {
								me.frm.savecancel(null, success, on_error);
							} else {
								frappe.msgprint(__("Document Status transition from ") + me.frm.doc.docstatus + " "
									+ __("to") +
									new_docstatus + " " + __("is not allowed."));
								frappe.msgprint(__("Document Status transition from {0} to {1} is not allowed", [me.frm.doc.docstatus, new_docstatus]));
								return false;
							}
						}
						return false;

					});
				}
			});
		});

		if(added) {
			this.frm.page.btn_primary.addClass("hide");
			this.frm.toolbar.current_status = "";
			this.setup_help();
		}
	},

	set_default_state: function() {
		var default_state = frappe.workflow.get_default_state(this.frm.doctype, this.frm.doc.docstatus);
		if(default_state) {
			this.frm.set_value(this.state_fieldname, default_state);
		}
	},

	get_state: function() {
		if(!this.frm.doc[this.state_fieldname]) {
			this.set_default_state();
		}
		return this.frm.doc[this.state_fieldname];
	},

	bind_action: function() {
		var me = this;
		this.dropdown.on("click", "[data-action]", function() {
		})
	},
	
});
