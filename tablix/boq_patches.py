
from frappe import _, msgprint, throw
from frappe.utils import cint, cstr, flt



class BOQPatch(object):
	
	def __init__(self, boq):
		self.boq  = boq



	def is_amc(self):

		return True if self.boq.is_amc else False



	def get_years_of_maintenance(self):
		
		year_of_maintenance = 1
		if(self.boq.one_year):
			year_of_maintenance = 1
		elif(self.boq.two_year):
			year_of_maintenance = 2
		elif (self.boq.three_year):
			year_of_maintenance = 3

		return year_of_maintenance


	def update_boq_amc_yearly(self):
		

		if not self.is_amc():
			return

		maintenance_years = self.get_years_of_maintenance()

		print(maintenance_years)

		


	def get_first_year_mainteance_charges(self, year):
		pass


	def get_second_year_maintenance_charges(self):
		pass


	def get_third_year_maintenance_charges(self):
		pass


	def get_fourth_year_maintenance_charges(self):
		pass

	def get_fifth_year_maintenance_charges(self):
		pass

				
