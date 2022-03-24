# coding: utf-8
# Wizard hook

import logging
logger = logging.getLogger(__name__)

def before_export(stage_name):
	''' This function is triggered
		before the export 

		The "stage_name" argument is the name
		of the exported stage '''
	pass

def after_export(stage_name, export_dir):
	''' This function is triggered
		after the export

		The "stage_name" argument is the name
		of the exported stage

		The "export_dir" argument is the path wher wizard exported the
		file as string '''
	pass
