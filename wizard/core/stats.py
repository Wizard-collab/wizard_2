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
import statistics
import json
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from wizard.core import tools
from wizard.core import project
from wizard.core import environment
from wizard.vars import assets_vars

def add_progress_event():
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
        assets_categories[asset_row['id']] = categories[asset_row['category_id']]

    stages_rows = project.get_all_stages()

    total_progresses_dic = dict()
    domains_progresses_dic = dict()
    categories_progresses_dic = dict()

    for stage_row in stages_rows:
        stage = stage_row['name']
        category = assets_categories[stage_row['asset_id']]
        domain = domains[stage_row['domain_id']]
        if domain != assets_vars._library_:
            if 'total' not in total_progresses_dic.keys():
                total_progresses_dic['total'] = []
            total_progresses_dic['total'].append(stage_row['progress'])
            if stage not in total_progresses_dic.keys():
                total_progresses_dic[stage] = []
            total_progresses_dic[stage].append(stage_row['progress'])
            if category not in categories_progresses_dic.keys():
                categories_progresses_dic[category] = dict()
            if 'total' not in categories_progresses_dic[category].keys():
                categories_progresses_dic[category]['total'] = []
            categories_progresses_dic[category]['total'].append(stage_row['progress'])
            if stage not in categories_progresses_dic[category].keys():
                categories_progresses_dic[category][stage] = []
            categories_progresses_dic[category][stage].append(stage_row['progress'])
            if domain not in domains_progresses_dic.keys():
                domains_progresses_dic[domain] = dict()
            if 'total' not in domains_progresses_dic[domain].keys():
                domains_progresses_dic[domain]['total'] = []
            domains_progresses_dic[domain]['total'].append(stage_row['progress'])
            if stage not in domains_progresses_dic[domain].keys():
                domains_progresses_dic[domain][stage] = []
            domains_progresses_dic[domain][stage].append(stage_row['progress'])

    for stage in total_progresses_dic.keys():
        total_progresses_dic[stage] = get_mean(total_progresses_dic[stage])
    project.add_progress_event('total', 'All project', json.dumps(total_progresses_dic))

    for domain in domains_progresses_dic.keys():
        for stage in domains_progresses_dic[domain].keys():
            domains_progresses_dic[domain][stage] = get_mean(domains_progresses_dic[domain][stage])
        project.add_progress_event('domain', domain, json.dumps(domains_progresses_dic[domain]))

    for category in categories_progresses_dic.keys():
        for stage in categories_progresses_dic[category].keys():
            categories_progresses_dic[category][stage] = get_mean(categories_progresses_dic[category][stage])
        project.add_progress_event('category', category, json.dumps(categories_progresses_dic[category]))

def get_mean(data_list):
    if data_list == []:
        data_list = [0]
    return statistics.mean(data_list)

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
            #if hour.split(':')[0] == '17':  
            if hour == '17:25':  
                if day != self.day:
                    self.day = day
                    self.is_done = False
                if not self.is_done:
                    add_progress_event()
                    self.is_done = True
            time.sleep(4)
