
tablix.dashboard.AccountDashboard = tablix.dashboard.Dashboard.extend({


	init: function(args){
		this._super(args);
	},
	make: function(args){
		this._super(args);
	},
	handle_response: function(res){
		console.log(res);
	}
});
