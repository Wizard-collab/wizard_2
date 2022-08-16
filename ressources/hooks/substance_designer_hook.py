# coding: utf-8
# Wizard hook

import logging
logger = logging.getLogger(__name__)

def sanity(stage_name):
	''' This function is triggered
		before the export and will stop the
		export process if the returned data is 
		"False"
		
		The "stage_name" argument is the name
		of the exported stage '''
	return True

def before_export(stage_name):
	''' This function is triggered
		before the export 

		The "stage_name" argument is the name
		of the exported stage

		You can return a list of objects 
		that wizard will add to the export '''
	return []

def after_export(stage_name, export_dir):
	''' This function is triggered
		after the export

		The "stage_name" argument is the name
		of the exported stage

		The "export_dir" argument is the path wher wizard exported the
		file as string '''
	pass

def after_reference(stage_name, 
						referenced_stage_name, 
						referenced_files_dir,
						namespace, 
 						new_objects):
	''' This function is triggered
		after referencing from wizard

		The "stage_name" argument is the name
		of the exported stage

		The "referenced_stage_name" argument is the name
		of the referenced stage

		The "referenced_files_dir" argument is the directory where the
		referenced files comes from

		The "namespace" argument is the namespace of the reference

		The "new_objects" argument is a list of the new objects added
		to the current scene after the reference '''
	pass