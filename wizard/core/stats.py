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
This module provides functionality for calculating and managing progress statistics 
for assets, categories, and domains in a project. It includes methods for retrieving 
progress data, updating progress events, and calculating weighted means. Additionally, 
it provides a thread-based scheduler for automating progress updates at a specific time.

Key Features:
- Calculate progress for assets, categories, and domains based on stages.
- Update progress events when stages are added or removed.
- Calculate weighted means for progress values.
- Retrieve total and rendered frames for sequence assets.
- Schedule daily progress updates using a thread-based scheduler.

Dependencies:
- Python modules: time, threading, json, logging
- Wizard modules: assets_vars, project, tools
"""

# Python modules
import time
import threading
import json
import logging

# Wizard modules
from wizard.vars import assets_vars
from wizard.core import project
from wizard.core import tools

logger = logging.getLogger(__name__)


def get_all_progresses(to_round=1):
    """
    Calculate the progress of assets, categories, and domains based on stages.

    Args:
        to_round (int): Number of decimal places to round the progress values.

    Returns:
        tuple: A tuple containing dictionaries for assets, categories, and domains progresses.
    """

    # Retrieve all stages and calculate the total number of frames
    stages_rows = project.get_all_stages()
    all_frames = get_all_frames()

    # Initialize dictionaries to store progress lists and final progress values
    assets_progresses_lists = dict()
    assets_progresses = dict()
    categories_progresses_lists = dict()
    categories_progresses = dict()
    domains_progresses_lists = dict()
    domains_progresses = dict()

    # Iterate through each stage to calculate progress for assets, categories, and domains
    for stage_row in stages_rows:
        asset_id = stage_row['asset_id']

        # Initialize progress list for the asset if not already present
        if asset_id not in assets_progresses_lists.keys():
            assets_progresses_lists[asset_id] = []

        # Retrieve asset data and calculate the number of frames
        asset_row = project.get_asset_data(asset_id)
        frames_number = asset_row['outframe'] - asset_row['inframe']

        # Add the stage progress to the asset's progress list
        assets_progresses_lists[asset_id].append((stage_row['progress'], 1))

        # Retrieve domain data for the stage
        domain_row = project.get_domain_data(stage_row['domain_id'])

        # Initialize progress list for the category if not already present
        if asset_row['category_id'] not in categories_progresses_lists.keys():
            categories_progresses_lists[asset_row['category_id']] = []

        # Add the stage progress to the category's progress list, weighted by frames if sequence
        if domain_row['name'] == assets_vars._sequences_:
            categories_progresses_lists[asset_row['category_id']].append(
                (stage_row['progress'], frames_number / all_frames))
        else:
            categories_progresses_lists[asset_row['category_id']].append(
                (stage_row['progress'], 1))

        # Initialize progress list for the domain if not already present
        if domain_row['id'] not in domains_progresses_lists.keys():
            domains_progresses_lists[domain_row['id']] = []

        # Add the stage progress to the domain's progress list, weighted by frames if sequence
        if domain_row['name'] == assets_vars._sequences_:
            domains_progresses_lists[domain_row['id']].append(
                (stage_row['progress'], frames_number / all_frames))
        else:
            domains_progresses_lists[domain_row['id']].append(
                (stage_row['progress'], 1))

    # Calculate the mean progress for each asset and round it
    for asset_id in assets_progresses_lists.keys():
        assets_progresses[asset_id] = round(
            get_mean(assets_progresses_lists[asset_id]), to_round)

    # Calculate the mean progress for each category and round it
    for category_id in categories_progresses_lists.keys():
        categories_progresses[category_id] = round(
            get_mean(categories_progresses_lists[category_id]), to_round)

    # Calculate the mean progress for each domain and round it
    for domain_id in domains_progresses_lists.keys():
        domains_progresses[domain_id] = round(
            get_mean(domains_progresses_lists[domain_id]), to_round)

    # Return the calculated progresses for assets, categories, and domains
    return assets_progresses, categories_progresses, domains_progresses


def add_progress_event(new_stage=None, removed_stage=None):
    """
    Update progress events based on the addition or removal of stages.

    Args:
        new_stage (int, optional): ID of the newly added stage.
        removed_stage (int, optional): ID of the removed stage.
    """
    start_time = time.time()

    # Calculate the total number of frames in the project
    all_frames = get_all_frames()

    # Handle the addition of a new stage
    if new_stage:
        # Retrieve data for the new stage
        new_stage_row = project.get_stage_data(new_stage)
        stage_name = new_stage_row['name']
        all_stages = project.get_all_stages('name')
        total_len = len(all_stages)
        stage_len = all_stages.count(stage_name)
        all_assets = project.get_all_assets()
        assets = {asset_row['id']: asset_row for asset_row in all_assets}

        # Retrieve all progress events and update them based on the new stage
        progress_rows = project.get_all_progress_events()
        datas_to_update = []
        for progress_row in progress_rows:
            datas_dic = json.loads(progress_row['datas_dic'])
            original_datas_dic = datas_dic.copy()

            if stage_name not in datas_dic:
                continue
            # Update progress for asset stages
            if stage_name in assets_vars._assets_stages_list_:
                datas_dic[stage_name] *= (stage_len - 1) / stage_len
                if 'total' in datas_dic:
                    datas_dic['total'] *= (total_len - 1) / total_len

            # Update progress for sequence stages
            elif stage_name in assets_vars._sequences_stages_list_:
                print(datas_dic)

                asset_row = assets[new_stage_row['asset_id']]
                frames_number = asset_row['outframe'] - asset_row['inframe']
                datas_dic[stage_name] *= (all_frames -
                                          frames_number) / all_frames
                if 'total' in datas_dic:
                    datas_dic['total'] *= (all_frames -
                                           frames_number) / all_frames

            # Skip if no changes were made
            if datas_dic == original_datas_dic:
                continue

            # Add updated data to the list
            datas_to_update.append(
                (progress_row['id'], 'datas_dic', json.dumps(datas_dic)))

        # Update progress events in the project
        project.update_progress_events(datas_to_update)

    # Handle the removal of a stage
    if removed_stage:
        all_stages = project.get_all_stages('name')
        total_len = len(all_stages)
        stage_len = all_stages.count(new_stage)

        # Update progress events based on the removed stage
        progress_rows = project.get_all_progress_events()
        for progress_row in progress_rows:
            datas_dic = json.loads(progress_row['datas_dic'])
            if new_stage not in datas_dic:
                continue
            datas_dic[new_stage] *= (stage_len + 1) / stage_len
            if 'total' in datas_dic:
                datas_dic['total'] *= (total_len + 1) / total_len
            if datas_dic == json.loads(progress_row['datas_dic']):
                continue
            project.update_progress_event(
                progress_row['id'], ('datas_dic', json.dumps(datas_dic)))

    # Retrieve domain and category data
    domains_rows = project.get_domains()
    domains = {domain_row['id']: domain_row['name']
               for domain_row in domains_rows}

    categories_rows = project.get_all_categories()
    categories = {category_row['id']: category_row['name']
                  for category_row in categories_rows}

    # Map assets to their categories
    assets_rows = project.get_all_assets()
    assets_categories = {
        asset_row['id']: categories[asset_row['category_id']] for asset_row in assets_rows}

    # Retrieve all stages
    stages_rows = project.get_all_stages()

    # Initialize dictionaries to store progress data
    total_progresses_dic = dict()
    domains_progresses_dic = dict()
    categories_progresses_dic = dict()

    # Calculate progress for each stage, category, and domain
    for stage_row in stages_rows:
        stage = stage_row['name']
        category = assets_categories[stage_row['asset_id']]
        domain = domains[stage_row['domain_id']]

        # Skip library and omt stages
        if domain == assets_vars._library_ or stage_row['state'] == 'omt':
            continue

        # Calculate weighted progress for sequence stages
        if domain == assets_vars._sequences_:
            asset_row = project.get_asset_data(stage_row['asset_id'])
            frames_number = asset_row['outframe'] - asset_row['inframe']
            progress = (stage_row['progress'], frames_number / all_frames)
        else:
            progress = (stage_row['progress'], 1)

        # Update total progress
        total_progresses_dic.setdefault('total', []).append(progress)
        total_progresses_dic.setdefault(stage, []).append(progress)

        # Update category progress
        categories_progresses_dic.setdefault(
            category, {}).setdefault('total', []).append(progress)
        categories_progresses_dic[category].setdefault(
            stage, []).append(progress)

        # Update domain progress
        domains_progresses_dic.setdefault(
            domain, {}).setdefault('total', []).append(progress)
        domains_progresses_dic[domain].setdefault(stage, []).append(progress)

    # Ensure all stages are present in the progress dictionaries
    for domain_row in domains_rows:
        if domain_row['name'] == 'library':
            continue
        domains_progresses_dic.setdefault(
            domain_row['name'], {}).setdefault('total', [])
        for stage in assets_vars._stages_list_[domain_row['name']]:
            domains_progresses_dic[domain_row['name']].setdefault(stage, [])

    for category_row in categories_rows:
        domain = domains[category_row['domain_id']]
        if domain == 'library':
            continue
        categories_progresses_dic.setdefault(
            category_row['name'], {}).setdefault('total', [])
        for stage in assets_vars._stages_list_[domain]:
            categories_progresses_dic[category_row['name']].setdefault(
                stage, [])

    total_progresses_dic.setdefault('total', [])
    for stage in (assets_vars._assets_stages_list_ + assets_vars._sequences_stages_list_):
        total_progresses_dic.setdefault(stage, [])

    # Calculate mean progress for each stage, category, and domain
    for stage in total_progresses_dic.keys():
        total_progresses_dic[stage] = get_mean(total_progresses_dic[stage])
    project.add_progress_event(
        'total', 'All project', json.dumps(total_progresses_dic))

    for domain in domains_progresses_dic.keys():
        for stage in domains_progresses_dic[domain].keys():
            domains_progresses_dic[domain][stage] = get_mean(
                domains_progresses_dic[domain][stage])
        project.add_progress_event(
            'domain', domain, json.dumps(domains_progresses_dic[domain]))

    for category in categories_progresses_dic.keys():
        for stage in categories_progresses_dic[category].keys():
            categories_progresses_dic[category][stage] = get_mean(
                categories_progresses_dic[category][stage])
        project.add_progress_event('category', category, json.dumps(
            categories_progresses_dic[category]))

    # Log the duration of the progress event calculation
    logger.debug(
        f"Progress event calculation duration : {time.time() - start_time}s")


def get_mean(data_list):
    """
    Calculate the weighted mean of a list of (value, weight) tuples.
    Args:
        data_list (list of tuple): A list where each element is a tuple containing
                                   a value and its corresponding weight. For example,
                                   [(value1, weight1), (value2, weight2), ...].
                                   If the list is empty, it defaults to [(0, 1)].
    Returns:
        float: The weighted mean calculated as the sum of (value * weight) divided
               by the sum of weights.
    Raises:
        ZeroDivisionError: If the total weight is zero, which would result in a
                           division by zero.
    """
    if data_list == []:
        data_list = [(0, 1)]
    weighted_sum = sum(value * weight for value, weight in data_list)
    total_weight = sum(weight for _, weight in data_list)

    return weighted_sum / total_weight


def get_all_frames():
    """
    Calculate the total number of frames across all sequence assets in the project.

    This function retrieves all sequence assets from the project and computes the 
    total number of frames by summing the difference between the 'outframe' and 
    'inframe' for each asset.

    Returns:
        int: The total number of frames across all sequence assets.
    """
    assets_rows = project.get_all_sequence_assets()
    all_frames = 0
    for asset_row in assets_rows:
        all_frames += asset_row['outframe'] - asset_row['inframe']
    return all_frames


def get_rendered_frames():
    """
    Calculate the total number of frames that have been rendered across all sequence assets.
    This function retrieves all sequence assets from the project, checks if their 
    associated rendering stage is marked as 'done', and sums up the frame range 
    (outframe - inframe) for those assets.
    Returns:
        int: The total number of rendered frames.
    """
    assets_rows = project.get_all_sequence_assets()
    done_frames = 0
    for asset_row in assets_rows:

        # Get rendering stage
        stage = project.get_asset_child_by_name(
            asset_row['id'], 'rendering', ignore_warning=True)
        if not stage:
            continue
        if stage['state'] != 'done':
            continue

        done_frames += asset_row['outframe'] - asset_row['inframe']
    return done_frames


class schedule(threading.Thread):
    """
    A thread-based scheduler that performs a specific action at a designated time each day.
    Attributes:
        day (str): The current day, updated based on the system time.
        is_done (bool): A flag indicating whether the scheduled action has been performed for the day.
        running (bool): A flag to control the execution of the thread.
    Methods:
        __init__(parent=None):
            Initializes the scheduler thread with default values.
        stop():
            Stops the scheduler by setting the running flag to False.
        run():
            Continuously checks the current time and performs the scheduled action
            at the specified hour and minute if it hasn't been done for the day.
    """

    def __init__(self, parent=None):
        """
        Initializes the schedule object.

        Args:
            parent (optional): The parent object, default is None.

        Attributes:
            day (int): The current day obtained from the converted time.
            hour (int): The current hour obtained from the converted time.
            is_done (bool): A flag indicating whether the schedule is completed. Defaults to False.
            running (bool): A flag indicating whether the schedule is active. Defaults to True.
        """
        super(schedule, self).__init__(parent)
        self.day, hour = tools.convert_time(time.time())
        self.is_done = False
        self.running = True

    def stop(self):
        """
        Stops the current process by setting the running flag to False.

        This method is typically used to signal the termination of a loop
        or process that depends on the `running` attribute to continue execution.
        """
        self.running = False

    def run(self):
        """
        Continuously monitors the current time and triggers a progress event at a specific hour.

        This function runs in a loop while the `self.running` flag is set to True. It checks the 
        current time and compares it to a predefined hour (`17:25`). If the hour matches and the 
        day has changed since the last event, it triggers the `add_progress_event` function and 
        ensures the event is only triggered once per day.

        Attributes:
            self.running (bool): A flag to control the execution of the loop.
            self.day (str): The last recorded day when the event was triggered.
            self.is_done (bool): A flag to ensure the event is triggered only once per day.

        Behavior:
            - Converts the current time to day and hour using `tools.convert_time`.
            - Checks if the current hour matches `17:25`.
            - If the day has changed, resets the `self.is_done` flag.
            - Triggers `add_progress_event` if the event has not been triggered for the current day.
            - Sleeps for 4 seconds between iterations to reduce CPU usage.
        """
        while self.running:
            day, hour = tools.convert_time(time.time())
            # if hour.split(':')[0] == '17':
            if hour == '17:25':
                if day != self.day:
                    self.day = day
                    self.is_done = False
                if not self.is_done:
                    add_progress_event()
                    self.is_done = True
            time.sleep(4)
