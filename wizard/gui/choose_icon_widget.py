# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.vars import ressources
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

# Wizard gui modules
from wizard.gui import gui_utils

class choose_icon_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(choose_icon_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.ToolTip)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.icon_path = None

        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def connect_functions(self):
        self.icon_view.itemDoubleClicked.connect(self.choose_icon)

    def choose_icon(self, item):
        self.icon_path = item.icon_path
        self.accept()

    def leaveEvent(self, event):
        self.reject()

    def build_ui(self):
        self.resize(290,200)
        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.main_widget_layout)

        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setObjectName('black_round_frame')
        self.main_widget_layout.addWidget(self.main_widget)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)

        self.icon_view = QtWidgets.QListWidget()
        self.icon_view.setObjectName('icon_view')
        self.icon_view.setStyleSheet('#icon_view{background-color:transparent}')
        self.icon_view.setSpacing(4)
        self.icon_view.setIconSize(QtCore.QSize(20,20))
        self.icon_view.setMovement(QtWidgets.QListView.Static)
        self.icon_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.icon_view.setViewMode(QtWidgets.QListView.IconMode)
        self.icon_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.icon_view_scrollBar = self.icon_view.verticalScrollBar()
        self.main_layout.addWidget(self.icon_view)

    def fill_ui(self):
        for icon in ressources._available_icons_list_:
            item = QtWidgets.QListWidgetItem()
            item.setIcon(QtGui.QIcon(icon))
            item.setSizeHint(QtCore.QSize(26,26))
            item.icon_path = icon
            self.icon_view.addItem(item)

    def showEvent(self, event):
        gui_utils.move_ui(self, -5)
