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
	fix_artefacts()
	project.create_assets_groups_table(environment.get_project_name())
	sql_cmd = """ALTER TABLE assets ADD COLUMN IF NOT EXISTS assets_group_id integer REFERENCES assets_groups (id);"""
	db_utils.create_table(environment.get_project_name(), sql_cmd)

	import time
	start_date = time.time()
	sql_cmd = f"""ALTER TABLE stages ADD COLUMN IF NOT EXISTS start_date real NOT NULL DEFAULT {start_date};"""
	db_utils.create_table(environment.get_project_name(), sql_cmd)

	sql_cmd = f"""ALTER TABLE references_data ADD COLUMN IF NOT EXISTS activated integer NOT NULL DEFAULT 1;"""
	db_utils.create_table(environment.get_project_name(), sql_cmd)
	sql_cmd = f"""ALTER TABLE grouped_references_data ADD COLUMN IF NOT EXISTS activated integer NOT NULL DEFAULT 1;"""
	db_utils.create_table(environment.get_project_name(), sql_cmd)
	sql_cmd = f"""ALTER TABLE referenced_groups_data ADD COLUMN IF NOT EXISTS activated integer NOT NULL DEFAULT 1;"""
	db_utils.create_table(environment.get_project_name(), sql_cmd)

def fix_stages_duration():
	stage_rows = project.get_all_stages()
	for stage in stage_rows:
		assets.modify_stage_estimation(stage['id'], 3)

def fix_artefacts():
	for user in repository.get_user_names_list():
		user_row = repository.get_user_row_by_name(user)
		artefacts_list = json.loads(user_row['artefacts'])
		if type(artefacts_list) == dict:
			return
		artefacts_dic = dict()
		for artefact in artefacts_list:
			artefacts_dic[time.time()] = artefact
		repository.modify_user_artefacts(user, artefacts_dic)