import logging
logger = logging.getLogger(__name__)

def before_export():
	''' This function is triggered
		before the export '''
	pass

def after_export(export_dir):
	''' This function is triggered
		after the export '''
	pass

def before_reference():
	''' This function is triggered
		before the import '''
	pass

def after_reference():
	''' This function is triggered
		before the import '''
	pass