/*
	Developer Sahil Saini
	Email sahil.saini@tablix.ae

*/
frappe.provide("tablix.gps");

/*
	Initialize filters
*/
tablix.gps.Filters = Class.extend({

	init: function(args){
		$.extend(this, args);
		this.fields_dict = {};
		this.make();
	},
	
	make: function(){
		this.init_filters();
	},

	init_filters: function(){
		this.fields = []
		this.filters = this.filters?this.filters:[];
		var me = this;
		$.each(me.filters, function(idx, val){
			cls_name = format(".{0}", [val.cls_name]);
			field = new frappe.ui.form.make_control({
					df:{
						fieldname:val.fieldname,
						fieldtype: val.fieldtype,
						default: val.default,
						options: val.options?val.options:null,
						placeholder: val.placeholder
					},
					parent: $.find(cls_name),
					only_input: true
			});
			field.make_input();
			me.fields.push(field);
			if(me.filters.length-1 == idx)
				me.update_link_field();
			me.fields_dict[field.df.fieldname] = field;
		});
		
	
	},
	get_values: function(){

		values = {};
		for(var i=0; i<this.fields.length; i++){
			temp = this.fields[i];
			values[temp.df.fieldname] =  temp.$input.val();
		}
		return values;
	},
	update_link_field: function(){

		$(".link-field").removeAttr("style");
	},
	validate_mandatory: function(){
		var messages = "";
		for(var i=0; i<this.fields.length; i++){
			temp  = this.fields[0]
	
			if(temp.df.reqd==1 && (!temp.$input.val() ||  temp.$input.val() == "")){
				 msg = format(" {0} ", [temp.df.label || temp.df.fieldname])
				messages += msg;
			}
			
		
		}
		this.reqd = false;
		if(messages != ""){
			this.reqd = true;
			msg = format("Please enter mandatory fields {0} ", [msg]);
			frappe.msgprint(__(msg));
			return false;
		}
		return true;
	},
	get_field: function(fieldname){

		if(this.fields_dict.hasOwnProperty(fieldname))
			return this.fields_dict[fieldname];
		return false;
	}
});
