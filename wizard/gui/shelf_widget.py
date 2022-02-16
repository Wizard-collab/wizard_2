# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard modules
from wizard.vars import ressources
from wizard.core import shelf
from wizard.core import project
from wizard.core import tools

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import create_tool_widget

class shelf_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(shelf_widget, self).__init__(parent)

        self.help_widget = help_widget(self)
        self.scripts_ids = dict()
        self.edit_mode = False

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('shelf_widget')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(4,4,4,4)
        self.setLayout(self.main_layout)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(2)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.edit_mode_widget = QtWidgets.QWidget()
        self.edit_mode_layout = QtWidgets.QHBoxLayout()
        self.edit_mode_layout.setContentsMargins(0,0,0,0)
        self.edit_mode_layout.setSpacing(1)
        self.edit_mode_widget.setLayout(self.edit_mode_layout)
        self.main_layout.addWidget(self.edit_mode_widget)
        self.edit_mode_widget.setVisible(False)

        self.move_left_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.move_left_button, 'Move selected shelf tool')
        self.move_left_button.setIcon(QtGui.QIcon(ressources._left_icon_))
        self.move_left_button.setFixedSize(20,20)
        self.move_right_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.move_right_button, 'Move selected shelf tool')
        self.move_right_button.setIcon(QtGui.QIcon(ressources._right_icon_))
        self.move_right_button.setFixedSize(20,20)
        self.edit_mode_layout.addWidget(self.move_left_button)
        self.edit_mode_layout.addWidget(self.move_right_button)

        self.edit_mode_label = QtWidgets.QLabel(' edit mode ')
        self.edit_mode_label.setObjectName('orange_label')
        self.edit_mode_layout.addWidget(self.edit_mode_label)

        self.edit_mode_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.edit_mode_button, 'Switch to edit mode')
        self.edit_mode_button.setObjectName('edit_mode_button')
        self.edit_mode_button.setCheckable(True)
        self.edit_mode_button.setFixedSize(20,20)
        self.edit_mode_button.setIcon(QtGui.QIcon(ressources._edit_icon_))
        self.edit_mode_button.setIconSize(QtCore.QSize(10,10))
        self.main_layout.addWidget(self.edit_mode_button)

        self.add_script_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.add_script_button, 'Create shelf tool')
        self.add_script_button.setFixedSize(20,20)
        self.add_script_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.add_script_button.setIconSize(QtCore.QSize(10,10))
        self.main_layout.addWidget(self.add_script_button)

        self.script_folder_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.script_folder_button, 'Open scripts folder')
        self.script_folder_button.setFixedSize(20,20)
        self.script_folder_button.setIcon(QtGui.QIcon(ressources._folder_icon_))
        self.script_folder_button.setIconSize(QtCore.QSize(10,10))
        self.main_layout.addWidget(self.script_folder_button)

    def connect_functions(self):
        self.add_script_button.clicked.connect(self.create_script)
        self.script_folder_button.clicked.connect(self.open_script_folder)
        self.edit_mode_button.clicked.connect(self.toggle_edit_mode)
        self.move_left_button.clicked.connect(self.move_checked_left)
        self.move_right_button.clicked.connect(self.move_checked_right)

    def open_script_folder(self):
        os.startfile(project.get_scripts_folder())

    def create_script(self):
        menu = gui_utils.QMenu()
        tool_action = menu.addAction(QtGui.QIcon(ressources._python_icon_), 'Tool')
        separator_action = menu.addAction(QtGui.QIcon(ressources._separator_icon_), 'Separator')
        action = menu.exec_(QtGui.QCursor().pos())
        if action == tool_action:
            self.create_tool_widget = create_tool_widget.create_tool_widget()
            self.create_tool_widget.show()
        elif action == separator_action:
            shelf.create_separator()
            gui_server.refresh_ui()

    def edit_script(self, script_id):
        self.create_tool_widget = create_tool_widget.create_tool_widget(script_id=script_id)
        self.create_tool_widget.show()

    def delete_script(self, script_id):
        if project.delete_shelf_script(script_id):
            gui_server.refresh_ui()

    def toggle_edit_mode(self):
        if self.edit_mode:
            self.apply_positions()

        self.edit_mode = self.edit_mode_button.isChecked()
        self.edit_mode_widget.setVisible(self.edit_mode)
        for script_id in self.scripts_ids.keys():
            self.scripts_ids[script_id]['widget'].toggle_edit_mode(self.edit_mode)

    def apply_positions(self):
        for script_id in self.scripts_ids.keys():
            script_id = self.scripts_ids[script_id]['row']['id']
            position = self.buttons_layout.indexOf(self.scripts_ids[script_id]['widget'])
            if position != self.scripts_ids[script_id]['row']['position']:
                project.modify_shelf_script_position(script_id, position)
        gui_server.refresh_ui()

    def move_checked_left(self):
        positions_dic = self.get_positions()
        for index in sorted(list(positions_dic.keys())):
            if index > 0:
                self.buttons_layout.insertWidget(index-1, self.scripts_ids[positions_dic[index]]['widget'])

    def move_checked_right(self):
        positions_dic = self.get_positions()
        for index in sorted(list(positions_dic.keys()), reverse=True):
            if index < self.buttons_layout.count()-1:
                self.buttons_layout.insertWidget(index+1, self.scripts_ids[positions_dic[index]]['widget'])

    def get_positions(self):
        positions_dic = dict()
        for script_id in self.scripts_ids.keys():
            if self.scripts_ids[script_id]['widget'].isChecked():
                index = self.buttons_layout.indexOf(self.scripts_ids[script_id]['widget'])
                positions_dic[index] = script_id
        return positions_dic

    def refresh(self):
        shelf_scripts_rows = project.get_all_shelf_scripts()
        if shelf_scripts_rows is not None:
            project_scripts_ids = []
            for shelf_script_row in shelf_scripts_rows:
                project_scripts_ids.append(shelf_script_row['id'])
                if shelf_script_row['id'] not in self.scripts_ids.keys():
                    self.scripts_ids[shelf_script_row['id']] = dict()
                    self.scripts_ids[shelf_script_row['id']]['row'] = shelf_script_row

                    if shelf_script_row['type'] == 'tool':
                        self.button = shelf_script_button(shelf_script_row)
                        self.button.exec_signal.connect(self.exec_script)
                        self.button.help_signal.connect(self.show_help)
                        self.button.hide_help_signal.connect(self.hide_help)
                        self.button.edit_signal.connect(self.edit_script)
                        self.button.delete_signal.connect(self.delete_script)
                        self.buttons_layout.insertWidget(shelf_script_row['position'], self.button)
                        self.scripts_ids[shelf_script_row['id']]['widget'] = self.button
                    elif shelf_script_row['type'] == 'separator':
                        self.separator = shelf_separator(shelf_script_row)
                        self.separator.delete_signal.connect(self.delete_script)
                        self.buttons_layout.insertWidget(shelf_script_row['position'], self.separator)
                        self.scripts_ids[shelf_script_row['id']]['widget'] = self.separator
                else:
                    self.scripts_ids[shelf_script_row['id']]['row'] = shelf_script_row
                    if shelf_script_row['type'] == 'tool':
                        self.scripts_ids[shelf_script_row['id']]['widget'].update(shelf_script_row)
                    self.buttons_layout.insertWidget(shelf_script_row['position'], self.scripts_ids[shelf_script_row['id']]['widget'])

            scripts_ids_list = list(self.scripts_ids.keys())
            for script_id in scripts_ids_list:
                if script_id not in project_scripts_ids:
                    self.remove_script(script_id)

    def remove_script(self, script_id):
        self.scripts_ids[script_id]['widget'].setParent(None)
        self.scripts_ids[script_id]['widget'].deleteLater()
        del self.scripts_ids[script_id]

    def show_help(self, script_id):
        self.help_widget = help_widget(self)
        self.help_widget.show_help(self.scripts_ids[script_id]['row']['name'],
                                    self.scripts_ids[script_id]['row']['help'])

    def hide_help(self):
        self.help_widget.close()

    def exec_script(self, script_id):
        shelf.execute_script(script_id)

