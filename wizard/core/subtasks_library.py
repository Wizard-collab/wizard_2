# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

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
	logger.info('Archiving started as subtask, open the subtask manager to get mode informations')

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
	logger.info('Archiving started as subtask, open the subtask manager to get mode informations')

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
	logger.info('Archiving started as subtask, open the subtask manager to get mode informations')

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
	logger.info('Archiving started as subtask, open the subtask manager to get mode informations')