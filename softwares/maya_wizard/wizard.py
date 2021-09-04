# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import maya.cmds as cmds

# Wizard modules
import wizard_communicate

def save():
	file_path=wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
	if file_path:
	    cmds.file(rename=file_path)
	    cmds.file(save=True, type='mayaAscii')