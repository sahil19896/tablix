from frappe import _
import frappe

def get_data():
	return {
		'fieldname': 'prevdoc_docname',
		'non_standard_fieldnames': {
			'Subscription': 'reference_document'
		},
		'internal_links': {
			'Boq': ['items', 'boq_ref'],
			'Opportunity': ['items', 'opp_ref']
		},
		'transactions': [
			{
				'label': _('Related'),
				'items': ['Sales Order', 'Subscription']
			},
			
			{
				'label': _('References'),
				'items': ['Boq', 'Opportunity']
			},
		]
	}
