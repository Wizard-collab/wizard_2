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

# This module manages the project events
# the events are stored in the project database
# and are accessed by the 'project' module but
# this module decode what is stored in the
# event rows

# Python modules
import logging

# Wizard modules
from wizard.core import environment
from wizard.core import project
from wizard.core import assets

logger = logging.getLogger(__name__)

def add_creation_event(instance_type, instance_id):
	data = (instance_type, instance_id)
	title = f"Created {assets.instance_to_string((instance_type, instance_id))}"
	project.add_event('creation', title, '', data)

def add_export_event(export_version_id):
	title = f"Exported {assets.instance_to_string(('export_version', export_version_id))}"
	data = export_version_id
	export_version_row = project.get_export_version_data(export_version_id)
	project.add_event('export', title, export_version_row['comment'], data, '', export_version_row['work_version_thumbnail_path'])

def add_video_event(video_id, work_env_id):
	title = f"Created a video from {assets.instance_to_string(('work_env', work_env_id))}"
	data = video_id
	video_row = project.get_video_data(video_id)
	project.add_event('video', title, video_row['comment'], data, '', video_row['thumbnail_path'])

def add_archive_event(title, archive_path):
	data = archive_path
	project.add_event('archive', title, '', data)

def add_tag_event(instance_type, instance_id, comment, user):
	data_dic = dict()
	data_dic['instance'] = (instance_type, instance_id)
	data_dic['tagged_user'] = user
	title = f"Tagged {user} in a comment"
	project.add_event('tag', title, comment, data_dic)