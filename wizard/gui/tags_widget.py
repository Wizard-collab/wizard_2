# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import logging

# Wizard core modules
from wizard.core import repository
from wizard.core import project
from wizard.core import image

# Wizard gui modules
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)

class tags_widget(gui_utils.QMenu):

    other_key_pressed = pyqtSignal(object)

    def __init__(self, pos, parent=None):
        super(tags_widget, self).__init__(parent)
        self.pos = pos
        self.add_users()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Up or key == QtCore.Qt.Key_Down or key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            super().keyPressEvent(event)
        else:
            self.other_key_pressed.emit(event)
            self.close() 

    def showEvent(self, event):
        self.move_ui()

    def move_ui(self):
        gui_utils.move_ui(self, pos=self.pos)

    def add_users(self):
        for user_id in project.get_users_ids_list():
            user_row = repository.get_user_data(user_id)
            icon = QtGui.QIcon()
            pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 24)
            icon.addPixmap(pm)
            self.addAction(icon, user_row['user_name'])
