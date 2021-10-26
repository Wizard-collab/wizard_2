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

# This provide substasks pycmds

# Python modules


# Wizard modules
from wizard.core import subtask
from wizard.core import custom_logger
logger = custom_logger.get_logger()

def archive_versions(version_ids):
	command =  "# coding: utf-8\n"
	command += "from wizard.core import assets\n"
	command += "from wizard.gui import gui_server\n"
	command += "print('wizard_task_name:Version archiving')\n"
	command += f"percent_step=100.0/len({version_ids})\n"
	command += "percent=0.0\n"
	command += "print(f'wizard_task_percent:{percent}')\n"
	command += f"for version_id in {version_ids}:\n"
	command += "	assets.archive_version(version_id)\n"
	command += "	percent+=percent_step\n"
	command += "	print(f'wizard_task_percent:{percent}')\n"
	command += "gui_server.refresh_ui()\n"
	command += "print('wizard_task_status:done')\n"
	task = subtask.subtask(pycmd=command, print_stdout=True)
	task.start()
	logger.info('Archiving started as subtask, open the subtask manager to get more informations')

def archive_export_versions(export_version_ids):
	command =  "# coding: utf-8\n"
	command += "from wizard.core import assets\n"
	command += "from wizard.gui import gui_server\n"
	command += "print('wizard_task_name:Export version archiving')\n"
	command += f"percent_step=100.0/len({export_version_ids})\n"
	command += "percent=0.0\n"
	command += "print(f'wizard_task_percent:{percent}')\n"
	command += f"for export_version_id in {export_version_ids}:\n"
	command += "	assets.archive_export_version(export_version_id)\n"
	command += "	percent+=percent_step\n"
	command += "	print(f'wizard_task_percent:{percent}')\n"
	command += "gui_server.refresh_ui()\n"
	command += "print('wizard_task_status:done')\n"
	task = subtask.subtask(pycmd=command, print_stdout=True)
	task.start()
	logger.info('Archiving started as subtask, open the subtask manager to get more informations')

def archive_exports(export_ids):
	command =  "# coding: utf-8\n"
	command += "from wizard.core import assets\n"
	command += "from wizard.gui import gui_server\n"
	command += "print('wizard_task_name:Export archiving')\n"
	command += f"percent_step=100.0/len({export_ids})\n"
	command += "percent=0.0\n"
	command += "print(f'wizard_task_percent:{percent}')\n"
	command += f"for export_id in {export_ids}:\n"
	command += "	assets.archive_export(export_id)\n"
	command += "	percent+=percent_step\n"
	command += "	print(f'wizard_task_percent:{percent}')\n"
	command += "gui_server.refresh_ui()\n"
	command += "print('wizard_task_status:done')\n"
	task = subtask.subtask(pycmd=command, print_stdout=True)
	task.start()
	logger.info('Archiving started as subtask, open the subtask manager to get more informations')

def archive_asset(asset_id):
	command =  "# coding: utf-8\n"
	command += "from wizard.core import assets\n"
	command += "from wizard.gui import gui_server\n"
	command += "print('wizard_task_name:Asset archiving')\n"
	command += "print('wizard_task_percent:0')\n"
	command += f"assets.archive_asset({asset_id})\n"
	command += "print('wizard_task_percent:100')\n"
	command += "gui_server.refresh_ui()\n"
	command += "print('wizard_task_status:done')\n"
	task = subtask.subtask(pycmd=command, print_stdout=True)
	task.start()
	logger.info('Archiving started as subtask, open the subtask manager to get more informations')

def archive_category(category_id):
	command =  "# coding: utf-8\n"
	command += "from wizard.core import assets\n"
	command += "from wizard.gui import gui_server\n"
	command += "print('wizard_task_name:Category archiving')\n"
	command += "print('wizard_task_percent:0')\n"
	command += f"assets.archive_category({category_id})\n"
	command += "print('wizard_task_percent:100')\n"
	command += "gui_server.refresh_ui()\n"
	command += "print('wizard_task_status:done')\n"
	task = subtask.subtask(pycmd=command, print_stdout=True)
	task.start()
	logger.info('Archiving started as subtask, open the subtask manager to get more informations')

def archive_stage(stage_id):
	command =  "# coding: utf-8\n"
	command += "from wizard.core import assets\n"
	command += "from wizard.gui import gui_server\n"
	command += "print('wizard_task_name:Stage archiving')\n"
	command += "print('wizard_task_percent:0')\n"
	command += f"assets.archive_stage({stage_id})\n"
	command += "print('wizard_task_percent:100')\n"
	command += "gui_server.refresh_ui()\n"
	command += "print('wizard_task_status:done')\n"
	task = subtask.subtask(pycmd=command, print_stdout=True)
	task.start()
	logger.info('Archiving started as subtask, open the subtask manager to get more informations')