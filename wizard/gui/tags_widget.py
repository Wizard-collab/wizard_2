# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import logging
import re

# Wizard core modules
from wizard.core import repository
from wizard.core import project
from wizard.core import image
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)

class tags_widget(gui_utils.QMenu):

    other_key_pressed = pyqtSignal(object)
    returned_text = pyqtSignal(str)

    def __init__(self, pos, text='', parent=None):
        super(tags_widget, self).__init__(parent)
        self.pos = pos
        self.text = text
        self.add_users()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Up or key == QtCore.Qt.Key_Down or key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            super().keyPressEvent(event)
        else:
            self.close() 
            self.other_key_pressed.emit(event)

    def exec(self):
        if len(self.actions) == 0:
            return
        action = self.exec_()
        if action is not None:
            token = self.text.split('@')[-1]
            text = self.text[:-(len(token)+1)] + f"@{action.text()} "
            self.returned_text.emit(text)

    def showEvent(self, event):
        self.move_ui()

    def move_ui(self):
        gui_utils.move_ui(self, pos=self.pos)

    def add_users(self):
        self.actions = []
        text = self.text.replace('\n', ' ')
        token = text.split(" ")[-1]
        if token.startswith('@'):
            token = token[1:]
            if token in 'all':
                action = self.addAction(QtGui.QIcon(ressources._guess_icon_), "all")
                self.addSeparator()
                self.actions.append(action)
            for user_id in project.get_users_ids_list():
                user_row = repository.get_user_data(user_id)
                if token in user_row['user_name']:
                    icon = QtGui.QIcon()
                    pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 24)
                    icon.addPixmap(pm)
                    action = self.addAction(icon, f"{user_row['user_name']}")
                    self.actions.append(action)
            self.addSeparator()
            for tag_group_name in project.get_all_tag_groups('name'):
                if token in tag_group_name:
                    action = self.addAction(QtGui.QIcon(ressources._tag_icon_), tag_group_name)
                    self.actions.append(action)
            if len(self.actions) > 0:
                self.setActiveAction(self.actions[0])

