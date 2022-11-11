frappe.pages['notification'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Notification',
		single_column: true
	});

	wrapper.view_document = new erpnext.Notification(wrapper);
}

erpnext.Notification = Class.extend({
	init: function(wrapper) {
		var me = this;
		this.parent = wrapper;
		this.page = this.parent.page;
		setTimeout(function() {
			me.setup(wrapper);
			me.make(wrapper);
		}, 0);
	},

	setup: function(wrapper) {
		var me = this;
		this.elements = {
			layout: $(wrapper).find(".layout-main"),

			approve_btn: wrapper.page.set_primary_action(__("<b>Confirm</b>"),
			function() {
				me.accept_confirm();
			}, "fa fa-refresh"),

			refresh_btn: wrapper.page.set_secondary_action(__("<b>Refersh</b>"),
			function() { me.view_document(frappe.route_options.name); }, "fa fa-refresh"),
		};
	},

	accept_confirm: function(){
		var me = this;
		
		var dialog = new frappe.ui.Dialog({
			title: __('Are you sure you want to confirm this?'),
			fields:[
				{fieldtype:'Section Break', fieldname: 'section', label: __('<p style="text-align:center;"><b>Reviewed, Understood, Recorded</b></p>')},
				{fieldtype:'Check', fieldname:'read', reqd:1, label:'I reviewed the Notification.'},
				{fieldtype:'Check', fieldname:'understand', reqd:1, label:'I understand.'},
			],
		});

		dialog.set_primary_action(__('Confirm'), function() {
			var user_data = dialog.get_values();
			var signature = ""
			if(!user_data.read || !user_data.understand){
				frappe.throw("Please read the Notification carefully & accept to confirm.", title="Review Carefully.");
			} else{
				me.submit_accept(signature);
			}
			dialog.hide();
		});
		dialog.show();
	},

	submit_accept: function(signature){
		var me = this;
		var user = frappe.session.user_email;
		var ref_no = frappe.route_options.name;
		
		if( user && ref_no){
			frappe.call({
				"method": "tablix.tablix_hr.page.notification.notification.check_accepted",
				"args": { "user": user, "ref_no": ref_no },
				"callback": function(r){
					if(r){	
						if(r.message.accept == 0){
							frappe.msgprint("Thanks for your review.", title="Reviewed");
							frappe.call({
								"method": "tablix.tablix_hr.page.notification.notification.submit_data",
								"args": { "user": user, "ref_no": ref_no, "sign": signature }
							});
						} else{
							frappe.msgprint("You Already view this document Notification.", title="Already Reviewed");
						}
					}
				}
			});
		} else{
			frappe.throw("System is facing some problems. Kindly contact to your System Admin.");
		}
		
	},
	
	make: function(wrapper){
		var me = this;
		this.body = $('<div></div>').appendTo(this.page.main);
		var data = "";
		var $container = $(frappe.render_template('notification', data)).appendTo(this.body);

		var doc_name = frappe.route_options.name || "";
		if(doc_name){
			me.view_document(doc_name);
		} else{
			frappe.msgprint("Please follow the correct procedure. <b>GO TO Your Assign Notification and then Click on View Notification.</b>")
		}
	},

	view_document: function(documentname){
		console.log(documentname);
		frappe.call({
			"method": "tablix.tablix_hr.page.notification.notification.get_data",
			"args": { "name": documentname },
			"callback": function(r){
				if(r && r.message){

					var data = r.message[0];
					console.log(data);	
					/* document data */
					if(data){
						$("#subject").html(__(data.subject));
						$("#ref_no").html(__(documentname));
						$("#release_date").html(__(data.date));
		
						const html = `
							<table class="table table-bordered" style="background-color: #f9f9f9;">
								<tbody>
									<tr><td>${data.description}</td></tr>
								</tbody>
							</table>`
						$("#get_des").html(html);
					}
				}
			}
		});
	},
});
