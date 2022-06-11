# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import json
import statistics

# Wizard gui modules
from wizard.gui import confirm_widget

# Wizard modules
from wizard.core import repository
from wizard.core import db_utils
from wizard.vars import ressources

class table_viewer_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(table_viewer_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Table viewer")

        self.apply_change = True
        self.table = None

        self.build_ui()
        self.connect_functions()
        self.fill_tables_list()
        self.refresh()

    def build_ui(self):
        self.setObjectName('main_widget')
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setFixedWidth(200)
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setStyleSheet('#tree_as_list_widget{background:#2c2c33;}')
        self.list_view.setColumnCount(1)
        self.list_view.setHeaderHidden(True)
        self.list_view.setIndentation(0)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.main_layout.addWidget(self.list_view)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName('transparent_widget')
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(1)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.toolbar_widget = QtWidgets.QWidget()
        self.toolbar_layout = QtWidgets.QHBoxLayout()
        self.toolbar_widget.setLayout(self.toolbar_layout)
        self.content_layout.addWidget(self.toolbar_widget)

        self.push_button = QtWidgets.QPushButton()
        self.push_button.setFixedSize(QtCore.QSize(30,30))
        self.push_button.setIcon(QtGui.QIcon(ressources._save_icon_))
        self.toolbar_layout.addWidget(self.push_button)

        self.refresh_button = QtWidgets.QPushButton()
        self.refresh_button.setFixedSize(QtCore.QSize(30,30))
        self.refresh_button.setIcon(QtGui.QIcon(ressources._refresh_icon_))
        self.toolbar_layout.addWidget(self.refresh_button)

        self.toolbar_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setItemDelegate(HighlightTextDelegate(self))
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.content_layout.addWidget(self.table_widget)

    def connect_functions(self):
        self.refresh_button.clicked.connect(self.refresh)
        self.push_button.clicked.connect(self.push_all)
        self.list_view.itemSelectionChanged.connect(self.change_table)
        self.table_widget.cellChanged.connect(self.cell_modified)

    def cell_modified(self, row, column):
        if self.apply_change:
            item = self.table_widget.item(row, column)
            item.setData(QtCore.Qt.ForegroundRole, QtGui.QColor(255, 175, 89, 250))
            item.new_data = item.text()

    def change_table(self):
        item = self.list_view.selectedItems()[0]
        table_name = item.table_name
        self.fill_table(table_name)
        self.table = table_name

    def fill_tables_list(self):
        tables_rows = db_utils.get_tables('project')
        items_list = []
        for table_row in tables_rows:
            item = QtWidgets.QTreeWidgetItem(self.list_view.invisibleRootItem())
            item.setText(0, table_row['table_name']) 
            item.table_name = table_row['table_name']
            items_list.append(item)
        items_list[0].setSelected(True)

    def refresh(self):
        if self.table:
            self.fill_table(self.table)

    def get_all_items(self):
        all_items = []
        row_count = self.table_widget.rowCount()
        column_count = self.table_widget.columnCount()
        for row_index in range(0, row_count):
            for column_index in range(0, column_count):
                all_items.append(self.table_widget.item(row_index, column_index))
        return all_items

    def push_all(self):
        if repository.is_admin():
            self.confirm_widget = confirm_widget.confirm_widget("Do you really want to modify the project database ?")
            if self.confirm_widget.exec_() == QtWidgets.QDialog.Accepted:
                all_items = self.get_all_items()
                for item in all_items:
                    if item.new_data is not None:
                        self.push_item_data(item)
                self.refresh()

    def push_item_data(self, item):
        data = item.new_data
        if data == '':
            data = None
        db_utils.update_data('project',
                                self.table,
                                (item.column, data),
                                ('id', item.id))

    def fill_table(self, table):
        self.apply_change = False
        self.table_widget.clear()
        columns_rows = db_utils.get_table_description('project', table)
        data_rows = db_utils.get_rows('project', table)
        self.table_widget.setRowCount(len(data_rows))
        self.table_widget.setColumnCount(len(columns_rows))

        headers = []
        headers_types = [] 
        for column_row in columns_rows:
            headers.append(column_row['column_name'])
            headers_types.append(column_row['data_type'])
        self.table_widget.setHorizontalHeaderLabels(headers)

        data_index = 0
        for data_row in data_rows:
            values_list = list(data_row.values())
            value_index = 0
            for value in values_list:
                item = custom_table_item(data_row['id'], headers[value_index], value, headers_types[value_index])
                self.table_widget.setItem(data_index, value_index, item)
                value_index += 1
            data_index += 1

        self.table_widget.resizeColumnsToContents()
        self.apply_change = True

class custom_table_item(QtWidgets.QTableWidgetItem):
    def __init__(self, id, column, data, data_type, parent=None):
        super(custom_table_item, self).__init__(parent)
        self.id = id
        self.column = column
        self.data = data
        self.new_data = None
        self.data_type = data
        self.fill_ui()

    def fill_ui(self):
        self.setText(str(self.data))
        if self.data is None:
            self.setData(QtCore.Qt.ForegroundRole, QtGui.QColor(255,255,255,40))

class HighlightTextDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(HighlightTextDelegate, self).__init__(parent)

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        foregroundData = index.data(QtCore.Qt.ForegroundRole)
        if foregroundData:
            option.palette.setBrush(QtGui.QPalette.HighlightedText, QtGui.QBrush(foregroundData))

