# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time
import psutil
import logging

# Wizard modules
from wizard.core import user
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import logging_widget

logger = logging.getLogger(__name__)

class footer_widget(QtWidgets.QFrame):

    show_console = pyqtSignal(int)
    show_wall = pyqtSignal(int)
    show_subtask_manager = pyqtSignal(int)
    show_production_manager = pyqtSignal(int)
    connect_team = pyqtSignal(int)
    show_team_widget = pyqtSignal(int)
    show_user_preferences = pyqtSignal(int)
    show_softwares_widget = pyqtSignal(int)
    show_locks_widget = pyqtSignal(int)
    refresh_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(footer_widget, self).__init__(parent)
        self.logging_widget = logging_widget.logging_widget()
        self.hardware_infos_widget = hardware_infos_widget()
        self.tooltip_widget = tooltip_widget()
        self.script_bar = script_bar()
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.script_bar)

        self.main_layout.addWidget(self.tooltip_widget)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(QtCore.QSize(22,22))
        self.icon_label.setPixmap(QtGui.QIcon(ressources._info_icon_).pixmap(22))
        self.main_layout.addWidget(self.icon_label)

        self.main_layout.addWidget(self.logging_widget)
        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(QtCore.QSize(22,22))
        self.icon_label.setPixmap(QtGui.QIcon(ressources._chip_icon_).pixmap(22))
        self.main_layout.addWidget(self.icon_label)

        self.main_layout.addWidget(self.hardware_infos_widget)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(12,0,0,0)
        self.buttons_layout.setSpacing(2)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setFixedWidth(130)
        self.refresh_label.setAlignment(QtCore.Qt.AlignCenter)
        self.refresh_label.setObjectName('gray_label')
        self.buttons_layout.addWidget(self.refresh_label)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(12,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        self.team_connection_button = QtWidgets.QPushButton()
        self.team_connection_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.team_connection_button, "Team connection status")
        self.team_connection_button.setIcon(QtGui.QIcon(ressources._team_connection_off_))
        self.buttons_layout.addWidget(self.team_connection_button)
        
        self.refresh_ui_button = QtWidgets.QPushButton()
        self.refresh_ui_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.refresh_ui_button, "Manually refresh the ui")
        self.refresh_ui_button.setIcon(QtGui.QIcon(ressources._refresh_icon_))
        self.buttons_layout.addWidget(self.refresh_ui_button)

        self.settings_button = QtWidgets.QPushButton()
        self.settings_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.settings_button, "Settings")
        self.settings_button.setIcon(QtGui.QIcon(ressources._settings_icon_))
        self.buttons_layout.addWidget(self.settings_button)
        
        self.locks_button = QtWidgets.QPushButton()
        self.locks_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.locks_button, "Show locked work environments")
        self.locks_button.setIcon(QtGui.QIcon(ressources._lock_icons_[1]))
        self.buttons_layout.addWidget(self.locks_button)

        self.softwares_button = QtWidgets.QPushButton()
        self.softwares_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.softwares_button, "Show running work environments")
        self.softwares_button.setIcon(QtGui.QIcon(ressources._running_softwares_icon_))
        self.buttons_layout.addWidget(self.softwares_button)

        self.task_manager_button = QtWidgets.QPushButton()
        self.task_manager_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.task_manager_button, "Show task manager")
        self.task_manager_button.setIcon(QtGui.QIcon(ressources._tasks_icon_))
        self.buttons_layout.addWidget(self.task_manager_button)

        self.production_manager_button = QtWidgets.QPushButton()
        self.production_manager_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.production_manager_button, "Show production manager")
        self.production_manager_button.setIcon(QtGui.QIcon(ressources._production_manager_icon_))
        self.buttons_layout.addWidget(self.production_manager_button)

        self.console_button = QtWidgets.QPushButton()
        self.console_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.console_button, "Show console")
        self.console_button.setIcon(QtGui.QIcon(ressources._console_icon_))
        self.buttons_layout.addWidget(self.console_button)

        self.wall_button = QtWidgets.QPushButton()
        self.wall_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.wall_button, "Show notification wall")
        self.wall_button.setIcon(QtGui.QIcon(ressources._wall_icon_))
        self.buttons_layout.addWidget(self.wall_button)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f"global refresh : {refresh_time}s")

    def set_team_connection(self, team_connection):
        if team_connection:
            self.team_connection_button.setIcon(QtGui.QIcon(ressources._team_connection_on_))
        else:
            self.team_connection_button.setIcon(QtGui.QIcon(ressources._team_connection_off_))

    def connect_functions(self):
        self.refresh_ui_button.clicked.connect(self.refresh_signal.emit)
        self.console_button.clicked.connect(self.show_console.emit)
        self.wall_button.clicked.connect(self.show_wall.emit)
        self.task_manager_button.clicked.connect(self.show_subtask_manager.emit)
        self.production_manager_button.clicked.connect(self.show_production_manager.emit)
        self.team_connection_button.clicked.connect(self.connect_team.emit)
        self.team_connection_button.clicked.connect(self.show_team_widget.emit)
        self.settings_button.clicked.connect(self.show_user_preferences.emit)
        self.softwares_button.clicked.connect(self.show_softwares_widget.emit)
        self.locks_button.clicked.connect(self.show_locks_widget.emit)

    def update_tooltip(self, tooltip):
        self.tooltip_widget.setText(tooltip)

    def handle_record(self, record_tuple):
        self.logging_widget.handle_record(record_tuple)

    def update_console_button(self, notification):
        if notification == 'warning':
            self.console_button.setIcon(QtGui.QIcon(ressources._console_warning_icon_))
        elif notification == 'error':
            self.console_button.setIcon(QtGui.QIcon(ressources._console_error_icon_))
        elif notification == 'info':
            self.console_button.setIcon(QtGui.QIcon(ressources._console_info_icon_))
        else:
            self.console_button.setIcon(QtGui.QIcon(ressources._console_icon_))

    def update_wall_button(self, notification):
        if notification:
            self.wall_button.setIcon(QtGui.QIcon(ressources._wall_notification_icon_))
        else:
            self.wall_button.setIcon(QtGui.QIcon(ressources._wall_icon_))

    def update_subtask_manager_button(self, status):
        if status == 'process':
            self.task_manager_button.setIcon(QtGui.QIcon(ressources._tasks_process_icon_))
        elif status == 'done':
            self.task_manager_button.setIcon(QtGui.QIcon(ressources._tasks_done_icon_))
        else:
            self.task_manager_button.setIcon(QtGui.QIcon(ressources._tasks_icon_))