class help_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(help_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ToolTip)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.build_ui()

    def build_ui(self):
        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.main_widget_layout)

        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setObjectName('black_round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.main_widget_layout.addWidget(self.main_widget)

        self.tool_name = QtWidgets.QLabel()
        self.tool_name.setObjectName('bold_label')
        self.main_layout.addWidget(self.tool_name)

        self.line_frame = QtWidgets.QFrame()
        self.line_frame.setFixedHeight(1)
        self.line_frame.setStyleSheet('background-color:rgba(255,255,255,20)')
        self.main_layout.addWidget(self.line_frame)

        self.tool_help = QtWidgets.QLabel()
        self.main_layout.addWidget(self.tool_help)

        self.right_click_label = QtWidgets.QLabel('Right click to edit')
        self.right_click_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.right_click_label)

    def show_help(self, name, help):
        gui_utils.move_ui(self, 30)
        self.tool_name.setText(name)
        self.tool_help.setText(help)
        QtWidgets.QApplication.processEvents()
        self.show()

class shelf_separator(QtWidgets.QFrame):

    delete_signal = pyqtSignal(int)

    def __init__(self, shelf_script_row, parent = None):
        super(shelf_separator, self).__init__(parent)
        self.shelf_script_row = shelf_script_row
        self.is_checked = False
        self.edit_mode = False
        self.build_ui()

    def build_ui(self):
        self.setFixedWidth(11)
        self.setObjectName('shelf_seperator_container')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(5,1,5,1)
        self.setLayout(self.main_layout)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setFixedWidth(1)
        self.main_frame.setStyleSheet('background-color:white;')
        self.main_layout.addWidget(self.main_frame)

    def isChecked(self):
        return self.is_checked

    def setChecked(self, state):
        self.is_checked = state

    def enterEvent(self, event):
        if self.edit_mode:
            if not self.isChecked():
                self.setStyleSheet('#shelf_seperator_container{background-color: rgba(255,255,255,30);}')
            else:
                self.setStyleSheet('#shelf_seperator_container{background-color: rgba(255,255,255,30);border:1px solid #f79360;}')

    def leaveEvent(self, event):
        if self.edit_mode:
            if not self.isChecked():
                self.setStyleSheet('')
            else:
                self.setStyleSheet('#shelf_seperator_container{border:1px solid #f79360;}')

    def mousePressEvent(self, event):
        if self.edit_mode:
            if event.button() == QtCore.Qt.LeftButton:
                self.setStyleSheet('#shelf_seperator_container{background-color:#1d1d21;}')

    def mouseReleaseEvent(self, event):
        event.accept()
        if self.edit_mode:
            if event.button() == QtCore.Qt.LeftButton:
                if self.isChecked():
                    self.setStyleSheet('')
                    self.setChecked(False)
                else:
                    self.setStyleSheet('#shelf_seperator_container{border:1px solid #f79360;}')
                    self.setChecked(True)   
        else:
            if event.button() == QtCore.Qt.RightButton:
                self.custom_menu()

    def custom_menu(self):
        if not self.edit_mode:
            menu = gui_utils.QMenu()
            delete_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Delete')
            action = menu.exec_(QtGui.QCursor().pos())
            if action == delete_action:
                self.delete_signal.emit(self.shelf_script_row['id'])

    def toggle_edit_mode(self, state):
        self.edit_mode = state
        if not self.edit_mode:
            self.setChecked(False)
            self.setStyleSheet('')

