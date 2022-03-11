# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import logging

# Wizard modules
from wizard.core import project
from wizard.core import assets
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import references_widget
from wizard.gui import color_picker
from wizard.gui import gui_utils
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

class groups_manager_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(groups_manager_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Groups manager")

        self.groups = dict()
        self.group_id = None
        self.old_group_id = None

        self.build_ui()
        self.connect_functions()
        self.refresh()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
                self.refresh()
            else:
                self.close()
        else:
            self.show()
            self.raise_()
            self.refresh()

    def set_group_id(self, group_id):
        group_name = project.get_group_data(group_id, 'name')
        if group_name in self.groups.keys():
            self.groups_comboBox.setCurrentText(group_name)

    def build_ui(self):
        self.resize(QtCore.QSize(1000,700))
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header = QtWidgets.QWidget()
        self.header.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(6)
        self.header.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header)

        self.create_group_button = QtWidgets.QPushButton()
        self.create_group_button.setFixedSize(26,26)
        self.create_group_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.create_group_button.setIconSize(QtCore.QSize(16,16))
        self.header_layout.addWidget(self.create_group_button)

        self.groups_comboBox = gui_utils.QComboBox()
        self.groups_comboBox.setFixedWidth(300)
        self.header_layout.addWidget(self.groups_comboBox)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.color_button = QtWidgets.QPushButton()
        self.color_button.setFixedSize(26,26)
        self.color_button.setObjectName('color_button')
        self.header_layout.addWidget(self.color_button)

        self.delete_group_button = QtWidgets.QPushButton()
        self.delete_group_button.setFixedSize(26,26)
        self.delete_group_button.setIcon(QtGui.QIcon(ressources._tool_archive_))
        self.delete_group_button.setIconSize(QtCore.QSize(24,24))
        self.header_layout.addWidget(self.delete_group_button)

        self.references_widget = references_widget.references_widget('groups')
        self.main_layout.addWidget(self.references_widget)

    def connect_functions(self):
        self.create_group_button.clicked.connect(self.create_group)
        self.color_button.clicked.connect(self.modify_color)
        self.delete_group_button.clicked.connect(self.delete_group)
        self.groups_comboBox.currentTextChanged.connect(self.current_group_changed)

    def current_group_changed(self):
        self.old_group_id = self.group_id
        if self.update_grouped_references:
            self.get_current_group_id()
            self.update_color()
            self.references_widget.change_work_env(self.group_id)

    def update_color(self):
        group_name = self.get_current_group()
        if group_name != '':
            color = self.groups[group_name]['color']
        else:
            color = 'transparent'
        self.update_button_color(color)

    def modify_color(self):
        group_name = self.get_current_group()
        if group_name != '':
            color = self.groups[group_name]['color']
            self.color_picker = color_picker.color_picker(color=color)
            self.color_picker.color_signal.connect(self.update_button_color)
            self.color_picker.validate_signal.connect(self.modify_group_color)
            self.color_picker.show()

    def modify_group_color(self, color):
        project.modify_group_color(self.group_id, color)
        gui_server.refresh_ui()

    def update_button_color(self, color):
        self.color_button.setStyleSheet(f'background-color:{color};')

    def get_current_group_id(self):
        current_group = self.groups_comboBox.currentText()
        if current_group != '':
            self.group_id = self.groups[current_group]['id']
        else:
            self.group_id = None

    def get_current_group(self):
        return self.groups_comboBox.currentText()

    def create_group(self):
        self.group_creation_widget = group_creation_widget(self)
        if self.group_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
            group_name = self.group_creation_widget.name_field.text()
            new_group_id = assets.create_group(group_name)
            gui_server.refresh_ui()
            self.groups_comboBox.setCurrentText(group_name)

    def delete_group(self):
        current_group = self.groups_comboBox.currentText()
        if current_group != '':
            group_id = self.groups[current_group]['id']
            assets.remove_group(group_id)
            gui_server.refresh_ui()

    def remove_group(self, group):
        if group in self.groups.keys():
            index = self.groups_comboBox.findText(group)
            self.groups_comboBox.removeItem(index)
            del self.groups[group]

    def refresh(self):
        if self.isVisible():
            self.update_grouped_references = False
            groups_rows = project.get_groups()
            project_groups = []
            for group_row in groups_rows:
                project_groups.append(group_row['name'])
                if group_row['name'] not in self.groups.keys():
                    index = self.groups_comboBox.addItem(gui_utils.QIcon_from_svg(ressources._group_icon_,
                                                            group_row['color']), group_row['name'])
                else:
                    index = self.groups_comboBox.findText(group_row['name'])
                    self.groups_comboBox.setItemIcon(index, gui_utils.QIcon_from_svg(ressources._group_icon_,
                                                            group_row['color']))
                self.groups[group_row['name']] = group_row

            groups = list(self.groups.keys())
            for group in groups:
                if group not in project_groups:
                    self.remove_group(group)
            self.update_grouped_references = True
            self.get_current_group_id()
            if self.group_id != self.old_group_id:
                self.current_group_changed()
            else:
                self.references_widget.refresh()

class group_creation_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(group_creation_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        self.apply_round_corners(corner)
        event.accept()
        self.name_field.setFocus()

    def apply_round_corners(self, corner):
        self.main_frame.setStyleSheet("#variant_creation_widget{border-%s-radius:0px;}"%corner)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)

        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.close_layout.addWidget(QtWidgets.QLabel('New group'))
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding)
        self.close_layout.addSpacerItem(self.spaceItem)
        self.close_pushButton = gui_utils.transparent_button(ressources._close_tranparent_icon_, ressources._close_icon_)
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)

        self.name_field = QtWidgets.QLineEdit()
        self.frame_layout.addWidget(self.name_field)

        self.accept_button = QtWidgets.QPushButton('Create')
        self.accept_button.setObjectName("blue_button")
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.frame_layout.addWidget(self.accept_button)

    def connect_functions(self):
        self.accept_button.clicked.connect(self.accept)
        self.close_pushButton.clicked.connect(self.reject)


