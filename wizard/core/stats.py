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

# This module manages the wizard "game" part
# it uses the "repository" module to access 
# and write user data
# Uses this module to add xps, levels,
# remove levels and remove life

# Python modules
import time
import threading
import statistics
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from wizard.core import tools
from wizard.core import project
from wizard.core import environment
from wizard.vars import assets_vars

def add_progress_event():
    stages_rows = project.get_all_stages()
    stages_progresses_dic = dict()
    domains_progresses_dic = dict()
    all_progresses = []
    for stage_row in stages_rows:
        all_progresses.append(stage_row['progress'])
        if stage_row['name'] not in stages_progresses_dic.keys():
            stages_progresses_dic[stage_row['name']] = []
        stages_progresses_dic[stage_row['name']].append(stage_row['progress'])
        if stage_row['name'] in assets_vars._assets_stages_list_:
            if 'assets' not in domains_progresses_dic.keys():
                domains_progresses_dic['assets'] = []
            domains_progresses_dic['assets'].append(stage_row['progress'])
        elif stage_row['name'] in assets_vars._sequences_stages_list_:
            if 'sequences' not in domains_progresses_dic.keys():
                domains_progresses_dic['sequences'] = []
            domains_progresses_dic['sequences'].append(stage_row['progress'])
    if all_progresses == []:
        all_progresses = [0]
    total = statistics.mean(all_progresses)
    for stage in stages_progresses_dic.keys():
        mean = statistics.mean(stages_progresses_dic[stage])
        project.add_progress_event('stage', stage, mean)
    for domain in domains_progresses_dic.keys():
        mean = statistics.mean(domains_progresses_dic[domain])
        project.add_progress_event('domain', domain, mean)
    project.add_progress_event('total', '', total)

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
