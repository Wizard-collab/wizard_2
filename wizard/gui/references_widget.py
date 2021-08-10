# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import search_reference_widget

class references_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(references_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        pass

    def connect_functions(self):
        self.search_sc = QtWidgets.QShortcut(QtGui.QKeySequence('Tab'), self)
        self.search_sc.activated.connect(self.search_reference)

    def search_reference(self):
        self.search_reference_widget = search_reference_widget.search_reference_widget()
        self.search_reference_widget.show()