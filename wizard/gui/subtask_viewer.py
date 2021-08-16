# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import time
import os

# Wizard gui modules
from wizard.gui import custom_window
from wizard.gui import logging_widget

# Wizard modules
from wizard.core import subtask
from wizard.core import tools
from wizard.vars import ressources
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class subtask_manager(custom_window.custom_window):
    def __init__(self, parent=None):
        super(subtask_manager, self).__init__(parent)

        self.logging_widget = logging_widget.logging_widget()
        self.subtask_thread = subtask.subtask_thread()

        self.add_title('Subtask manager')
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.cwd_lineEdit = QtWidgets.QLineEdit()
        self.cwd_lineEdit.setPlaceholderText('Work directory')
        self.main_layout.addWidget(self.cwd_lineEdit)

        self.env_textEdit = QtWidgets.QTextEdit()
        self.env_textEdit.setMaximumHeight(100)
        self.env_textEdit.setPlaceholderText('Environment')
        self.main_layout.addWidget(self.env_textEdit)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('transparent_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.command_lineEdit = QtWidgets.QLineEdit()
        self.command_lineEdit.setPlaceholderText('Your command here')
        self.header_layout.addWidget(self.command_lineEdit)

        self.run_button = QtWidgets.QPushButton()
        self.run_button.setFixedSize(26,26)
        self.run_button.setIcon(QtGui.QIcon(ressources._play_icon_))
        self.header_layout.addWidget(self.run_button)

        self.stdout_textEdit = QtWidgets.QTextEdit()
        self.stdout_textEdit.setObjectName('console_textEdit')
        self.stdout_textEdit.setReadOnly(True)
        self.stdout_textEdit_scrollBar = self.stdout_textEdit.verticalScrollBar()
        self.main_layout.addWidget(self.stdout_textEdit)

        self.stdin_widget = QtWidgets.QWidget()
        self.stdin_widget.setObjectName('transparent_widget')
        self.stdin_layout = QtWidgets.QHBoxLayout()
        self.stdin_layout.setContentsMargins(0,0,0,0)
        self.stdin_layout.setSpacing(6)
        self.stdin_widget.setLayout(self.stdin_layout)
        self.main_layout.addWidget(self.stdin_widget)

        self.stdin_layout.addWidget(QtWidgets.QLabel('>>>'))

        self.stdin_lineEdit = QtWidgets.QLineEdit()
        self.stdin_lineEdit.setPlaceholderText('Stdin')
        self.stdin_layout.addWidget(self.stdin_lineEdit)

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

        self.restart_button = QtWidgets.QPushButton()
        self.restart_button.setFixedSize(20,20)
        self.restart_button.setIcon(QtGui.QIcon(ressources._refresh_icon_))
        self.infos_layout.addWidget(self.restart_button)
        
        self.main_layout.addWidget(self.logging_widget)

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

    def update_progress(self, percent):
        self.progress.setValue(percent)

    def write_stdin(self):
        stdin = self.stdin_lineEdit.text()
        self.subtask_thread.write(stdin)
        self.stdin_lineEdit.clear()

    def connect_functions(self):
        self.stdout_textEdit_scrollBar.rangeChanged.connect(lambda: self.stdout_textEdit_scrollBar.setValue(self.stdout_textEdit_scrollBar.maximum()))
        self.subtask_thread.stdout_signal.connect(self.analyse_stdout)
        self.subtask_thread.time_signal.connect(self.update_time)
        self.subtask_thread.status_signal.connect(self.update_status)
        self.subtask_thread.percent_signal.connect(self.update_progress)
        self.subtask_thread.current_task_signal.connect(self.current_task_data_label.setText)
        self.kill_button.clicked.connect(self.subtask_thread.kill)
        self.restart_button.clicked.connect(self.restart)
        self.run_button.clicked.connect(self.start)
        self.command_lineEdit.returnPressed.connect(self.start)
        self.stdin_lineEdit.returnPressed.connect(self.write_stdin)

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
        self.command_lineEdit.setText(command)

    def set_cwd(self, cwd):
        self.cwd_lineEdit.setText(cwd)

    def set_env(self, env):
        if env is not None:
            for key in env.keys():
                line = f"{key}={env[key]}\n"
                self.env_textEdit.append(line)

    def get_env(self):
        raw_text = self.env_textEdit.toPlainText()
        print(raw_text)
        if raw_text != '':
            env = dict()
            lines = raw_text.split('\n')
            if lines[0] == 'COPY':
                env = os.environ.copy()
                lines.pop(0) 
            for line in lines:
                key = line.split('=')[0]
                data = line.split('=')[-1]
                if key not in env.keys():
                    env[key] = data
                else:
                    env[key] += data
        else:
            env = None
        return env

    def get_cwd(self):
        raw_text = self.cwd_lineEdit.text()
        if raw_text != '':
            cwd = os.path.normpath(raw_text)
        else:
            cwd = None
        return cwd

    def start(self):

        if self.subtask_thread.running == True:
            logger.warning('A task is already running')
        else:
            command = self.command_lineEdit.text()
            cwd = self.get_cwd()
            env = self.get_env()

            self.subtask_thread.set_command(command)
            self.subtask_thread.set_env(env)
            self.subtask_thread.set_cwd(cwd)
            self.subtask_thread.start()

    def restart(self):
        self.subtask_thread.kill()
        time.sleep(1)
        self.subtask_thread.start()

    def closeEvent(self, event):
        self.subtask_thread.kill()
