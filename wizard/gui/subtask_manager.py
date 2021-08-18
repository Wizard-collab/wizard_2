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
        self.tasks_server.new_process.connect(self.add_task)

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

    def add_task(self, data_tuple):
        conn = data_tuple[0]
        process_id = data_tuple[1]
        if process_id not in self.tasks_ids.keys():
            task_widget = subtask_widget(conn, process_id)
            self.tasks_ids[process_id] = task_widget
            self.tasks_scrollArea_layout.addWidget(task_widget)

class subtask_widget(QtWidgets.QFrame):
    def __init__(self, conn, process_id, parent=None):
        super(subtask_widget, self).__init__(parent)

        self.conn = conn
        self.process_id = process_id

        self.stdout = ''
        self.percent = 0
        self.current_task = None
        self.status = None
        self.command = None
        self.last_time = 0

        self.subtask_viewer = None

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

        self.show_subtask_viewer_button = QtWidgets.QPushButton()
        self.show_subtask_viewer_button.setFixedSize(16, 16)
        self.show_subtask_viewer_button.setIconSize(QtCore.QSize(10,10))
        self.show_subtask_viewer_button.setIcon(QtGui.QIcon(ressources._console_icon_))
        self.header_layout.addWidget(self.show_subtask_viewer_button)

        self.delete_task_button = QtWidgets.QPushButton()
        self.delete_task_button.setFixedSize(16, 16)
        self.delete_task_button.setIconSize(QtCore.QSize(10,10))
        self.delete_task_button.setIcon(QtGui.QIcon(ressources._quit_decoration_))
        self.header_layout.addWidget(self.delete_task_button)

        self.stdout_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.stdout_label)

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

    def show_subtask_viewer(self):
        self.subtask_viewer = subtask_viewer(self)
        self.subtask_viewer.set_command(self.command)
        self.subtask_viewer.update_status(self.status)
        self.subtask_viewer.update_current_task(self.current_task)
        self.subtask_viewer.update_progress(self.percent)
        self.subtask_viewer.update_time(self.last_time)
        self.subtask_viewer.set_buffered_stdout(self.stdout)
        self.subtask_viewer.kill.connect(self.task_thread.kill)
        self.subtask_viewer.show()

    def update_current_task(self, task):
        self.current_task_data_label.setText(task)
        self.current_task = task
        if self.subtask_viewer is not None:
            self.subtask_viewer.update_current_task(task)

    def update_time(self, seconds):
        self.last_time = seconds
        if self.subtask_viewer is not None:
            self.subtask_viewer.update_time(seconds)

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
        self.status = status
        if self.subtask_viewer is not None:
            self.subtask_viewer.update_status(status)

    def update_progress(self, percent):
        self.progress.setValue(percent)
        self.percent = percent
        if self.subtask_viewer is not None:
            self.subtask_viewer.update_progress(percent)

    def update_thread_status(self, status):
        self.thread_status_label.setText(f"{status} - ")

    def connect_functions(self):
        self.task_thread.signal.connect(self.analyse_signal)
        self.task_thread.connection_dead.connect(lambda:self.update_thread_status('Task closed'))
        self.task_thread.connection_dead.connect(self.clock_thread.stop)
        self.kill_button.clicked.connect(self.task_thread.kill)
        self.delete_task_button.clicked.connect(self.delete_task)
        self.show_subtask_viewer_button.clicked.connect(self.show_subtask_viewer)

    def delete_task(self):
        if self.task_thread.conn is not None:
            logger.warning('You need to kill the task before removing it')
        else:
            self.setParent(None)
            self.deleteLater()

    def unbuffer_stdout(self, out):
        for line in out.split('\n'):
            self.stdout += f"{line}\n"
            if self.subtask_viewer is not None:
                self.subtask_viewer.analyse_stdout(line)

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
        self.stdout += f"{stdout}\n"
        if self.subtask_viewer is not None:
            self.subtask_viewer.analyse_stdout(stdout)

    def analyse_signal(self, signal_list):
        process_id = signal_list[0]
        data_type = signal_list[1]
        data = signal_list[2]

        if data_type == 'time':
            self.update_time(data)
        elif data_type == 'percent':
            self.update_progress(data)
        elif data_type == 'stdout':
            self.analyse_stdout(data)
        elif data_type == 'current_task':
            self.update_current_task(data)
        elif data_type == 'status':
            self.update_status(data)
        elif data_type == 'cmd':
            self.command = data
        elif data_type == 'buffered_stdout':
            self.unbuffer_stdout(data)
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

class subtask_viewer(custom_window.custom_window):

    kill = pyqtSignal(int)

    def __init__(self, parent=None):
        super(subtask_viewer, self).__init__(parent)

        self.add_title('Subtask viewer')
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.command_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.command_label)

        self.stdout_textEdit = QtWidgets.QTextEdit()
        self.stdout_textEdit.setObjectName('console_textEdit')
        self.stdout_textEdit.setReadOnly(True)
        self.stdout_textEdit_scrollBar = self.stdout_textEdit.verticalScrollBar()
        self.main_layout.addWidget(self.stdout_textEdit)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.progress)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('transparent_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(6)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.time_label = QtWidgets.QLabel('Duration :')
        self.time_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.time_label)
        self.time_data_label = QtWidgets.QLabel('00:00:00')
        self.infos_layout.addWidget(self.time_data_label)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(60, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.current_task_label = QtWidgets.QLabel('Current task :')
        self.current_task_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.current_task_label)
        self.current_task_data_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.current_task_data_label)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(60, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.status_label = QtWidgets.QLabel('Status :')
        self.status_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.status_label)
        self.status_data_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.status_data_label)

        self.kill_button = QtWidgets.QPushButton()
        self.kill_button.setFixedSize(20,20)
        self.kill_button.setIcon(QtGui.QIcon(ressources._kill_task_icon_))
        self.infos_layout.addWidget(self.kill_button)
        
    def update_time(self, seconds):
        hours, minutes, seconds = tools.convert_seconds(seconds)
        self.time_data_label.setText(f"{hours}:{minutes}:{seconds}")

    def update_current_task(self, task):
        self.current_task_data_label.setText(task)

    def update_status(self, status):
        if status == 'Running':
            color = '#f79360'
        elif status == 'Killed':
            color = '#f0605b'
        elif status == 'Done':
            color = '#9cf277'
        self.status_data_label.setText(status)
        self.status_data_label.setStyleSheet(f"color:{color};")

    def update_progress(self, percent):
        self.progress.setValue(percent)

    def connect_functions(self):
        self.stdout_textEdit_scrollBar.rangeChanged.connect(lambda: self.stdout_textEdit_scrollBar.setValue(self.stdout_textEdit_scrollBar.maximum()))
        self.kill_button.clicked.connect(self.kill.emit)

    def set_buffered_stdout(self, out):
        for line in out.split('\n'):
            self.analyse_stdout(line+'\n')
            print(line)

    def analyse_stdout(self, stdout):
        if 'INFO' in stdout:
            stdout = f'<span style="color:#90d1f0;">{stdout}'
        elif 'WARNI' in stdout:
            stdout = f'<strong><span style="color:#f79360;">{stdout}</strong>'
        elif 'CRITI' in stdout or 'ERRO' in stdout:
            stdout = f'<strong><span style="color:#f0605b;">{stdout}</strong>'
        self.stdout_textEdit.insertHtml(stdout)
        self.stdout_textEdit.insertHtml('<br>')

    def set_command(self, command):
        self.command_label.setText(command)

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