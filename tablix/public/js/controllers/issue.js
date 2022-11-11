
frappe.provide("tablix.issue");

tablix.issue.Issue = tablix.manual_assign.ManualAssign.extend({

	init: function(args){
		$.extend(this, args);
		
	},
	refresh: function(frm){
		this.make_dialog();	
	},
	attended_datetime: function(){
		this.calculate_rectification_time();	
	},
	
	rectification_datetime: function(){
		this.calculate_rectification_time();
	},

	calculate_rectification_time: function(){
		if(!this.frm.doc.attended_datetime  || !this.frm.doc.rectification_datetime){
			frappe.msgprint(__("Please enter <b> Attended Datetime and Rectification Datetime</b>"));
			return false;
		}

		var diff = moment(this.frm.doc.rectification_datetime).diff(this.frm.doc.attended_datetime, "minutes");
		this.frm.doc.rectification_time  = diff/60.0;
		this.frm.refresh_field("rectification_time")

		if(this.frm.doc.opening_date && this.frm.doc.opening_time){
				
			var opening_datetime = cstr(this.frm.doc.opening_date) + " " + cstr(this.frm.doc.opening_time);
			var diff = moment(this.frm.doc.rectification_datetime).diff(opening_datetime, "minutes");
			this.frm.doc.time_duration_ = diff/60.0;
			this.frm.refresh_field("time_duration_");
		}
	},
});

cur_frm.script_manager.make(tablix.issue.Issue);
