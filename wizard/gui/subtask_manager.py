# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
import time
import json
import os
import traceback

# Wizard gui modules
from wizard.gui import custom_window
from wizard.gui import logging_widget
from wizard.gui import log_viewer
from wizard.gui import gui_utils

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
        self.refresh()

    def connect_functions(self):
        self.tasks_server.new_process.connect(self.add_task)

    def build_ui(self):
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(1)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

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

    def add_task(self, data_tuple):
        conn = data_tuple[0]
        process_id = data_tuple[1]
        if process_id not in self.tasks_ids.keys():
            task_widget = subtask_widget(conn, process_id)
            self.tasks_ids[process_id] = task_widget
            self.tasks_ids[process_id].remove_task_signal.connect(self.remove_task)
            self.tasks_scrollArea_layout.addWidget(task_widget)
            self.refresh()

    def remove_task(self, process_id):
        if process_id in self.tasks_ids.keys():
            del self.tasks_ids[process_id]
            self.refresh()

    def refresh(self):
        if len(self.tasks_ids) == 0:
            self.tasks_scrollArea.setVisible(0)
            self.info_widget.setVisible(1)
            self.info_widget.setText("No current subtask...")
            self.info_widget.setImage(ressources._chill_info_image_)
        else:
            self.info_widget.setVisible(0)
            self.tasks_scrollArea.setVisible(1)

class subtask_widget(QtWidgets.QFrame):

    remove_task_signal = pyqtSignal(str)

    def __init__(self, conn, process_id, parent=None):
        super(subtask_widget, self).__init__(parent)

        self.conn = conn
        self.process_id = process_id
        self.log_file = None

        self.build_ui()
        self.update_thread_status(self.process_id)

        self.task_thread = task_thread(self.conn)
        self.task_thread.start()

        self.start_clock()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(2)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.thread_status_label = QtWidgets.QLabel()
        self.thread_status_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.thread_status_label.setObjectName('gray_label')
        self.header_layout.addWidget(self.thread_status_label)

        self.current_task_data_label = QtWidgets.QLabel()
        self.header_layout.addWidget(self.current_task_data_label)

        self.show_log_viewer_button = QtWidgets.QPushButton()
        self.show_log_viewer_button.setFixedSize(16, 16)
        self.show_log_viewer_button.setIconSize(QtCore.QSize(10,10))
        self.show_log_viewer_button.setIcon(QtGui.QIcon(ressources._console_icon_))
        self.header_layout.addWidget(self.show_log_viewer_button)

        self.delete_task_button = QtWidgets.QPushButton()
        self.delete_task_button.setFixedSize(16, 16)
        self.delete_task_button.setIconSize(QtCore.QSize(10,10))
        self.delete_task_button.setIcon(QtGui.QIcon(ressources._quit_decoration_))
        self.header_layout.addWidget(self.delete_task_button)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setMaximumHeight(6)
        self.progress.setObjectName('task_progressBar')
        self.progress.setStyleSheet('#task_progressBar{color:transparent;}')
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

    def start_clock(self):
        self.clock_thread = clock_thread(self)
        self.clock_thread.time_signal.connect(self.update_time)
        self.clock_thread.start()

    def show_log_viewer(self):
        self.log_viewer = log_viewer.log_viewer(self.log_file, parent = self)
        self.log_viewer.show()

    def update_current_task(self, task):
        self.current_task_data_label.setText(task)
        self.current_task = task

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

    def update_thread_status(self, status):
        self.thread_status_label.setText(f"{status} - ")

    def connect_functions(self):
        self.task_thread.signal.connect(self.analyse_signal)
        self.task_thread.connection_dead.connect(lambda:self.update_thread_status('Task closed'))
        self.task_thread.connection_dead.connect(self.clock_thread.stop)
        self.kill_button.clicked.connect(self.task_thread.kill)
        self.delete_task_button.clicked.connect(self.delete_task)
        self.show_log_viewer_button.clicked.connect(self.show_log_viewer)

    def delete_task(self):
        if self.task_thread.conn is not None:
            logger.warning('You need to kill the task before removing it')
        else:
            self.remove_task_signal.emit(self.process_id)
            self.setParent(None)
            self.deleteLater()

    def analyse_signal(self, signal_list):
        process_id = signal_list[0]
        data_type = signal_list[1]
        data = signal_list[2]

        if data_type == 'percent':
            self.update_progress(data)
        elif data_type == 'current_task':
            self.update_current_task(data)
        elif data_type == 'status':
            self.update_status(data)
        elif data_type == 'log_file':
            self.log_file = data
        elif data_type == 'end':
            self.task_thread.stop()

class clock_thread(QThread):

    time_signal = pyqtSignal(float)

    def __init__(self, parent = None):
        super(clock_thread, self).__init__(parent)
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        start_time = time.time()
        while self.running:
            time.sleep(1)
            self.time_signal.emit(time.time()-start_time)


class tasks_server(QThread):

    new_process = pyqtSignal(object)

    def __init__(self):
        super(tasks_server, self).__init__()
        self.server, self.server_address = socket_utils.get_server(_DNS_)
        self.running = True

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    process_id = json.loads(socket_utils.recvall(conn))
                    self.new_process.emit((conn, process_id))
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def stop(self):
        self.running = False

class task_thread(QThread):

    signal = pyqtSignal(object)
    connection_dead = pyqtSignal(int)

    def __init__(self, conn):
        super(task_thread, self).__init__()
        self.conn = conn
        self.running = True

    def run(self):
        while self.running and self.conn is not None:
            try:
                raw_data = socket_utils.recvall(self.conn)
                if raw_data is not None:
                    self.analyse_signal(raw_data)
                else:
                    if self.conn is not None:
                        self.conn.close()
                        self.conn = None
                        self.connection_dead.emit(1)
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def kill(self):
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, 'kill'):
                if self.conn is not None:
                    self.conn.close()
                    self.conn = None
                    self.connection_dead.emit(1)

    def stop(self):
        self.running = False
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.connection_dead.emit(1)

    def analyse_signal(self, raw_data):
        try:
            data = json.loads(raw_data)
            self.signal.emit(data)
        except json.decoder.JSONDecodeError:
            logger.debug("cannot read json data")