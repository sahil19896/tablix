frappe.pages['view-document'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'View Document',
		single_column: true
	});
	
	wrapper.view_document = new erpnext.ViewDocument(wrapper);
}

erpnext.ViewDocument = Class.extend({
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
		
		frappe.model.get_value("Employee", {"user_id": frappe.session.user_email}, "signature", function(r){
			if(r){
				if(r.signature){
					var dialog = new frappe.ui.Dialog({
						title: __('Are you sure you want to confirm this?'),
						fields: [
							{fieldtype:'Section Break', fieldname: 'section', label: __('<p style="text-align:center;"><b>Reviewed, Understood, Recorded</b></p>')},
							{fieldtype:'Check', fieldname:'read', reqd:1, label:'I reviewed the Policy.'},
							{fieldtype:'Check', fieldname:'understand', reqd:1, label:'I understand.'},
							{fieldtype:'Check', fieldname:'accept', reqd:1, label:'I accept.'},
						],
					});
				
					dialog.set_primary_action(__('Confirm'), function() {
						var user_data = dialog.get_values();
						var sign = ""
						if(!user_data.read || !user_data.accept || !user_data.understand){
							frappe.throw("Please read the Document carefully & accept to confirm.", title="Review Carefully.");
						} else{
							me.get_ans(sign);
						}
						dialog.hide();
					});

					dialog.show();
				} else{
					var dialog = new frappe.ui.Dialog({
						title: __('Are you sure you want to confirm this?'),
						fields: [
							{fieldtype:'Section Break', fieldname: 'section', label: __('<p style="text-align:center;"><b>Reviewed, Understood, Recorded</b></p>')},
							{fieldtype:'Check', fieldname:'read', reqd:1, label:'I reviewed the Policy.'},
							{fieldtype:'Check', fieldname:'understand', reqd:1, label:'I understand.'},
							{fieldtype:'Check', fieldname:'accept', reqd:1, label:'I accept.'},
							{fieldtype:'Column Break', fieldname:'column', reqd:1, label:''},
							{fieldtype:'Attach', fieldname:'sign', reqd:1, label:'Signature'},
						],
					});
					
					dialog.set_primary_action(__('Confirm'), function() {
						var user_data = dialog.get_values();
						var sign = user_data.sign;
						if(!user_data.read || !user_data.accept || !user_data.understand || !user_data.sign){
							frappe.throw("Please read the Document carefully & accept to confirm.", title="Review Carefully.");
						} else{
							me.get_ans(sign);
						}
						dialog.hide();
					});
					dialog.show();
				}
			}
		});
	},

	get_ans: function(sign){
		var me = this;
		var doc_name = frappe.route_options.name || "";
		if(doc_name){
			frappe.call({
				"method": "tablix.tablix_hr.page.view_document.view_document.check_data",
				"args": { "name": doc_name },
				"callback": function(r){
					if(r){
						var table = r.message;
						if(table){
							var user_input = $('input:radio:checked').map(function(j, el){return $(el).val();}).get();
							if(table.length == user_input.length){
								me.check_ans(user_input, table, sign);
							}else{
								frappe.msgprint("Kindly answer all the questions.");
							}
						} else{
							me.submit_accept(sign);					
						}
					}
				}
			});
		}
	},

	check_ans: function(user_input, table, sign){
		var me = this;
		var ans = [];
		for(i=0;i<table.length;i++){
			if(table[i][user_input[i]] == 1){
				ans.push(i);
			}
		}
		if(ans.length != table.length){
			frappe.msgprint("Some of your Answers are wrong. Please read document carefully and Submit again.", title="Review Carefully.");
		} else{
			me.submit_accept(sign);
		}
	},

	submit_accept: function(sign){
		var me = this;
		var user = frappe.session.user_email;
		var ref_no = frappe.route_options.name;
		
		if( user && ref_no){
			frappe.call({
				"method": "tablix.tablix_hr.page.view_document.view_document.check_accepted",
				"args": { "user": user, "ref_no": ref_no },
				"callback": function(r){
					if(r){	
						if(r.message.accept == 0){
							frappe.msgprint("Thanks for your review.", title="Reviewed");
							frappe.call({
								"method": "tablix.tablix_hr.page.view_document.view_document.submit_data",
								"args": { "user": user, "ref_no": ref_no, "sign": sign }
							});
						} else{
							frappe.msgprint("You Already view & accept this document.", title="Already Reviewed");
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
		var $container = $(frappe.render_template('view_document', data)).appendTo(this.body);

		me.render_weather();
		var doc_name = frappe.route_options.name || "";
		if(doc_name != ""){
			me.view_document(doc_name);
		} else{
			frappe.msgprint("Please follow the correct procedure. <b>GO TO Your Assign Policy and then Click on Read Complete Document.</b>")
		}
	},

	render_weather: function(){
		!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');
	},

	view_document: function(documentname){
		frappe.call({
			"method": "tablix.tablix_hr.page.view_document.view_document.get_data",
			"args": { "name": documentname },
			"callback": function(r){
				if(r && r.message){

					var data = r.message[0];
					var quiz = r.message[1];
	
					/* document data */
					if(data){
						$("#document_name").html(__(data.document_name));
						$("#document_type").html(__(data.document_type));
						$("#ref_no").html(__(documentname));
						$("#release_date").html(__(data.date));
		
						const html = `
							<table class="table table-bordered" style="background-color: #f9f9f9;">
								<tbody>
									<tr><td>${data.policy_description}</td> </tr>
								</tbody>
							</table>`
						$("#get_des").html(html);
					}

					/* Quiz */
					if(quiz){
						const quiz_html = `
							<table class="table table-bordered" style="background-color: #f9f9f9;">
								<thead>
									<tr><th>${__("#")}</th>
									<th>${__("Question")}</th>
									<th>${__("A")}</th>
									<th>${__("B")}</th>
									<th>${__("C")}</th>
									<th>${__("D")}</th></tr>
								</thead>
								<tbody>
									${quiz.map((l,p) => `<tr>
										<td>${p+1}</td>
										<td>${l.question}</td>

										<td><input type="radio" name=${p+1} value=${__("a")}>&nbsp ${l.choice_1}</td>

										<td><input type="radio" name=${p+1} value=${__("b")}>&nbsp ${l.choice_2}</td>
										<td><input type="radio" name=${p+1} value=${__("c")}>&nbsp ${l.choice_3}</td>
										<td><input type="radio" name=${p+1} value=${__("d")}>&nbsp ${l.choice_4}</td>					
					
									</tr>`).join('')}
								</tbody>
							</table>`
						$("#get_que").html(quiz_html);
						$("#quiz").html(__("QUIZ(Enter Choices)"));
					}
				}
			}
		});
	},

});
