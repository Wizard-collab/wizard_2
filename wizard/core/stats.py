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
    stages_rows = project.get_all_stages()
    all_frames = get_all_frames()

    assets_progresses_lists = dict()
    assets_progresses = dict()
    categories_progresses_lists = dict()
    categories_progresses = dict()
    domains_progresses_lists = dict()
    domains_progresses = dict()

    for stage_row in stages_rows:
        asset_id = stage_row['asset_id']
        if asset_id not in assets_progresses_lists.keys():
            assets_progresses_lists[asset_id] = []
        asset_row = project.get_asset_data(asset_id)
        frames_number = asset_row['outframe'] - asset_row['inframe']
        assets_progresses_lists[asset_id].append((stage_row['progress'], 1))
        domain_row = project.get_domain_data(stage_row['domain_id'])
        if asset_row['category_id'] not in categories_progresses_lists.keys():
            categories_progresses_lists[asset_row['category_id']] = []
        if domain_row['name'] == assets_vars._sequences_:
            categories_progresses_lists[asset_row['category_id']].append(
                (stage_row['progress'], frames_number / all_frames))
        else:
            categories_progresses_lists[asset_row['category_id']].append(
                (stage_row['progress'], 1))
        if domain_row['id'] not in domains_progresses_lists.keys():
            domains_progresses_lists[domain_row['id']] = []
        if domain_row['name'] == assets_vars._sequences_:
            domains_progresses_lists[domain_row['id']].append(
                (stage_row['progress'], frames_number / all_frames))
        else:
            domains_progresses_lists[domain_row['id']].append(
                (stage_row['progress'], 1))

    for asset_id in assets_progresses_lists.keys():
        assets_progresses[asset_id] = round(
            get_mean(assets_progresses_lists[asset_id]), to_round)
    for category_id in categories_progresses_lists.keys():
        categories_progresses[category_id] = round(
            get_mean(categories_progresses_lists[category_id]), to_round)
    for domain_id in domains_progresses_lists.keys():
        domains_progresses[domain_id] = round(
            get_mean(domains_progresses_lists[domain_id]), to_round)

    return assets_progresses, categories_progresses, domains_progresses


