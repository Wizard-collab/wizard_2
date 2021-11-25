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

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

from wizard.core import environment
from wizard.core import project
from wizard.core import assets

def add_creation_event(instance_type, instance_id):
	data = (instance_type, instance_id)
	if instance_type == 'category':
		category_name = project.get_category_data(instance_id, 'name')
		title = f"Created {category_name}"
	elif instance_type == 'asset':
		asset_row = project.get_asset_data(instance_id)
		category_row = project.get_category_data(asset_row['category_id'])
		title = f"Created {category_row['name']}-{asset_row['name']}"
	elif instance_type == 'variant':
		variant_row = project.get_variant_data(instance_id)
		stage_row = project.get_stage_data(variant_row['stage_id'])
		asset_row = project.get_asset_data(stage_row['asset_id'])
		category_row = project.get_category_data(asset_row['category_id'])
		title = f"Created {category_row['name']}-{asset_row['name']}-{stage_row['name']}-{variant_row['name']}"

	#message = assets.instance_to_string((instance_type, instance_id))
	message = ''
	project.add_event('creation', title, message, data)

def add_export_event(export_version_id):
	export_version_row = project.get_export_version_data(export_version_id)
	export_row = project.get_export_data(export_version_row['export_id'])
	variant_row = project.get_variant_data(export_version_row['variant_id'])
	stage_row = project.get_stage_data(export_version_row['stage_id'])
	asset_row = project.get_asset_data(stage_row['asset_id'])
	category_row = project.get_category_data(asset_row['category_id'])
	title = f"Exported {category_row['name']}-{asset_row['name']}-{stage_row['name']}-{variant_row['name']}"
	data = export_version_id
	export_version_row = project.get_export_version_data(export_version_id)
	message = f"Exported asset : {export_row['name']}\nVersion : {export_version_row['name']}"
	project.add_event('export', title, message, data, export_version_row['comment'], export_version_row['work_version_thumbnail_path'])

def add_archive_event(message, archive_path, additional_message):
	title = 'Archive event'
	data = archive_path
	project.add_event('archive', title, message, additional_message, data)
