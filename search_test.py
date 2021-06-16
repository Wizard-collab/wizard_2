import sys

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QWidget,
)
from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from wizard.core import project
import PyWizard
import time
from wizard.core import launch
from wizard.core import communicate
from wizard.core import user
import json
import traceback

from wizard.core import logging
logging = logging.get_logger(__name__)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search test")
        self.layout=QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.search_bar=QtWidgets.QLineEdit()
        self.search_bar.textChanged.connect(self.update_list)
        self.layout.addWidget(self.search_bar)
        self.list=QtWidgets.QListWidget()
        self.layout.addWidget(self.list)
        self.search_thread = search_thread('')
        self.search_thread.item_signal.connect(self.add_item)

    def update_list(self, search):
        self.search_thread.running=False
        self.list.clear()
        if search != '' and len(search)>=2:
            #self.search_thread = search_thread(search)
            self.search_thread.search=search
            self.search_thread.running=True
            self.search_thread.start()

    def add_item(self, item_tuple):
        list_item = QtWidgets.QListWidgetItem(item_tuple[0])
        list_item.id = item_tuple[1]
        self.list.addItem(list_item)

class search_thread(QtCore.QThread):

    item_signal = pyqtSignal(tuple)
    done_signal = pyqtSignal(bool)

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
            if not self.running:
                break
            stages = project_obj.get_asset_childs(asset_row['id'])
            if not self.running:
                break
            for stage_row in stages:
                if not self.running:
                    break
                if self.running:
                    self.item_signal.emit((f"{domain_name}-{asset_row['name']}-{stage_row['name']}", stage_row['id']))
                else:
                    break
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())