class tooltip_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(tooltip_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setFixedWidth(200)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(QtCore.QSize(22,22))
        self.icon_label.setPixmap(QtGui.QIcon(ressources._bulb_icon_).pixmap(22))
        self.main_layout.addWidget(self.icon_label)

        self.main_label = gui_utils.ElidedLabel('Tooltips')
        gui_utils.application_tooltip(self.main_label, "Come here if you're lost")
        self.main_layout.addWidget(self.main_label)

    def setText(self, text):
        self.main_label.setText(text)

class script_bar(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(script_bar, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setFixedWidth(300)
        gui_utils.application_tooltip(self, "Python command line")

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(QtCore.QSize(22,22))
        self.icon_label.setPixmap(QtGui.QIcon(ressources._python_icon_).pixmap(22))
        self.main_layout.addWidget(self.icon_label)

        self.script_lineEdit = QtWidgets.QLineEdit()
        self.script_lineEdit.setPlaceholderText('Python commands')
        self.main_layout.addWidget(self.script_lineEdit)

    def connect_functions(self):
        self.script_lineEdit.returnPressed.connect(self.execute)

    def execute(self):
        data = self.script_lineEdit.selectedText()
        if data == '':
            data = self.script_lineEdit.text()
        user.user().execute_session(data)

class hardware_infos_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(hardware_infos_widget, self).__init__(parent)
        self.build_ui()
        self.timer=QtCore.QTimer(self)
        self.timer.start(3000)
        #self.hardware_thread = hardware_thread(self)
        self.connect_functions()

    def build_ui(self):
        gui_utils.application_tooltip(self, "Computer hardware informations")
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.cpu_label = QtWidgets.QLabel('Cpu')
        self.main_layout.addWidget(self.cpu_label)
        
        self.cpu_progressBar = gui_utils.RoundProgress()
        self.cpu_progressBar.set_line_width(6)
        self.cpu_progressBar.setValue(0)
        self.cpu_progressBar.setFixedSize(QtCore.QSize(25,25))
        self.main_layout.addWidget(self.cpu_progressBar)

        self.ram_label = QtWidgets.QLabel('Ram')
        self.main_layout.addWidget(self.ram_label)

        self.ram_progressBar = gui_utils.RoundProgress()
        self.ram_progressBar.set_line_width(6)
        self.ram_progressBar.setValue(0)
        self.ram_progressBar.setFixedSize(QtCore.QSize(25,25))
        self.main_layout.addWidget(self.ram_progressBar)

    def connect_functions(self):
        self.timer.timeout.connect(self.update_progress)

    def update_progress(self):
        ram = dict(psutil.virtual_memory()._asdict())['percent']
        cpu = psutil.cpu_percent()
        if 0<=int(cpu)<=33:
            color = '#d9d9d9'
        elif 33<int(cpu)<66:
            color = '#f79360'
        else:
            color = '#f0605b' 
        self.cpu_progressBar.setChunckColor(color)
        self.cpu_progressBar.setValue(cpu)

        if 0<=int(ram)<=56:
            color = '#d9d9d9'
        elif 56<int(ram)<86:
            color = '#f79360'
        else:
            color = '#f0605b' 
        self.ram_progressBar.setChunckColor(color)
        self.ram_progressBar.setValue(ram)
