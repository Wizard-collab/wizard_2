# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This module manages the asset events
# the events are stored in the project database
# and are accessed by the 'project' module but
# this module decode what is stored in the
# asset tracking event rows

# Python modules
import logging

# Wizard modules
from wizard.core import project
logger = logging.getLogger(__name__)

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
	if work_time > 120:
		event_type = 'work_session'
		data = work_time
		project.add_asset_tracking_event(variant_id, event_type, data, comment)

def add_comment_event(variant_id, comment):
	event_type = 'comment'
	data = comment
	project.add_asset_tracking_event(variant_id, event_type, data, comment)
