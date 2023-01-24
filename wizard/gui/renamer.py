# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os

# Wizard core modules
from wizard.core import path_utils
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

class renamer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(renamer, self).__init__(parent)
        self.directory = None
        self.files_dic = dict()
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(2)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.path_lineEdit = QtWidgets.QLineEdit()
        self.path_lineEdit.setEnabled(False)
        self.header_layout.addWidget(self.path_lineEdit)

        self.path_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.path_button, "Open work environment folder")
        self.path_button.setFixedSize(QtCore.QSize(26, 26))
        self.path_button.setIconSize(QtCore.QSize(20, 20))
        self.path_button.setIcon(QtGui.QIcon(ressources._folder_icon_))
        self.header_layout.addWidget(self.path_button)

        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(1)
        self.main_layout.addLayout(self.content_layout)

        self.viewer_widget = QtWidgets.QWidget()
        self.viewer_layout = QtWidgets.QVBoxLayout()
        self.viewer_layout.setContentsMargins(0,0,0,0)
        self.viewer_widget.setLayout(self.viewer_layout)
        self.content_layout.addWidget(self.viewer_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(3)
        self.list_view.setHeaderLabels(['Original file', '', 'File renamed'])
        self.list_view.header().resizeSection(1, 20)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.viewer_layout.addWidget(self.list_view)

        self.settings_widget = QtWidgets.QWidget()
        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_widget.setLayout(self.settings_layout)
        self.content_layout.addWidget(self.settings_widget)

        self.settings_layout.addWidget(QtWidgets.QLabel("Replace"))

        self.replace_layout = QtWidgets.QHBoxLayout()
        self.settings_layout.addLayout(self.replace_layout)
        self.to_replace_lineEdit = QtWidgets.QLineEdit()
        self.to_replace_lineEdit.setPlaceholderText('String to find and replace')
        self.replace_layout.addWidget(self.to_replace_lineEdit)
        self.replace_lineEdit = QtWidgets.QLineEdit()
        self.replace_lineEdit.setPlaceholderText('String to use as replacement')
        self.replace_layout.addWidget(self.replace_lineEdit)

        self.settings_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def refresh(self):
        self.path_lineEdit.setText(self.directory)
        files = path_utils.listdir(self.directory)
        for file in files:
            if file not in self.files_dic.keys():
                item = QtWidgets.QTreeWidgetItem(self.list_view.invisibleRootItem())
                self.files_dic[file] = dict()
                self.files_dic[file]['tree_item'] = item
                self.files_dic[file]['original'] = file
                self.files_dic[file]['renamed'] = file
                self.files_dic[file]['tree_item'].setText(0, self.files_dic[file]['original'])
                self.files_dic[file]['tree_item'].setIcon(1, QtGui.QIcon(ressources._rigth_arrow_icon_))
        existings_items = list(self.files_dic.keys())
        for existing_item in existings_items:
            if existing_item not in files:
                self.remove_file(existing_item)
        self.apply_filters()

    def connect_functions(self):
        self.path_button.clicked.connect(self.set_directory)
        self.to_replace_lineEdit.textChanged.connect(self.apply_filters)
        self.replace_lineEdit.textChanged.connect(self.apply_filters)

    def apply_filters(self):
        find = self.to_replace_lineEdit.text()
        replace = self.replace_lineEdit.text()
        for file in self.files_dic.keys():
            file_name, ext = os.path.splitext(file) 
            if find != '':
                self.files_dic[file]['renamed'] = f"{file_name.replace(find, replace)}{ext}"
            else:
                self.files_dic[file]['renamed'] = self.files_dic[file]['original']
            self.files_dic[file]['tree_item'].setText(2, self.files_dic[file]['renamed'])

    def remove_item(self, file):
        if file in self.files_dic.keys():
            self.files_dic[file]['tree_item'].setParent(None)
            self.files_dic[file]['tree_item'].deleteLater()
            del self.files_dic[file]

    def clear_all(self):
        self.files_dic = dict()
        self.list_view.clear()

    def set_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose directory",
                                                                   "",
                                                                   QtWidgets.QFileDialog.ShowDirsOnly
                                                                   | QtWidgets.QFileDialog.DontResolveSymlinks)
        if directory is not None and directory != '':
            self.clear_all()
            self.directory = path_utils.clean_path(directory)
        self.refresh()

w=renamer()
w.show()