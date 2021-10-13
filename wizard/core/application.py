# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import yaml
import os

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

def get_version():
	version_file = 'version.yaml'
	if os.path.isfile(version_file):
		with open(version_file, 'r') as f:
			version_dic = yaml.load(f, Loader=yaml.Loader)
		return version_dic
	else:
		logger.error(f'{version_file} not found')
		return None