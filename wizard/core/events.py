# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

from wizard.core import environment
from wizard.core import project

def add_creation_event(instance_type, instance_id):
	data = (instance_type, instance_id)
	project_obj=project.project()
	if instance_type == 'category':
		category_row = project_obj.get_category_data(instance_id)
		domain_name = project_obj.get_domain_data(category_row['domain_id'], 'name')
		message = f"Created {domain_name}|{category_row['name']}"
	elif instance_type == 'asset':
		asset_row = project_obj.get_asset_data(instance_id)
		category_name = project_obj.get_category_data(asset_row['category_id'], 'name')
		message = f"Created {category_name}|{asset_row['name']}"
	elif instance_type == 'variant':
		variant_row = project_obj.get_variant_data(instance_id)
		stage_row = project_obj.get_stage_data(variant_row['stage_id'])
		asset_row = project_obj.get_asset_data(stage_row['asset_id'])
		category_name = project_obj.get_category_data(asset_row['category_id'], 'name')
		message = f"Created {category_name}|{asset_row['name']}|{stage_row['name']}|{variant_row['name']}"
	project_obj.add_event('creation', message, data)

def add_export_event(export_version_id, comment):
	data = export_version_id
	project_obj=project.project()
	export_version_row = project_obj.get_export_version_data(export_version_id)
	export_row = project_obj.get_export_data(export_version_row['export_id'])
	variant_row = project_obj.get_variant_data(export_row['variant_id'])
	stage_row = project_obj.get_stage_data(variant_row['stage_id'])
	asset_row = project_obj.get_asset_data(stage_row['asset_id'])
	category_name = project_obj.get_category_data(asset_row['category_id'], 'name')
	message = f"Exported {category_name}"
	message += f"|{asset_row['name']}"
	message += f"|{stage_row['name']}"
	message += f"|{variant_row['name']}"
	message += f"|{export_row['name']}"
	message += f"|{export_version_row['name']}"
	message += f"\n{comment}"
	project_obj.add_event('export', message, data)

def add_ticket_openned_event(ticket_id):
	data = ticket_id
	project_obj=project.project()
	ticket_row = project_obj.get_ticket_data(ticket_id)
	destination_user = ticket_row['destination_user']
	if destination_user is None:
		destination_user = 'everybody'
	message = f"Adressed a ticket to {destination_user}"
	message += f"\n{ticket_row['title']}"
	message += f"\n{ticket_row['message']}"
	project_obj.add_event('ticket_openned', message, data)

def add_ticket_closed_event(ticket_id):
	data = ticket_id
	project_obj=project.project()
	message = "Closed a ticket"
	project_obj.add_event('ticket_closed', message, data)
