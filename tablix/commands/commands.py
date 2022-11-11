
import os
import click
from frappe.commands import pass_context, get_site

@click.command("setup-metabase")
@click.option("--site", help="Name of Site")
@click.option("--minjvm", default="-Xms256", help="Mimimum Memory required to start JVM")
@click.option("--maxjvm", default="-Xmx512", help="Maximum Memory to be useb by JVM")
@pass_context
def setup_metabase(context, site, minjvm="-Xms256", maxjvm="-Xmx512"):
	
	try:
		print("sahil saini")
		pass
	except Exception as e:
		print ("sahil saini here")


