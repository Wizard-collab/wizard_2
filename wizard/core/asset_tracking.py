# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module manages the asset events
# the events are stored in the project database
# and are accessed by the 'project' module but
# this module decode what is stored in the
# asset tracking event rows

# Wizard modules
from wizard.core import project
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

def add_assignment_event(variant_id, assigned_user, comment=''):
	event_type = 'assignment'
	data = assigned_user
	project.add_asset_tracking_event(variant_id, event_type, data, comment)

def add_estimation_event(variant_id, estimation_time, comment=''):
	event_type = 'estimation'
	data = str(estimation_time)
	project.add_asset_tracking_event(variant_id, event_type, data, comment)

def add_state_switch_event(variant_id, new_state, comment=''):
	event_type = 'state_switch'
	data = new_state
	project.add_asset_tracking_event(variant_id, event_type, data, comment)

def add_work_session_event(variant_id, work_time, comment=''):
	event_type = 'work_session'
	data = work_time
	project.add_asset_tracking_event(variant_id, event_type, data, comment)

def add_comment_event(variant_id, comment):
	event_type = 'comment'
	data = comment
	project.add_asset_tracking_event(variant_id, event_type, data)
