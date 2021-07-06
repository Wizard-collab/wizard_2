# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import project
from wizard.core import tools

class exports_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(exports_widget, self).__init__(parent)
        self.export_ids = dict()
        self.export_versions_ids = dict()
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setObjectName('tree_as_list_widget')
        self.tree_widget.setColumnCount(5)
        self.tree_widget.setIndentation(20)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setHeaderLabels(['Export name', 'Version', 'User', 'Date', 'Comment'])
        self.tree_widget_scrollBar = self.tree_widget.verticalScrollBar()
        self.main_layout.addWidget(self.tree_widget)

    def connect_functions(self):
        self.tree_widget_scrollBar.rangeChanged.connect(lambda: self.tree_widget_scrollBar.setValue(self.tree_widget_scrollBar.maximum()))

    def refresh(self):
        exports_rows = project.get_variant_export_childs(self.variant_id)
        if exports_rows is not None:
            for export_row in exports_rows:
                if export_row['id'] not in self.export_ids.keys():
                    export_item = custom_export_tree_item(export_row, self.tree_widget.invisibleRootItem())
                    self.export_ids[export_row['id']] = export_item
        export_versions_rows = project.get_export_versions_by_variant(self.variant_id)
        if export_versions_rows is not None:
            for export_version_row in export_versions_rows:
                if export_version_row['id'] not in self.export_versions_ids.keys():
                    if export_version_row['export_id'] in self.export_ids.keys():
                        export_version_item = custom_export_version_tree_item(export_version_row, self.export_ids[export_version_row['export_id']])
                        self.export_versions_ids[export_version_row['id']] = export_version_item

    def change_variant(self, variant_id):
        self.export_ids = dict()
        self.export_versions_ids = dict()
        self.tree_widget.clear()
        self.variant_id = variant_id
        self.refresh()
        

class custom_export_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, export_row, parent=None):
        super(custom_export_tree_item, self).__init__(parent)
        self.export_row = export_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.export_row['name'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(0, bold_font)
        self.setText(2, self.export_row['creation_user'])
        day, hour = tools.convert_time(self.export_row['creation_time'])
        self.setText(3, f"{day} - {hour}")
        #self.setText(3, self.export_row['comment'])

class custom_export_version_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, export_version_row, parent=None):
        super(custom_export_version_tree_item, self).__init__(parent)
        self.export_version_row = export_version_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(1, self.export_version_row['name'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.setText(2, self.export_version_row['creation_user'])
        day, hour = tools.convert_time(self.export_version_row['creation_time'])
        self.setText(3, f"{day} - {hour}")
        self.setText(4, self.export_version_row['comment'])