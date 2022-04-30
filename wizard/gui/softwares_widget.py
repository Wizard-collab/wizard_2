# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
import time

# Wizard modules
from wizard.core import environment
from wizard.core import site
from wizard.core import launch
from wizard.core import image
from wizard.core import assets
from wizard.core import project
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

class softwares_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(softwares_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ToolTip)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.work_env_ids = dict()
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.kill_all_button.clicked.connect(self.kill_all)

    def leaveEvent(self, event):
        self.hide()

    def build_ui(self):
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)

        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.main_widget_layout)

        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setObjectName('round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.main_widget_layout.addWidget(self.main_widget)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 190))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.main_widget.setGraphicsEffect(self.shadow)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('dark_widget')
        self.header_widget.setStyleSheet('#dark_widget{border-top-left-radius:8px;border-top-right-radius:8px;}')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(10,10,10,10)
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)

        self.title = QtWidgets.QLabel('Running work environments')
        self.header_layout.addWidget(self.title)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.kill_all_button = QtWidgets.QPushButton('Kill all')
        self.kill_all_button.setStyleSheet('padding:3px;')
        self.kill_all_button.setIcon(QtGui.QIcon(ressources._kill_task_icon_))
        self.header_layout.addWidget(self.kill_all_button)

        self.main_layout.addWidget(self.header_widget)

        self.info_widget = gui_utils.info_widget(transparent=1)
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.work_envs_scrollArea = QtWidgets.QScrollArea()
        self.work_envs_scrollArea.setObjectName('transparent_widget')
        self.work_envs_scrollBar = self.work_envs_scrollArea.verticalScrollBar()

        self.work_envs_scrollArea_widget = QtWidgets.QWidget()
        self.work_envs_scrollArea_widget.setObjectName('transparent_widget')
        self.work_envs_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.work_envs_scrollArea_layout.setContentsMargins(10,10,10,10)
        self.work_envs_scrollArea_layout.setSpacing(3)
        self.work_envs_scrollArea_widget.setLayout(self.work_envs_scrollArea_layout)

        self.work_envs_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.work_envs_scrollArea.setWidgetResizable(True)
        self.work_envs_scrollArea.setWidget(self.work_envs_scrollArea_widget)

        self.work_envs_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.main_layout.addWidget(self.work_envs_scrollArea)

    def refresh(self):
        running_work_env_ids = launch.get()
        for work_env_id in running_work_env_ids:
            if work_env_id not in self.work_env_ids.keys():
                widget = work_env_widget(work_env_id, self)
                self.work_envs_scrollArea_layout.addWidget(widget)
                self.work_env_ids[work_env_id] = widget
        work_env_id_list = list(self.work_env_ids.keys())
        for work_env_id in work_env_id_list:
            if work_env_id not in running_work_env_ids:
                self.remove_work_env(work_env_id)
        self.refresh_info_widget()

    def kill_all(self):
        launch.kill_all()
        gui_server.refresh_team_ui()

    def remove_work_env(self, work_env_id):
        if work_env_id in self.work_env_ids.keys():
            self.work_env_ids[work_env_id].setParent(None)
            self.work_env_ids[work_env_id].deleteLater()
            del self.work_env_ids[work_env_id]

    def refresh_info_widget(self):
        if len(self.work_env_ids) == 0:
            self.work_envs_scrollArea.setVisible(0)
            self.info_widget.setVisible(1)
            self.info_widget.setText("You need to get to work !")
            self.info_widget.setImage(ressources._nothing_info_)
        else:
            self.info_widget.setVisible(0)
            self.work_envs_scrollArea.setVisible(1)

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
                gui_utils.move_ui(self)
            else:
                self.hide()
        else:
            self.show()
            self.raise_()
            gui_utils.move_ui(self)

class work_env_widget(QtWidgets.QFrame):
    def __init__(self, work_env_id, parent=None):
        super(work_env_widget, self).__init__(parent)
        self.work_env_id = work_env_id
        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def fill_ui(self):
        work_env_row = project.get_work_env_data(self.work_env_id)
        software = project.get_software_data(work_env_row['software_id'], 'name')
        icon = ressources._sofwares_icons_dic_[software]
        self.software_icon.setPixmap(QtGui.QIcon(icon).pixmap(26))
        work_env_label = assets.instance_to_string(('work_env', self.work_env_id))
        self.work_env_label.setText(work_env_label)

    def connect_functions(self):
        self.kill_button.clicked.connect(self.kill)

    def kill(self):
        launch.kill(self.work_env_id)
        gui_server.refresh_team_ui()

    def build_ui(self):
        self.setObjectName('item_widget_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.software_icon = QtWidgets.QLabel()
        self.software_icon.setFixedSize(26,26)
        self.main_layout.addWidget(self.software_icon)

        self.work_env_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.work_env_label)

        self.kill_button = QtWidgets.QPushButton()
        self.kill_button.setFixedSize(26,26)
        self.kill_button.setIcon(QtGui.QIcon(ressources._kill_task_icon_))
        gui_utils.application_tooltip(self.kill_button, "Kill work env software instance")
        self.main_layout.addWidget(self.kill_button)