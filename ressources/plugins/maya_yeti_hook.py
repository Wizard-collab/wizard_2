import logging
logger = logging.getLogger(__name__)

import pymel.core as pm

def yeti_sanity(stage_name):
	if stage_name == 'grooming':
		# Grooming sanity
		sanity_status = True
		if not pm.objExists('yeti_scalps_set'):
			logger.warning("yeti_scalps_set not found")
			sanity_status = False
		if not pm.objExists('yeti_nodes_set'):
			logger.warning("yeti_nodes_set not found")
			sanity_status = False
		return sanity_status
	else:
		return True

def yeti_before_export(stage_name):
	if stage_name == 'grooming':
		yeti_scalps_set = pm.PyNode('yeti_scalps_set')
		yeti_nodes_set = pm.PyNode('yeti_nodes_set')
		return [yeti_scalps_set, yeti_nodes_set]
	else:
		return []
