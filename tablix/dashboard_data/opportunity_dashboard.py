from frappe import _

def get_data():
	return {
		'fieldname': 'prevdoc_docname',
		'non_standard_fieldnames': {
			'Supplier Quotation': 'opportunity',
			'Quotation': 'opportunity',
			'Boq': 'opportunity'
		},
		'internal_links':{
			#'Boq':["items", "opp_ref"],
			#'Quotation':["items", "opp_ref"]	
		},
		'transactions': [
			{
				"label": _("Selling"),
				"items": ["Quotation", "Supplier Quotation", "Sales Order", "Sales Invoice", "Develiry Note"]
			},
			{
				"label": _("Buying"),
				"items": ["Material Request", "Purchase Order", "Purchase Receipt", "Purchase Invoice"],
			},
			{
				"label": _("Design & Estimation"),
				'items': ['Boq']
			},
		]
	}
