# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

# Wizard modules
from wizard.core import project

class tree_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(tree_widget, self).__init__(parent)

        self.domain_ids=dict()
        self.category_ids=dict()
        self.asset_ids=dict()
        self.stage_ids=dict()

        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.search_bar = QtWidgets.QLineEdit()
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.search_list = QtWidgets.QListWidget()
        self.search_list.setVisible(0)
        self.main_layout.addWidget(self.search_bar)
        self.main_layout.addWidget(self.tree)
        self.main_layout.addWidget(self.search_list)

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.search_asset)
        self.search_thread = search_thread('')
        self.search_thread.item_signal.connect(self.add_search_item)

    def fill_ui(self):
        project_obj = project.project()

        for domain_row in project_obj.get_domains():
            self.add_domain(domain_row)
        for category_row in project_obj.get_all_categories():
            self.add_category(category_row)
        for asset_row in project_obj.get_all_assets():
            self.add_asset(asset_row)
        for stage_row in project_obj.get_all_stages():
            self.add_stage(stage_row)

    def add_domain(self, row):
        if row['id'] not in self.domain_ids.keys():
            domain_item = QtWidgets.QTreeWidgetItem([f"{row['name']}"])
            domain_item.id = row['id']
            self.domain_ids[row['id']] = domain_item
            self.tree.addTopLevelItem(domain_item)

    def add_category(self, row):
        if row['id'] not in self.category_ids.keys():
            parent_widget = self.domain_ids[row['domain_id']]
            category_item = QtWidgets.QTreeWidgetItem([f"{row['name']}"])
            category_item.id = row['id']
            self.category_ids[row['id']] = category_item
            parent_widget.addChild(category_item)

    def add_asset(self, row):
        if row['id'] not in self.asset_ids.keys():
            parent_widget = self.category_ids[row['category_id']]
            asset_item = QtWidgets.QTreeWidgetItem([f"{row['name']}"])
            asset_item.id = row['id']
            self.asset_ids[row['id']] = asset_item
            parent_widget.addChild(asset_item)

    def add_stage(self, row):
        if row['id'] not in self.stage_ids.keys():
            parent_widget = self.asset_ids[row['asset_id']]
            stage_item = QtWidgets.QTreeWidgetItem([f"{row['name']}"])
            stage_item.id = row['id']
            self.stage_ids[row['id']] = stage_item
            parent_widget.addChild(stage_item)

    def search_asset(self, search):
        if search != '' or len(search) > 2:
            self.tree.setVisible(0)
            self.search_list.setVisible(1)
            self.search_thread.running=False
            self.search_list.clear()
            self.search_thread.search=search
            self.search_thread.running=True
            self.search_thread.start()
        else:
            self.tree.setVisible(1)
            self.search_list.setVisible(0)
            self.search_thread.running=False
            self.search_list.clear()
            self.fill_ui()

    def add_search_item(self, item_tuple):
        search_item = QtWidgets.QListWidgetItem(item_tuple[0])
        search_item.id = item_tuple[1]
        self.search_list.addItem(search_item)

class search_thread(QtCore.QThread):

    item_signal = pyqtSignal(tuple)

    def __init__(self, search):
        super().__init__()
        self.search = search
        self.running = True

    def run(self):
        project_obj = project.project()
        assets_list = project_obj.search_asset(self.search)
        stages = []
        for asset_row in assets_list:
            if not self.running:
                break
            domain_name = project_obj.get_category_data(project_obj.get_asset_data(asset_row['id'], 'category_id'), 'name')
            stages = project_obj.get_asset_childs(asset_row['id'])
            for stage_row in stages:
                if not self.running:
                    break
                if self.running:
                    self.item_signal.emit((f"{domain_name}-{asset_row['name']}-{stage_row['name']}", stage_row['id']))

def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = tree_widget()
    widget.show()
    #widget.fill_ui()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()