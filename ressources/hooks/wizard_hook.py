# coding: utf-8
# Wizard hook

import logging
logger = logging.getLogger(__name__)

def after_export(export_version_string,
					export_dir,
					stage_name,
					gui):
	''' This function is triggered
		after an export.

		The "export_version_string" argument is the exported asset as
		string

		The "export_dir" argument is the directory where the 
		asset was exported

		The "stage_name" argument is the name of the
		exported stage

		The "gui" argument is true if wizard is openned 
		with the user interface, if it is PyWizard or wizard_CMD,
		gui will be false.'''
	pass
