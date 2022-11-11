cur_frm.add_fetch("tablix_rep", "full_name", "tablix_rep_name");
cur_frm.add_fetch("bank_account", "account_num", "ac_details");
cur_frm.add_fetch("bank_account", "iban_no", "iban");
cur_frm.add_fetch("bank_account", "address", "address");
cur_frm.add_fetch("bank_account", "swift_code", "swift_code");
cur_frm.add_fetch("bank_account", "phone_1", "bank_phone1");
cur_frm.add_fetch("bank_account", "bank_name", "bank_name");
cur_frm.add_fetch("sales_order", "customer", "customer");
cur_frm.add_fetch("sales_order", "po_no", "customer_ref");
cur_frm.add_fetch("tablix_rep", "full_name", "tablix_rep_name");
cur_frm.add_fetch("tablix_rep", "phone", "tablix_rep_phone");
cur_frm.get_docfield("items").allow_bulk_edit = 1;

var Controller = tablix.taxes.extend_class(erpnext.accounts.SalesInvoiceController);
cur_frm.script_manager.make(Controller);
