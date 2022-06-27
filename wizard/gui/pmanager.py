# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time
import logging

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import gui_utils
from wizard.gui import logging_widget

# Wizard modules
from wizard.core import repository
from wizard.core import tools
from wizard.core import assets
from wizard.core import project
from wizard.core import launch
from wizard.core import environment
from wizard.core import image
from wizard.core import path_utils
from wizard.vars import ressources
from wizard.vars import assets_vars

logger = logging.getLogger(__name__)

class production_manager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(production_manager, self).__init__(parent)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Preview", "Modeling", "Rigging", "Grooming", "Texturing", "Shading"])
        self.main_layout.addWidget(self.table_widget)

    def refresh(self):
        asset_rows = project.get_category_childs(1)
        for asset_row in asset_rows:
            print(asset_row)

w=production_manager()
w.show()
