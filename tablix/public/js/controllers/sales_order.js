cur_frm.get_docfield("items").allow_bulk_edit = 1;
//cur_frm.add_fetch("payment_term", "payment_term_description", "payment_term_description");

var Controller = tablix.taxes.extend_class(erpnext.selling.SalesOrderController);
cur_frm.script_manager.make(Controller);
