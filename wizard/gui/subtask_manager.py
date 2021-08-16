# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
import time
import json
import os

# Wizard gui modules
from wizard.gui import custom_window
from wizard.gui import logging_widget

# Wizard modules
from wizard.core import socket_utils
from wizard.core import tools
from wizard.vars import ressources
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

_DNS_ = ('localhost', 10231)

class subtask_manager(custom_window.custom_window):
    def __init__(self, parent = None):
        super(subtask_manager, self).__init__(parent)
        self.tasks_ids = dict()

        self.add_title('Subtasks manager')
        self.build_ui()

        self.tasks_server = tasks_server()
        self.tasks_server.start()

        self.connect_functions()

    def connect_functions(self):
        self.tasks_server.signal.connect(self.analyse_signal)

    def build_ui(self):
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(1)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.tasks_scrollArea = QtWidgets.QScrollArea()
        self.tasks_scrollBar = self.tasks_scrollArea.verticalScrollBar()

        self.tasks_scrollArea_widget = QtWidgets.QWidget()
        self.tasks_scrollArea_widget.setObjectName('wall_scroll_area')
        self.tasks_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.tasks_scrollArea_layout.setContentsMargins(3,3,3,3)
        self.tasks_scrollArea_layout.setSpacing(3)
        self.tasks_scrollArea_widget.setLayout(self.tasks_scrollArea_layout)

        self.tasks_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tasks_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tasks_scrollArea.setWidgetResizable(True)
        self.tasks_scrollArea.setWidget(self.tasks_scrollArea_widget)

        self.tasks_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.main_layout.addWidget(self.tasks_scrollArea)

    def analyse_signal(self, signal_list):
        process_id = signal_list[0]
        data_type = signal_list[1]
        data = signal_list[2]

        if process_id not in self.tasks_ids.keys():
            task_widget = subtask_widget()
            self.tasks_ids[process_id] = task_widget
            self.tasks_scrollArea_layout.addWidget(task_widget)

        if data_type == 'time':
            self.tasks_ids[process_id].update_time(data)
        elif data_type == 'percent':
            self.tasks_ids[process_id].update_progress(data)
        elif data_type == 'stdout':
            self.tasks_ids[process_id].analyse_stdout(data)
        elif data_type == 'current_task':
            self.tasks_ids[process_id].update_current_task(data)
        elif data_type == 'status':
            self.tasks_ids[process_id].update_status(data)

class subtask_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        
        super(subtask_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.current_task_data_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.current_task_data_label)

        self.stdout_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.stdout_label)

        self.progress = QtWidgets.QProgressBar()
        #self.progress.setTextVisible(0)
        self.progress.setMaximumHeight(6)
        self.progress.setObjectName('task_progressBar')
        self.progress.setStyleSheet('#task_progressBar{color:transparent;}')
        #self.progress.setAlignment(QtCore.Qt.AlignRight)
        self.main_layout.addWidget(self.progress)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('transparent_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(3)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.time_label = QtWidgets.QLabel('Duration :')
        self.time_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.time_label)
        self.time_data_label = QtWidgets.QLabel('00:00:00')
        self.infos_layout.addWidget(self.time_data_label)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.status_data_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.status_data_label)

        self.kill_button = QtWidgets.QPushButton()
        self.kill_button.setFixedSize(16,16)
        self.kill_button.setIconSize(QtCore.QSize(14,14))
        self.kill_button.setIcon(QtGui.QIcon(ressources._kill_task_icon_))
        self.infos_layout.addWidget(self.kill_button)

        self.restart_button = QtWidgets.QPushButton()
        self.restart_button.setFixedSize(16,16)
        self.restart_button.setIconSize(QtCore.QSize(14,14))
        self.restart_button.setIcon(QtGui.QIcon(ressources._refresh_icon_))
        self.infos_layout.addWidget(self.restart_button)

    def update_current_task(self, task):
        self.current_task_data_label.setText(task)

    def update_time(self, seconds):
        hours, minutes, seconds = tools.convert_seconds(seconds)
        self.time_data_label.setText(f"{hours}:{minutes}:{seconds}")

    def update_status(self, status):
        if status == 'Running':
            color = '#f79360'
        elif status == 'Killed':
            color = '#f0605b'
        elif status == 'Done':
            color = '#9cf277'
        self.status_data_label.setText(status)
        self.status_data_label.setStyleSheet(f"color:{color};")
        self.progress.setStyleSheet('#task_progressBar{color:transparent;}\n#task_progressBar::chunk{background-color:%s;}'%color)

    def update_progress(self, percent):
        self.progress.setValue(percent)

    def connect_functions(self):
        pass
        #self.kill_button.clicked.connect(self.subtask_thread.kill)
        #self.restart_button.clicked.connect(self.restart)

    def analyse_stdout(self, stdout):
        color = "gray"
        if 'INFO' in stdout:
            color = "#90d1f0"
        elif 'WARNI' in stdout:
            color = "#f79360"
        elif 'CRITI' in stdout or 'ERRO' in stdout:
            color = "#f0605b"
        self.stdout_label.setStyleSheet(f"color:{color};")
        self.stdout_label.setText(stdout)

class tasks_server(QThread):

    signal = pyqtSignal(object)

    def __init__(self):
        super(tasks_server, self).__init__()
        self.server, self.server_address = socket_utils.get_server(_DNS_)
        self.running = True

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = conn.recv(2048).decode('utf8')
                    if signal_as_str:
                        self.analyse_signal(signal_as_str, conn)
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def stop(self):
        self.running = False

    def analyse_signal(self, signal_as_str, conn):
        signal_list = json.loads(signal_as_str)
        self.signal.emit(signal_list)
