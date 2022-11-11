from frappe import _

data = {
	'fieldname': 'boq',
	'internal_links': {
		'Opportunity': ['payment_term_table', 'opp_ref']
	},
	'transactions': [
		{
			'label': _('Related'),
			'items': ['Quotation', 'Sales Order']
		},
		{
			'label': _('Reference'),
			'items': ['Opportunity']
		},
		
	]
}