# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module manages the project events
# the events are stored in the project database
# and are accessed by the 'project' module but
# this module decode what is stored in the
# event rows

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

from wizard.core import environment
from wizard.core import project

def add_creation_event(instance_type, instance_id):
	data = (instance_type, instance_id)
	title = "Creation event"
	if instance_type == 'category':
		category_row = project.get_category_data(instance_id)
		domain_name = project.get_domain_data(category_row['domain_id'], 'name')
		message = f"Created {domain_name} | {category_row['name']}"
	elif instance_type == 'asset':
		asset_row = project.get_asset_data(instance_id)
		category_name = project.get_category_data(asset_row['category_id'], 'name')
		message = f"Created {category_name} | {asset_row['name']}"
	elif instance_type == 'variant':
		variant_row = project.get_variant_data(instance_id)
		stage_row = project.get_stage_data(variant_row['stage_id'])
		asset_row = project.get_asset_data(stage_row['asset_id'])
		category_name = project.get_category_data(asset_row['category_id'], 'name')
		message = f"Created {category_name} | {asset_row['name']} | {stage_row['name']} | {variant_row['name']}"
	project.add_event('creation', title, message, data)

def add_export_event(export_version_id):
	title = "Export event"
	data = export_version_id
	export_version_row = project.get_export_version_data(export_version_id)
	export_row = project.get_export_data(export_version_row['export_id'])
	variant_row = project.get_variant_data(export_row['variant_id'])
	stage_row = project.get_stage_data(variant_row['stage_id'])
	asset_row = project.get_asset_data(stage_row['asset_id'])
	category_name = project.get_category_data(asset_row['category_id'], 'name')
	message = f"Exported {category_name}"
	message += f" | {asset_row['name']}"
	message += f" | {stage_row['name']}"
	message += f" | {variant_row['name']}"
	message += f" | {export_row['name']}"
	message += f" | {export_version_row['name']}"
	project.add_event('export', title, message, data)

def add_archive_event(message, archive_path):
	title = 'Archive event'
	data = archive_path
	project.add_event('archive', title, message, data)

def add_ticket_openned_event(ticket_id):
	data = ticket_id
	ticket_row = project.get_ticket_data(ticket_id)
	destination_user = ticket_row['destination_user']
	if destination_user is None:
		destination_user = 'everybody'
	title = f"Adressed a ticket to {destination_user}"
	message = f"{ticket_row['title']}"
	message += f"\n{ticket_row['message']}"
	project.add_event('ticket_openned', title, message, data)

def add_ticket_closed_event(ticket_id):
	title = f"Closed a ticket"
	data = ticket_id
	message = "Closed a ticket"
	project.add_event('ticket_closed', title, message, data)