class shelf_script_button(QtWidgets.QPushButton):

    exec_signal = pyqtSignal(int)
    help_signal = pyqtSignal(int) 
    hide_help_signal = pyqtSignal(int)
    edit_signal = pyqtSignal(int)
    delete_signal = pyqtSignal(int)

    def __init__(self, shelf_script_row, parent=None):
        super(shelf_script_button, self).__init__(parent)

        self.timer=QtCore.QTimer(self)
        self.w=QtWidgets.QWidget()

        self.edit_mode = False

        self.shelf_script_row = shelf_script_row
        self.setFixedSize(20, 20)
        self.setObjectName('shelf_script_button')
        gui_utils.application_tooltip(self, '')
        self.connect_functions()
        self.refresh()

    def toggle_edit_mode(self, state):
        self.edit_mode = state
        self.setCheckable(state)
        self.setStyleSheet('')

    def update(self, shelf_script_row):
        self.shelf_script_row = shelf_script_row
        self.refresh()

    def refresh(self):
        self.setIcon(QtGui.QIcon(self.shelf_script_row['icon']))
        gui_utils.modify_application_tooltip(self, self.shelf_script_row['name'])

    def connect_functions(self):
        self.timer.timeout.connect(self.show_details)

    def execute(self):
        self.exec_signal.emit(self.shelf_script_row['id'])

    def show_details(self):
        self.help_signal.emit(self.shelf_script_row['id'])
        self.timer.stop()

    def enterEvent(self, event):
        if not self.edit_mode:
            self.timer.start(500)

    def leaveEvent(self, event):
        if not self.edit_mode:
            self.hide_help_signal.emit(self.shelf_script_row['id'])
            self.timer.stop()

    def mousePressEvent(self, event):
        event.accept()
        if not self.edit_mode:
            self.hide_help_signal.emit(self.shelf_script_row['id'])
            if event.button() == QtCore.Qt.LeftButton:
                self.setStyleSheet('background-color:#1d1d21;')
            self.timer.stop()
        else:
            if event.button() == QtCore.Qt.LeftButton:
                self.setStyleSheet('background-color:#1d1d21;')

    def mouseReleaseEvent(self, event):
        event.accept()
        if not self.edit_mode:
            self.setStyleSheet('')
            if event.button() == QtCore.Qt.RightButton:
                self.custom_menu()
            elif event.button() == QtCore.Qt.LeftButton:
                self.execute()
        else:
            if event.button() == QtCore.Qt.LeftButton:
                if self.isChecked():
                    self.setStyleSheet('')
                    self.setChecked(False)
                else:
                    self.setStyleSheet('border:1px solid #f79360;')
                    self.setChecked(True)


    def custom_menu(self):
        if not self.edit_mode:
            menu = gui_utils.QMenu()
            edit_action = menu.addAction(QtGui.QIcon(ressources._tool_edit_), 'Edit')
            delete_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Delete')
            action = menu.exec_(QtGui.QCursor().pos())
            if action == edit_action:
                self.edit_signal.emit(self.shelf_script_row['id'])
            elif action == delete_action:
                self.delete_signal.emit(self.shelf_script_row['id'])
