# coding: utf-8
# Wizard commands hook

import logging
logger = logging.getLogger(__name__)

def abc_command():
	''' This function is used to store 
	a default alembic export command.
	You can modify it from here
	Be carreful on what you are modifying'''
	abc_command = "-frameRange {start} {end} "
	abc_command += "-step 1 -frameRelativeSample -0.2 -frameRelativeSample 0 -frameRelativeSample 0.2 "
	abc_command += "-attr wizardTags "
	abc_command += "-writeVisibility "
	abc_command += "-writeUVSets -uvWrite "
	abc_command += "-worldSpace "
	abc_command += "{object_list} "
	abc_command += "-dataFormat ogawa "
	abc_command += "-file {export_file} "
	abc_command += "-pythonPerFrameCallback '{perFrameCallback}' "
	return abc_command