def add_progress_event(new_stage=None, removed_stage=None):
    start_time = time.time()

    all_frames = get_all_frames()

    if new_stage:
        new_stage_row = project.get_stage_data(new_stage)
        stage_name = new_stage_row['name']
        all_stages = project.get_all_stages('name')
        total_len = len(all_stages)
        stage_len = all_stages.count(stage_name)
        all_assets = project.get_all_assets()
        assets = dict()
        for asset_row in all_assets:
            assets[asset_row['id']] = asset_row

        progress_rows = project.get_all_progress_events()
        ids_to_update = []
        datas_to_update = []
        for progress_row in progress_rows:
            datas_dic = json.loads(progress_row['datas_dic'])
            original_datas_dic = datas_dic.copy()
            if stage_name not in datas_dic:
                continue
            if stage_name in assets_vars._assets_stages_list_:
                datas_dic[stage_name] = datas_dic[stage_name] * \
                    ((stage_len-1) / stage_len)
                if 'total' in datas_dic:
                    datas_dic['total'] = datas_dic['total'] * \
                        ((total_len-1) / total_len)
            elif stage_name in assets_vars._sequences_stages_list_:
                asset_row = assets[new_stage_row['asset_id']]
                frames_number = asset_row['outframe'] - asset_row['inframe']
                datas_dic[stage_name] = datas_dic[stage_name] * \
                    (all_frames-frames_number) / (all_frames)
                if 'total' in datas_dic:
                    datas_dic['total'] = datas_dic['total'] * \
                        (all_frames-frames_number) / (all_frames)
            if datas_dic == original_datas_dic:
                continue
            datas_to_update.append(
                (progress_row['id'], 'datas_dic', json.dumps(datas_dic)))
        project.update_progress_events(datas_to_update)

    if removed_stage:
        all_stages = project.get_all_stages('name')
        total_len = len(all_stages)
        stage_len = all_stages.count(new_stage)

        progress_rows = project.get_all_progress_events()
        for progress_row in progress_rows:
            datas_dic = json.loads(progress_row['datas_dic'])
            if new_stage not in datas_dic:
                continue
            datas_dic[new_stage] = datas_dic[new_stage] * \
                ((stage_len+1) / stage_len)
            if 'total' in datas_dic:
                datas_dic['total'] = datas_dic['total'] * \
                    ((total_len+1) / total_len)
            if datas_dic == json.loads(progress_row['datas_dic']):
                continue
            project.update_progress_event(
                progress_row['id'], ('datas_dic', json.dumps(datas_dic)))

    domains_rows = project.get_domains()
    domains = dict()
    for domain_row in domains_rows:
        domains[domain_row['id']] = domain_row['name']

    categories_rows = project.get_all_categories()
    categories = dict()
    for category_row in categories_rows:
        categories[category_row['id']] = category_row['name']

    assets_rows = project.get_all_assets()
    assets_categories = dict()
    for asset_row in assets_rows:
        assets_categories[asset_row['id']
                          ] = categories[asset_row['category_id']]

    stages_rows = project.get_all_stages()

    total_progresses_dic = dict()
    domains_progresses_dic = dict()
    categories_progresses_dic = dict()

    for stage_row in stages_rows:
        stage = stage_row['name']
        category = assets_categories[stage_row['asset_id']]
        domain = domains[stage_row['domain_id']]
        if domain == assets_vars._library_:
            continue
        if stage_row['state'] == 'omt':
            continue
        if domain == assets_vars._sequences_:
            asset_row = project.get_asset_data(stage_row['asset_id'])
            frames_number = asset_row['outframe'] - asset_row['inframe']
            progress = (stage_row['progress'], (frames_number/all_frames))
        else:
            progress = (stage_row['progress'], 1)

        if 'total' not in total_progresses_dic.keys():
            total_progresses_dic['total'] = []
        total_progresses_dic['total'].append(progress)
        if stage not in total_progresses_dic.keys():
            total_progresses_dic[stage] = []
        total_progresses_dic[stage].append(progress)
        if category not in categories_progresses_dic.keys():
            categories_progresses_dic[category] = dict()
        if 'total' not in categories_progresses_dic[category].keys():
            categories_progresses_dic[category]['total'] = []
        categories_progresses_dic[category]['total'].append(progress)
        if stage not in categories_progresses_dic[category].keys():
            categories_progresses_dic[category][stage] = []
        categories_progresses_dic[category][stage].append(progress)
        if domain not in domains_progresses_dic.keys():
            domains_progresses_dic[domain] = dict()
        if 'total' not in domains_progresses_dic[domain].keys():
            domains_progresses_dic[domain]['total'] = []
        domains_progresses_dic[domain]['total'].append(progress)
        if stage not in domains_progresses_dic[domain].keys():
            domains_progresses_dic[domain][stage] = []
        domains_progresses_dic[domain][stage].append(progress)

    for domain_row in domains_rows:
        if domain_row['name'] == 'library':
            continue
        if domain_row['name'] not in domains_progresses_dic.keys():
            domains_progresses_dic[domain_row['name']] = dict()
        if 'total' not in domains_progresses_dic[domain_row['name']].keys():
            domains_progresses_dic[domain_row['name']]['total'] = []
        for stage in assets_vars._stages_list_[domain_row['name']]:
            if stage not in domains_progresses_dic[domain_row['name']].keys():
                domains_progresses_dic[domain_row['name']][stage] = []

    for category_row in categories_rows:
        domain = domains[category_row['domain_id']]
        if domain == 'library':
            continue
        if category_row['name'] not in categories_progresses_dic.keys():
            categories_progresses_dic[category_row['name']] = dict()
        if 'total' not in categories_progresses_dic[category_row['name']].keys():
            categories_progresses_dic[category_row['name']]['total'] = []
        for stage in assets_vars._stages_list_[domain]:
            if stage not in categories_progresses_dic[category_row['name']].keys():
                categories_progresses_dic[category_row['name']][stage] = []

    if 'total' not in total_progresses_dic.keys():
        total_progresses_dic['total'] = []
    for stage in (assets_vars._assets_stages_list_ + assets_vars._sequences_stages_list_):
        if stage not in total_progresses_dic.keys():
            total_progresses_dic[stage] = []

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

    logger.debug(
        f"Progress event calculation duration : {time.time()-start_time}s")


def get_mean(data_list):
    if data_list == []:
        data_list = [(0, 1)]
    weighted_sum = sum(value * weight for value, weight in data_list)
    total_weight = sum(weight for _, weight in data_list)

    return weighted_sum / total_weight


def get_all_frames():
    assets_rows = project.get_all_sequence_assets()
    all_frames = 0
    for asset_row in assets_rows:
        all_frames += asset_row['outframe'] - asset_row['inframe']
    return all_frames


def get_rendered_frames():
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
    def __init__(self, parent=None):
        super(schedule, self).__init__(parent)
        self.day, hour = tools.convert_time(time.time())
        self.is_done = False
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
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
