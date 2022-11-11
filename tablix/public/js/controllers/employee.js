frappe.ui.form.on("Employee", "refresh", function(frm){
	console.log("here");
	var emails = ["sahil.saini@tablix.ae","binu.c@tablix.ae","manoj@tablix.ae","ansarali@tablix.ae", "dileep.kumar@tablix.ae", "raj.kiran@tablix.ae", "bhavish@tablix.ae", "execsec@tablix.ae"];
	if(!emails.includes(frappe.session.user_email)){
		window.history.back();
	}
});
