# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class warning_tooltip(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(warning_tooltip, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.ToolTip)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.additional_labels = []

        self.build_ui()
        self.show()

        self.custom_leave_thread = custom_leave_thread(self.main_widget, self)
        self.custom_leave_thread.hide_signal.connect(self.remove)

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

        self.log_level = QtWidgets.QLabel()
        self.log_level.setObjectName('bold_label')
        self.main_layout.addWidget(self.log_level)

        self.line_frame = QtWidgets.QFrame()
        self.line_frame.setFixedHeight(1)
        self.line_frame.setStyleSheet('background-color:rgba(255,255,255,20)')
        self.main_layout.addWidget(self.line_frame)

        self.log_msg = QtWidgets.QLabel()
        self.main_layout.addWidget(self.log_msg)

        self.open_console_label = QtWidgets.QLabel('Open console for more informations')
        self.open_console_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.open_console_label)
        self.main_widget.setVisible(0)

    def remove(self):
        self.main_widget.setVisible(0)
        for additional_label in self.additional_labels:
            additional_label.setParent(None)
            additional_label.deleteLater()
        self.additional_labels = []

    def invoke(self, log_tuple):
        gui_utils.move_ui(self, 5)
        if not self.main_widget.isVisible():
            self.log_level.setText(log_tuple[0])
            self.log_msg.setText(log_tuple[1])

            self.main_widget.setVisible(1)
            QtWidgets.QApplication.processEvents()
            self.custom_leave_thread.start()
        else:
            new_label = QtWidgets.QLabel(log_tuple[1])
            self.additional_labels.append(new_label)
            self.main_layout.insertWidget(self.main_layout.count()-1, new_label)

class custom_leave_thread(QtCore.QThread):

    hide_signal = pyqtSignal(int)

    def __init__(self, widget, parent=None):
        super(custom_leave_thread, self).__init__(parent)
        self.running = True
        self.widget = widget

    def run(self):
        time.sleep(0.5)
        while True:
            time.sleep(0.01)
            if not self.widget.geometry().contains(self.widget.mapFromGlobal(QtGui.QCursor.pos())):
                #self.widget.setVisible(0)
                self.hide_signal.emit(1)
                break
