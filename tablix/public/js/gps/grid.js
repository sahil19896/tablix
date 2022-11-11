
frappe.provide("tablix.gps");

tablix.gps.Grid =  Class.extend({

	init: function(args){
		
		$.extend(this, args);
		this.make()
	},
	make: function(){
		this.config();
	},
	
	config: function(){

		var me= this;
		var args = {
			fields: me.fields,
			data: me.data,

			autoload: false,
			controller: {
				loadData: $.noop,
				insertItem: $.noop,
				updateItem: $.noop,
				deleteItem: $.noop
			},
			width: "auto",
			height: "auto",

			heading: true,
			filtering: false,
			inserting: false,
			editing: false,
			selecting: true,
			sorting: false,
			paging: false,
			pageLoading: false,

			rowClass: function(item, itemIndex) {  },
			rowClick: function(args) {  },
			rowDoubleClick: function(args) {  },

			noDataContent: "Not found",

			confirmDeleting: true,
			deleteConfirm: "Are you sure?",

			pagerContainer: null,
			pageIndex: 1,
			pageSize: 20,
			pageButtonCount: 15,
			pagerFormat: "Pages: {first} {prev} {pages} {next} {last}    {pageIndex} of {pageCount}",
			pagePrevText: "Prev",
			pageNextText: "Next",
			pageFirstText: "First",
			pageLastText: "Last",
			pageNavigatorNextText: "...",
			pageNavigatorPrevText: "...",

			invalidNotify: function(args) {  },
			invalidMessage: "Invalid data entered!",

			loadIndication: true,
			loadIndicationDelay: 500,
			loadMessage: "Please, wait...",
			loadShading: true,

			updateOnResize: true,

			rowRenderer: null,
			headerRowRenderer: null,
			filterRowRenderer: null,
			insertRowRenderer: null,
			editRowRenderer: null
		}
	
		this.grid = $(me.cls_name).jsGrid(args);
	},

});


tablix.gps.LoadTask = Class.extend({
	
	init: function(args){

		$.extend(this, args);
		this.args = args;
		this._super();
	},
	
	make: function(args){
	
		this._super();
	},
	
	get_data: function(){

				
		
	}
});
