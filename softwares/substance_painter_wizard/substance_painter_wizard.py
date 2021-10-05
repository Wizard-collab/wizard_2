# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com
    
# Python modules
import os
import logging
from PySide2 import QtWidgets, QtCore, QtGui

# Substance Painter modules
import substance_painter.project
import substance_painter.ui

# Wizard modules
import wizard_communicate

def save():
    file_path = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path:
        if substance_painter.project.is_open():
            if substance_painter.project.needs_saving():
                substance_painter.project.save_as(file_path,
                                                  substance_painter.project.ProjectSaveMode.Full)
            else:
                logging.info("There is nothing to save!")
        else:
            logging.info("No painter project openned!")

class wizard_toolbar(QtWidgets.QMenu):
    def __init__(self):
        super(wizard_toolbar, self).__init__()
        self.setTitle('Wizard')
        substance_painter.ui.add_menu(self)
        save_icon = os.path.abspath("icons/save_increment.png")
        self.save_action = self.addAction(QtGui.QIcon(save_icon), 'Save')
        self.save_action.triggered.connect(save)
