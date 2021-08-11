# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard modules
from wizard.core import assets
from wizard.core import project
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

class search_reference_widget(QtWidgets.QWidget):

    variant_ids_signal = pyqtSignal(list)

    def __init__(self, parent = None):
        super(search_reference_widget, self).__init__(parent)

        self.accept_item_from_thread = True

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

        self.search_thread = search_thread()
        self.variant_ids = dict()

        self.build_ui()
        self.connect_functions()

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        event.accept()

    def clear(self):
        self.search_bar.setFocus(1)
        self.search_bar.setText('')

    def leaveEvent(self, event):
        self.close()

    def search_asset(self, search):
        self.accept_item_from_thread = False
        self.list_view.clear()
        self.variant_ids = dict()
        if len(search) > 1:
            stage_filter = None
            if '*' in search:
                stage_filter = search.split('*')[-1]
                search = search.split('*')[0]

            if ':' in search:
                category_string=search.split(':')[0]
                asset_string=search.split(':')[-1]
            else:
                category_string = None
                asset_string = search
            self.accept_item_from_thread = True
            self.search_thread.update_search(category_string, asset_string, stage_filter)
        else:
            self.search_thread.running=False

    def add_item(self, item_list):
        if self.accept_item_from_thread:
            if item_list[3]['id'] not in self.variant_ids.keys():
                variant_item = custom_item(item_list[0], item_list[1], item_list[2], item_list[3], self.list_view.invisibleRootItem())
                self.variant_ids[item_list[3]['id']] = variant_item

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.search_asset)
        self.search_thread.item_signal.connect(self.add_item)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Down:
            self.list_view.keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Up:
            self.list_view.keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Return:
            self.return_references()
        event.accept()

    def return_references(self):
        selected_items = self.list_view.selectedItems()
        if selected_items is not None and len(selected_items)>=1:
            variant_ids = []
            for selected_item in selected_items:
                variant_ids.append(selected_item.variant_row['id'])
            if variant_ids != []:
                self.variant_ids_signal.emit(variant_ids)
                print(variant_ids)
            self.close()

    def build_ui(self):
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12,12,12,12)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setStyleSheet('border-radius:12px;')
        self.main_widget_layout = QtWidgets.QVBoxLayout()
        self.main_widget_layout.setContentsMargins(0,0,0,0)
        self.main_widget_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_widget_layout)
        self.main_layout.addWidget(self.main_widget)

        self.search_bar = gui_utils.search_bar()
        self.search_bar.setObjectName('transparent_widget')
        self.search_bar.setPlaceholderText('"asset", "category:asset"')
        self.main_widget_layout.addWidget(self.search_bar)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setStyleSheet('border-top-left-radius:0px;border-top-right-radius:0px;')
        self.list_view.setColumnCount(4)
        self.list_view.setHeaderHidden(True)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.header().resizeSection(0, 110)
        self.list_view.header().resizeSection(1, 110)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.main_widget_layout.addWidget(self.list_view)

class search_thread(QtCore.QThread):

    item_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.category = None
        self.asset = None
        self.running = True
        self.all_export_versions_stage_ids = []

    def update_search(self, category=None, asset=None, stage_filter=None):
        self.running = False
        self.all_export_versions_variant_ids = project.get_all_export_versions('variant_id')
        self.category = category
        self.asset = asset
        self.stage_filter = stage_filter
        self.running = True
        self.start()

    def run(self):
        process=1
        parent_id = None
        if self.category and len(self.category)>2:
            category_id=project.get_category_data_by_name(self.category, 'id')
            if category_id:
                parent_id = category_id
        if self.category and not parent_id:
            process=None
        if process:
            assets_list = project.search_asset(self.asset, parent_id)
            for asset_row in assets_list:
                if not self.running:
                    break
                category_row = project.get_category_data(project.get_asset_data(asset_row['id'], 'category_id'))
                stage_rows = project.get_asset_childs(asset_row['id'])
                for stage_row in stage_rows:
                    if not self.running:
                        break
                    variant_rows = project.get_stage_childs(stage_row['id'])
                    for variant_row in variant_rows:
                        if not self.running:
                            break
                        if variant_row['id'] in self.all_export_versions_variant_ids:
                            if (self.stage_filter is None) or (self.stage_filter in stage_row['name']):
                                if self.running:
                                    self.item_signal.emit([category_row, asset_row, stage_row, variant_row])

class custom_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, category_row, asset_row, stage_row, variant_row, parent=None):
        super(custom_item, self).__init__(parent)
        self.category_row = category_row
        self.asset_row = asset_row
        self.stage_row = stage_row
        self.variant_row = variant_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.category_row['name'])
        self.setText(1, self.asset_row['name'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.setText(2, self.stage_row['name'])
        self.setIcon(2, QtGui.QIcon(ressources._stage_icons_dic_[self.stage_row['name']]))
        self.setText(3, self.variant_row['name'])