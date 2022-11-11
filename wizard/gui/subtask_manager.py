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
import logging

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import submit_log_widget

# Wizard modules
from wizard.core import socket_utils
from wizard.core import environment
from wizard.core import tools
from wizard.core import path_utils
from wizard.vars import ressources

logger = logging.getLogger(__name__)

_DNS_ = ('localhost', 10231)

class subtask_manager(QtWidgets.QWidget):

    global_status_signal = pyqtSignal(object)

    def __init__(self, parent = None):
        super(subtask_manager, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Subtasks manager")

        self.tasks_ids = dict()

        self.build_ui()

        self.timer=QtCore.QTimer(self)
        self.timer.start(1000)

        self.tasks_server = tasks_server()
        self.tasks_server.start()

        self.connect_functions()
        self.refresh()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()

    def connect_functions(self):
        self.tasks_server.new_process.connect(self.add_task)
        self.timer.timeout.connect(self.update_time)
        self.list_view.itemSelectionChanged.connect(self.refresh_stdout_viewer)
        self.stdout_viewer.verticalScrollBar().rangeChanged.connect(lambda: self.stdout_viewer.verticalScrollBar().setValue(self.stdout_viewer.verticalScrollBar().maximum()))
        self.list_view.customContextMenuRequested.connect(self.context_menu_requested)

    def build_ui(self):
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(1)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.info_widget = gui_utils.info_widget(transparent=1)
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setAnimated(1)
        self.list_view.setExpandsOnDoubleClick(1)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(6)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setHeaderLabels(['Task ID', 'Process status', 'Elapsed time', 'Status', 'Current task', 'Progress'])
        self.list_view.header().resizeSection(0, 350)
        self.list_view.header().resizeSection(4, 550)
        self.list_view.header().resizeSection(5, 400)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.main_layout.addWidget(self.list_view)

        self.stdout_viewer = QtWidgets.QTextEdit()
        self.stdout_viewer.setObjectName('console_textEdit')
        self.stdout_viewer.setReadOnly(True)
        self.stdout_viewer.setVisible(0)
        self.main_layout.addWidget(self.stdout_viewer)
    
    def add_task(self, data_tuple):
        conn = data_tuple[0]
        process_id = data_tuple[1]
        if process_id not in self.tasks_ids.keys():
            self.tasks_ids[process_id] = dict()
            self.tasks_ids[process_id]['thread'] = task_thread(process_id, conn)
            self.tasks_ids[process_id]['thread'].signal.connect(self.analyse_task_signal)
            self.tasks_ids[process_id]['thread'].connection_dead.connect(self.task_connection_dead)
            self.tasks_ids[process_id]['item'] = subtask_tree_item(process_id, self.list_view.invisibleRootItem())
            self.tasks_ids[process_id]['thread'].start()
            gui_server.custom_popup('Subtask started !', 'Open the subtask manager to see details', ressources._tasks_icon_)
            self.refresh()
            self.check_global_status()

    def remove_tasks(self):
        selection = self.list_view.selectedItems()
        for selected_item in selection:
            self.remove_task(selected_item.process_id)

    def kill_tasks(self):
        selection = self.list_view.selectedItems()
        for selected_item in selection:
            self.kill_task(selected_item.process_id)

    def remove_task(self, process_id):
        if process_id not in self.tasks_ids.keys():
            return
        if self.tasks_ids[process_id]['thread'].running:
            logger.warning(f"Can't remove openned task ({process_id}), kill it first")
            return
        task_item = self.tasks_ids[process_id]['item']
        self.list_view.invisibleRootItem().removeChild(task_item)
        del self.tasks_ids[process_id]
        self.refresh()
        self.check_global_status()

    def kill_task(self, process_id):
        if process_id not in self.tasks_ids.keys():
            return
        self.tasks_ids[process_id]['thread'].kill()

    def send_to_support(self):
        selection = self.list_view.selectedItems()
        if len(selection) != 1:
            return
        process_id = selection[0].process_id
        if process_id not in self.tasks_ids.keys():
            return
        log_file = self.tasks_ids[process_id]['thread'].log_file
        if not log_file:
            logger.warning("Log file is available only when task is closed")
            return
        if not path_utils.isfile(log_file):
            logger.warning(f"{log_file} not found")
            return
        with open(log_file, 'r') as f:
            data = f.read()
        self.submit_log_widget = submit_log_widget.submit_log_widget(data, 'subtask')
        self.submit_log_widget.show()

    def refresh(self):
        if len(self.tasks_ids) == 0:
            self.list_view.setVisible(0)
            self.info_widget.setVisible(1)
            self.info_widget.setText("No current subtask...")
            self.info_widget.setImage(ressources._nothing_info_)
        else:
            self.info_widget.setVisible(0)
            self.list_view.setVisible(1)

    def analyse_task_signal(self, data_tuple):
        process_id = data_tuple[0]
        signal_type = data_tuple[1]
        data = data_tuple[2]
        if process_id not in self.tasks_ids.keys():
            return
        if signal_type == 'percent':
            self.tasks_ids[process_id]['item'].update_progress(data)
        elif signal_type == 'current_task':
            self.tasks_ids[process_id]['item'].update_current_task(data)
        elif signal_type == 'status':
            self.tasks_ids[process_id]['item'].update_status(data)
        elif signal_type == 'end':
            self.tasks_ids[process_id]['thread'].stop()
        elif signal_type == 'stdout':
            self.append_to_stdout_viewer(process_id, data)

    def refresh_stdout_viewer(self):
        selection = self.list_view.selectedItems()
        self.stdout_viewer.clear()
        if len(selection) != 1:
            self.stdout_viewer.setVisible(0)
            return
        self.stdout_viewer.setVisible(1)
        process_id = selection[0].process_id
        stdout = self.tasks_ids[process_id]['thread'].stdout
        self.append_to_stdout_viewer(process_id, stdout)

    def append_to_stdout_viewer(self, process_id, stdout):
        selection = self.list_view.selectedItems()
        if len(selection) != 1:
            return
        if selection[0].process_id != process_id:
            return
        self.stdout_viewer.insertHtml(stdout)

    def update_time(self):
        for process_id in self.tasks_ids.keys():
            if not self.tasks_ids[process_id]['thread'].running:
                continue
            self.tasks_ids[process_id]['item'].update_time()

    def task_connection_dead(self, process_id):
        if process_id not in self.tasks_ids.keys():
            return
        self.tasks_ids[process_id]['item'].update_process_status('closed')

    def check_global_status(self):
        status = None
        for task_id in self.tasks_ids.keys():
            if self.tasks_ids[task_id]['thread'].running:
                status = 'process'
                break
            else:
                status = 'done'
        self.global_status_signal.emit(status)

    def context_menu_requested(self):
        menu = gui_utils.QMenu(self)
        selection = self.list_view.selectedItems()
        kill_action = None
        remove_action = None
        submit_log_action = None
        if len(selection)>=1:
            kill_action = menu.addAction(QtGui.QIcon(ressources._kill_task_icon_), 'Kill selected task(s)')
            remove_action = menu.addAction(QtGui.QIcon(ressources._archive_icon_), 'Remove selected task(s)')
        if len(selection) == 1:
            submit_log_action = menu.addAction(QtGui.QIcon(ressources._send_icon_), 'Submit to support')
        pos = QtGui.QCursor().pos()
        action = menu.exec_(pos)
        if action is None:
            return
        if action == kill_action:
            self.kill_tasks()
        elif action == remove_action:
            self.remove_tasks()
        elif action == submit_log_action:
            self.send_to_support()

class subtask_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, process_id, parent=None):
        super(subtask_tree_item, self).__init__(parent)
        self.process_id = process_id
        self.elapsed = 0
        self.fill_ui()

    def fill_ui(self):
        self.progress_widget = QtWidgets.QWidget()
        self.progress_widget.setObjectName('transparent_widget')
        self.progress_layout = QtWidgets.QVBoxLayout()
        self.progress_layout.setContentsMargins(6,6,6,6)
        self.progress_widget.setLayout(self.progress_layout)
        self.progress = QtWidgets.QProgressBar()
        #self.progress.setMaximumHeight(6)
        self.progress.setObjectName('task_progressBar')
        self.progress.setStyleSheet('#task_progressBar{color:transparent;}')
        self.progress_layout.addWidget(self.progress)
        self.treeWidget().setItemWidget(self, 5, self.progress_widget)

        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(3, bold_font)
        self.setText(0, self.process_id)
        self.update_time()
        self.update_process_status('open')
        self.setForeground(0, QtGui.QBrush(QtGui.QColor('gray')))
        self.setForeground(1, QtGui.QBrush(QtGui.QColor('gray')))

    def update_process_status(self, process_status):
        self.setText(1, process_status)
        if process_status == 'closed':
            self.progress.setStyleSheet('#task_progressBar{color:transparent;}\n#task_progressBar::chunk{background-color:gray;}')
            self.setForeground(2, QtGui.QBrush(QtGui.QColor('gray')))
            self.setForeground(4, QtGui.QBrush(QtGui.QColor('gray')))

    def update_time(self):
        self.elapsed += 1
        hours, minutes, seconds = tools.convert_seconds(self.elapsed)
        self.setText(2, f"{hours}:{minutes}:{seconds}")

    def update_status(self, status):
        if status == 'Running':
            color = '#f79360'
        elif status == 'Killed':
            color = '#f0605b'
        elif status == 'Done':
            self.update_progress(100)
            color = '#9cf277'
        self.setText(3, status)
        self.setForeground(3, QtGui.QBrush(QtGui.QColor(color)))

    def update_current_task(self, current_task):
        self.setText(4, current_task)

    def update_progress(self, progress):
        self.progress.setValue(int(progress))

