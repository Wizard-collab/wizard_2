# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import logging

# Wizard gui modules
from wizard.gui import drop_files_widget

# Wizard modules
from wizard.vars import ressources

logger = logging.getLogger(__name__)

class manual_export_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(manual_export_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Manual exports")

        self.files = []
        self.export_name = None
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.reject_button.clicked.connect(self.reject)
        self.merge_button.clicked.connect(self.merge)
        self.drop_files_button.new_file.connect(self.add_file)

    def merge(self):
        self.get_files_list()
        self.export_name = self.export_name_lineEdit.text()
        self.comment = self.comment_textEdit.toPlainText()
        process = 1
        if self.export_name == '':
            logger.warning('Please enter an export name')
            process = None
        if len(self.files) == 0:
            logger.warning('Please add files to merge')
            process = None
        if process is not None:
            self.accept()

    def get_files_list(self):
        self.files = []
        items = []
        for item_index in range(self.files_list.count()):
            self.files.append(self.files_list.item(item_index).text())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.remove_selection()

    def add_file(self, file):
        self.files_list.addItem(file)
        QtWidgets.QApplication.processEvents()

    def add_files(self, files):
        for file in files:
            self.add_file(file)

    def remove_selection(self):
        if self.files_list.hasFocus():
            selected_items = self.files_list.selectedItems()
            for item in selected_items:
                self.files_list.takeItem(self.files_list.row(item))
                del item

    def set_export_name(self, export_name):
        self.export_name_lineEdit.setText(export_name)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(8)
        self.setLayout(self.main_layout)

        self.infos_label = QtWidgets.QLabel('Drag and drop files or use explorer to manually merge files as exports.')
        self.infos_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.infos_label)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(4)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.header_layout.addWidget(QtWidgets.QLabel('Export name'))

        self.export_name_lineEdit = QtWidgets.QLineEdit()
        self.export_name_lineEdit.setPlaceholderText('The asset exported, Ex: {asset_name}_{stage}')
        self.header_layout.addWidget(self.export_name_lineEdit)

        self.comment_textEdit = QtWidgets.QTextEdit()
        self.comment_textEdit.setPlaceholderText('Your comment here')
        self.comment_textEdit.setMaximumHeight(100)
        self.main_layout.addWidget(self.comment_textEdit)

        self.files_list = QtWidgets.QListWidget()
        self.files_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.main_layout.addWidget(self.files_list)

        self.drop_files_button = drop_files_widget.drop_files_button()
        self.main_layout.addWidget(self.drop_files_button)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.reject_button = QtWidgets.QPushButton('Cancel')
        self.reject_button.setDefault(False)
        self.reject_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.reject_button)

        self.merge_button = QtWidgets.QPushButton('Merge')
        self.merge_button.setObjectName('blue_button')
        self.merge_button.setDefault(True)
        self.merge_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.merge_button)
