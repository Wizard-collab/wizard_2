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
from wizard.core import assets

def add_creation_event(instance_type, instance_id):
	data = (instance_type, instance_id)
	title = "Creation event"
	message = assets.instance_to_string((instance_type, instance_id))
	project.add_event('creation', title, message, data)

def add_export_event(export_version_id):
	title = "Export event"
	data = export_version_id
	export_version_row = project.get_export_version_data(export_version_id)
	message = assets.instance_to_string(('export_version', export_version_id))
	project.add_event('export', title, message, data, export_version_row['comment'])

def add_archive_event(message, archive_path, additional_message):
	title = 'Archive event'
	data = archive_path
	project.add_event('archive', title, message, additional_message, data)

def add_ticket_openned_event(ticket_id, ticket_message):
	data = ticket_id
	ticket_row = project.get_ticket_data(ticket_id)
	export_version_id = ticket_row['export_version_id']
	string_instance = assets.instance_to_string(('export_version', export_version_id))
	destination_user = ticket_row['destination_user']
	if destination_user is None:
		destination_user = 'everybody'
	title = f"Adressed a ticket to {destination_user}"
	additional_message = f"{ticket_row['title']}:\n{ticket_message}"
	project.add_event('ticket_openned', title, string_instance, data, additional_message)

def add_ticket_closed_event(ticket_id):
	title = f"Closed a ticket"
	data = ticket_id
	ticket_row = project.get_ticket_data(ticket_id)
	export_version_id = ticket_row['export_version_id']
	string_instance = assets.instance_to_string(('export_version', export_version_id))
	project.add_event('ticket_closed', title, string_instance, data, ticket_row['title'])
