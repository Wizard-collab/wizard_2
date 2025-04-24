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

"""
This module provides functions to log various types of events in the asset tracking system.

Each function corresponds to a specific type of event, such as assignment, estimation, 
start date, state switch, priority switch, work session, or comment. These events are 
recorded using the `assets.add_asset_tracking_event` function, and some functions also 
interact with other modules like `repository` and `environment`.

Functions:
    - add_assignment_event: Logs an assignment event for a stage.
    - add_estimation_event: Logs an estimation event for a stage.
    - add_start_date_event: Logs a start date event for a stage.
    - add_state_switch_event: Logs a state switch event for a stage.
    - add_priority_switch_event: Logs a priority switch event for a stage.
    - add_work_session_event: Logs a work session event and updates user work time.
    - add_comment_event: Logs a comment event for a stage.

Dependencies:
    - `assets`: Used to log asset tracking events.
    - `repository`: Used to update user work time.
    - `environment`: Used to retrieve the current user.

Logging:
    - Uses the `logging` module to set up a logger for the module.
"""

# Python modules
import logging

# Wizard modules
from wizard.core import assets
from wizard.core import repository
from wizard.core import environment

logger = logging.getLogger(__name__)


def add_assignment_event(stage_id, assigned_user, comment=''):
    """
    Adds an assignment event to the asset tracking system.

    This function logs an event of type 'assignment' for a specific stage,
    associating it with a user and an optional comment.

    Args:
        stage_id (int): The ID of the stage where the event is being added.
        assigned_user (str): The user being assigned in the event.
        comment (str, optional): Additional information or remarks about the event. Defaults to an empty string.

    Returns:
        None
    """
    event_type = 'assignment'
    data = assigned_user
    assets.add_asset_tracking_event(stage_id, event_type, data, comment)


def add_estimation_event(stage_id, estimation_time, comment=''):
    """
    Records an estimation event for a specific stage.

    This function logs an event when an estimation time is set for a stage.

    Args:
        stage_id (int): The identifier of the stage for which the estimation is being set.
        estimation_time (int or str): The estimated time for the stage.
        comment (str, optional): An optional comment describing the estimation. Defaults to an empty string.

    Side Effects:
        - Adds an asset tracking event for the estimation.

    Dependencies:
        - `assets.add_asset_tracking_event`: Logs the asset tracking event.
    """
    event_type = 'estimation'
    data = str(estimation_time)
    assets.add_asset_tracking_event(stage_id, event_type, data, comment)


def add_start_date_event(stage_id, start_date, comment=''):
    """
    Records a start date event for a specific stage.

    This function logs an event when a start date is set for a stage.

    Args:
        stage_id (int): The identifier of the stage for which the start date is being set.
        start_date (str): The start date for the stage in string format.
        comment (str, optional): An optional comment describing the start date. Defaults to an empty string.

    Side Effects:
        - Adds an asset tracking event for the start date.

    Dependencies:
        - `assets.add_asset_tracking_event`: Logs the asset tracking event.
    """
    event_type = 'start_date'
    data = str(start_date)
    assets.add_asset_tracking_event(stage_id, event_type, data, comment)


def add_state_switch_event(stage_id, new_state, comment=''):
    """
    Records a state switch event for a specific stage.

    This function logs an event when the state of a stage is switched.

    Args:
        stage_id (int): The identifier of the stage whose state is being switched.
        new_state (str): The new state of the stage.
        comment (str, optional): An optional comment describing the state switch. Defaults to an empty string.

    Side Effects:
        - Adds an asset tracking event for the state switch.

    Dependencies:
        - `assets.add_asset_tracking_event`: Logs the asset tracking event.
    """
    event_type = 'state_switch'
    data = new_state
    assets.add_asset_tracking_event(stage_id, event_type, data, comment)


def add_priority_switch_event(stage_id, new_priority, comment=''):
    """
    Records a priority switch event for a specific stage.

    This function logs an event when the priority of a stage is switched.

    Args:
        stage_id (int): The identifier of the stage whose priority is being switched.
        new_priority (str): The new priority of the stage.
        comment (str, optional): An optional comment describing the priority switch. Defaults to an empty string.

    Side Effects:
        - Adds an asset tracking event for the priority switch.

    Dependencies:
        - `assets.add_asset_tracking_event`: Logs the asset tracking event.
    """
    event_type = 'priority_switch'
    data = new_priority
    assets.add_asset_tracking_event(stage_id, event_type, data, comment)


def add_work_session_event(stage_id, work_time, comment=''):
    """
    Records a work session event and updates the user's work time.

    Args:
        stage_id (int): The identifier of the stage where the work session occurred.
        work_time (int): The duration of the work session in minutes.
        comment (str, optional): An optional comment describing the work session. Defaults to an empty string.

    Behavior:
        - If the work_time exceeds 120 minutes, a 'work_session' event is logged with the provided stage_id, 
          work_time, and comment.
        - Independently of the work_time, the user's total work time is updated in the repository.

    Dependencies:
        - Calls `assets.add_asset_tracking_event` to log the work session event.
        - Calls `repository.add_user_work_time` to update the user's work time.
        - Uses `environment.get_user()` to retrieve the current user.

    """
    if work_time > 120:
        event_type = 'work_session'
        data = work_time
        assets.add_asset_tracking_event(stage_id, event_type, data, comment)
    repository.add_user_work_time(environment.get_user(), work_time)


def add_comment_event(stage_id, comment):
    """
    Adds a comment event to the asset tracking system.

    This function records a comment event for a specific stage in the asset
    tracking system. The event type is set to 'comment', and the provided
    comment is stored as the event data.

    Args:
        stage_id (int): The identifier of the stage where the comment event
                        should be added.
        comment (str): The comment text to be recorded as part of the event.

    Returns:
        None
    """
    event_type = 'comment'
    data = comment
    assets.add_asset_tracking_event(stage_id, event_type, data, comment)
