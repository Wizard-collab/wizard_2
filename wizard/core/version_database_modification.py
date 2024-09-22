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
import traceback
import json
import time
import logging

logger = logging.getLogger(__name__)

# Wizard modules
from wizard.core import environment
from wizard.core import repository
from wizard.core import project
from wizard.core import assets
from wizard.core import db_utils

def main():
	add_rendering_extensions()

def add_rendering_extensions():
	from wizard.core import project
	from wizard.vars import softwares_vars
	from wizard.vars import assets_vars


	for software in softwares_vars._softwares_list_:
		for stage in assets_vars._ext_dic_.keys():
			if stage != 'rendering':
				continue
			software_id = project.get_software_data_by_name(software,'id')
			if software in assets_vars._ext_dic_[stage].keys():
				extension = assets_vars._ext_dic_[stage][software][0]
				if not project.get_default_extension_row(stage, software_id, ignore_warning=True):
					project.create_extension_row(stage, software_id, extension)

	sql_cmd = """ALTER TABLE settings ADD COLUMN IF NOT EXISTS OCIO text;"""
	db_utils.create_table(environment.get_project_name(), sql_cmd)
