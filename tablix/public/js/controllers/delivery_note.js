cur_frm.add_fetch("tablix_rep", "full_name", "tablix_rep_name");
cur_frm.add_fetch("tablix_rep", "phone", "tablix_rep_phone");
cur_frm.add_fetch("sales_order_no", "po_no_new", "po_no");
cur_frm.add_fetch("sales_order_no", "po_date", "po_date");
cur_frm.add_fetch("sales_order_no", "po_no_new", "ship_via");
cur_frm.add_fetch("sales_order_no", "shipping_address_name", "shipping_address_name");
cur_frm.add_fetch("sales_order_no", "shipping_address", "shipping_address");
cur_frm.add_fetch("sales_order_no", "territory", "territory");
cur_frm.add_fetch("sales_order_no", "customer_address", "customer_address");
cur_frm.add_fetch("sales_order_no", "address_display", "address_display");
cur_frm.add_fetch("sales_order_no", "contact_person", "contact_person");
cur_frm.add_fetch("sales_order_no", "contact_display", "contact_display");
cur_frm.add_fetch("sales_order_no", "contact_mobile", "contact_mobile");
cur_frm.add_fetch("sales_order_no", "customer", "customer");

var Controller = tablix.taxes.extend_class(erpnext.stock.DeliveryNoteController);
cur_frm.script_manager.make(Controller);