class tasks_server(QThread):

    new_process = pyqtSignal(object)

    def __init__(self):
        super(tasks_server, self).__init__()
        self.port = socket_utils.get_port('localhost')
        environment.set_subtasks_server_port(self.port)
        self.server, self.server_address = socket_utils.get_server(('localhost', self.port))
        self.running = True

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = socket_utils.recvall(conn)
                    if signal_as_str:
                        process_id = json.loads(signal_as_str)
                        self.new_process.emit((conn, process_id))
            except OSError:
                pass
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def stop(self):
        self.server.close()
        self.running = False

class task_thread(QThread):

    signal = pyqtSignal(object)
    connection_dead = pyqtSignal(str)

    def __init__(self, process_id, conn):
        super(task_thread, self).__init__()
        self.stdout = ''
        self.log_file = None
        self.process_id = process_id
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
                        self.connection_dead.emit(self.process_id)
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def kill(self):
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, 'kill'):
                if self.conn is not None:
                    self.conn.close()
                    self.conn = None
                    self.connection_dead.emit(self.process_id)

    def get_stdout(self):
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, 'get_stdout'):
                if self.conn is not None:
                    self.conn.close()
                    self.conn = None
                    self.connection_dead.emit(self.process_id)

    def stop(self):
        self.running = False
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.connection_dead.emit(self.process_id)

    def analyse_signal(self, raw_data):
        try:
            data = json.loads(raw_data)
            if data[1] == 'stdout':
                self.analyse_stdout(data[2])
            elif data[1] == 'log_file':
                self.log_file = data[2]
            else:
                self.signal.emit(data)
        except json.decoder.JSONDecodeError:
            logger.debug("cannot read json data")

    def analyse_stdout(self, stdout):
        new_lines = ''
        if stdout.startswith('\n'):
            stdout = stdout[1:]
        for line in stdout.split('\n'):
            if 'INFO' in line:
                line = f'<span style="color:#90d1f0;">{line}'
            elif 'WARNI' in line:
                line = f'<strong><span style="color:#f79360;">{line}</strong>'
            elif 'CRITI' in line or 'ERRO' in line:
                line = f'<strong><span style="color:#f0605b;">{line}</strong>'
            self.stdout += line+'<br>'
            new_lines += line+'<br>'
        self.signal.emit([self.process_id, 'stdout', new_lines])

        
