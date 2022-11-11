
frappe.provide("tablix.duplicate");

tablix.duplicate.DuplicateRow = Class.extend({

	init: function(args){
		$.extend(this, args);
		var me = this;
		this.grid.df.on_setup = function(grid){
			me.setup(grid);
		};
	},
	setup: function(grid){
		this.grid_btn_group = this.grid.$wrapper.find(".grid-buttons");
		this.duplicate_row_button = $("<button class='btn btn-xs btn-success'>Duplicate Row </button>");
		this.duplicate_row_button.appendTo(".grid-buttons");
		this.add_duplicate_row(grid);
	},
	add_duplicate_row: function(grid){
		var me = this;
		this.duplicate_row_button.on("click", function(event){
	
				if(me.grid.grid.get_selected_children().length == 0){
					frappe.msgprint(__("Please <b>Select Items</b>"));
					return;
				}
				me.grid.grid.get_selected_children().forEach(row => {
					me._add_row(row, grid);
				});
		});
			
	},

	_add_row: function(row, grid){
		console.log(grid);
		var index  = this.frm.doc[grid.df.fieldname].length;
		index += 1;	
		var doc = frappe.model.get_new_doc(grid.options, this.frm);
		$.extend(doc, row);
		doc.idx = index;
		this.frm.add_child(grid.df.fieldname, doc);
		this.frm.refresh_field(grid.df.fieldname);
	}

})
