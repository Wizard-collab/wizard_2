# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from qroundprogressbar import QRoundProgressBar
import time
import psutil

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import logging_widget

class footer_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(footer_widget, self).__init__(parent)
        self.logging_widget = logging_widget.logging_widget()
        self.hardware_infos_widget = hardware_infos_widget()
        self.build_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.logging_widget)
        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        self.main_layout.addWidget(self.hardware_infos_widget)

class hardware_infos_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(hardware_infos_widget, self).__init__(parent)
        self.build_ui()
        self.hardware_thread = hardware_thread(self)
        self.connect_functions()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.cpu_label = QtWidgets.QLabel('Cpu')
        self.main_layout.addWidget(self.cpu_label)

        '''
        self.cpu_progressBar = QtWidgets.QProgressBar()
        self.cpu_progressBar.setTextVisible(0)
        '''
        
        self.cpu_progressBar = QRoundProgressBar()
        self.cpu_progressBar.setBarStyle(QRoundProgressBar.BarStyle.LINE)

        self.cpu_progressBar.setFixedSize(QtCore.QSize(25,25))
        self.cpu_progressBar.setDataPenWidth(4)
        self.main_layout.addWidget(self.cpu_progressBar)

        self.ram_label = QtWidgets.QLabel('Ram')
        self.main_layout.addWidget(self.ram_label)

        '''
        self.ram_progressBar = QtWidgets.QProgressBar()
        self.ram_progressBar.setTextVisible(0)
        '''

        self.ram_progressBar = QRoundProgressBar()
        self.ram_progressBar.setBarStyle(QRoundProgressBar.BarStyle.LINE)
        self.ram_progressBar.setDataPenWidth(4)
        self.ram_progressBar.setFixedSize(QtCore.QSize(25,25))
        self.main_layout.addWidget(self.ram_progressBar)

    def connect_functions(self):
        self.hardware_thread.start()
        self.hardware_thread.hardware_infos.connect(self.update_progress)

    def update_progress(self, infos_tuple):
        cpu = infos_tuple[-1]
        ram = infos_tuple[0]
        if 0<int(cpu)<33:
            color = '#98d47f'
        elif 33<int(cpu)<66:
            color = '#f79360'
        else:
            color = '#f0605b' 
        self.cpu_progressBar.setStyleSheet('QProgressBar::chunk{background-color:%s;}'%color)
        self.cpu_progressBar.setValue(cpu)

        if 0<=int(ram)<33:
            color = '#98d47f'
        elif 33<int(ram)<66:
            color = '#f79360'
        else:
            color = '#f0605b' 
        self.ram_progressBar.setStyleSheet('QProgressBar::chunk{background-color:%s;}'%color)
        self.ram_progressBar.setValue(ram)

class hardware_thread(QtCore.QThread):

    hardware_infos = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(hardware_thread, self).__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            ram = dict(psutil.virtual_memory()._asdict())['percent']
            self.hardware_infos.emit((float(ram), psutil.cpu_percent()))
            time.sleep(0.5)

    def stop(self):
        self.running = False
