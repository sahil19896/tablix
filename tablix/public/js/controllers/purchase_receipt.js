cur_frm.add_fetch("purchase_order", "customer_po", "sales_order");


var Controller = tablix.taxes.extend_class(erpnext.stock.PurchaseReceiptController);
cur_frm.script_manager.make(Controller);

