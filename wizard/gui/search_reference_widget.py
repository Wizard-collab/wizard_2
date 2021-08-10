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
    def __init__(self, parent = None):
        super(search_reference_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

        self.search_thread = search_thread()
        self.stage_ids = dict()

        self.build_ui()
        self.connect_functions()

        self.all_export_versions_stage_ids = project.get_all_export_versions('stage_id')

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        event.accept()

    def leaveEvent(self, event):
        self.close()

    def search_asset(self, search):
        self.list_view.clear()
        self.stage_ids = dict()
        if len(search) > 2:
            if ':' in search:
                category_string=search.split(':')[0]
                asset_string=search.split(':')[-1]
            else:
                category_string = None
                asset_string = search
            self.search_thread.update_search(category_string, asset_string)
        else:
            self.search_thread.running=False

    def add_item(self, item_list):
        if item_list[-1]['id'] not in self.stage_ids.keys():
            if item_list[-1]['id'] in self.all_export_versions_stage_ids:
                asset_item = custom_item(item_list[0], item_list[-1], self.list_view.invisibleRootItem())
                self.stage_ids[item_list[-1]['id']] = asset_item

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.search_asset)
        self.search_thread.item_signal.connect(self.add_item)

    def build_ui(self):
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
        self.list_view.setColumnCount(2)
        self.list_view.setHeaderHidden(True)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.header().resizeSection(0, 40)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.main_widget_layout.addWidget(self.list_view)

class search_thread(QtCore.QThread):

    item_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.category = None
        self.asset = None
        self.running = True

    def update_search(self, category=None, asset=None):
        self.running = False
        self.category = category
        self.asset = asset
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
                stage_rows = project.get_asset_childs(asset_row['id'])
                for stage_row in stage_rows:
                    if not self.running:
                        break
                    self.item_signal.emit([f"{asset_row['name']}", stage_row])

class custom_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, text, stage_row, parent=None):
        super(custom_item, self).__init__(parent)
        self.text = text
        self.stage_row = stage_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.text)
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(0, bold_font)
        self.setText(1, self.stage_row['name'])
        self.setIcon(1, QtGui.QIcon(ressources._stage_icons_dic_[self.stage_row['name']]))
