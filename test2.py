import sys

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QWidget,
)
from PyQt5 import QtWidgets, QtGui
from wizard.core import project
import PyWizard
import time
from wizard.core import launch
from wizard.core import communicate
import json

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QHBoxLayout Example")
        # Create a QHBoxLayout instance
        layout = QHBoxLayout()
        # Add widgets to the layout
        self.tree = QtWidgets.QTreeWidget()
        self.tree.currentItemChanged.connect(self.item_changed)
        layout.addWidget(self.tree)

        #root = QtWidgets.QTreeWidgetItem()
        #tree.addTopLevelItem(root)
        project_obj = project.project()
        domains_rows = project_obj.get_domains()
        for domain_row in domains_rows:
            domain_item = QtWidgets.QTreeWidgetItem([f"{domain_row['id']}-{domain_row['name']}"])
            domain_item.id = domain_row['id']
            domain_item.instance = 'domain'
            self.tree.addTopLevelItem(domain_item)
            for category_row in project_obj.get_domain_childs(domain_row['id']):
                category_item = QtWidgets.QTreeWidgetItem([f"{category_row['id']}-{category_row['name']}"])
                category_item.id = category_row['id']
                category_item.instance = 'category'
                domain_item.addChild(category_item)
                for asset_row in project_obj.get_category_childs(category_row['id']):
                    asset_item = QtWidgets.QTreeWidgetItem([f"{asset_row['id']}-{asset_row['name']}"])
                    asset_item.id = asset_row['id']
                    asset_item.instance = 'asset'
                    category_item.addChild(asset_item)
                    for stage_row in project_obj.get_asset_childs(asset_row['id']):
                        stage_item = QtWidgets.QTreeWidgetItem([f"{stage_row['id']}-{stage_row['name']}"])
                        stage_item.id = stage_row['id']
                        stage_item.instance = 'stage'
                        asset_item.addChild(stage_item)

        self.variant_listwidget = QtWidgets.QListWidget()
        self.variant_listwidget.itemClicked.connect(self.variant_changed)
        layout.addWidget(self.variant_listwidget)

        self.variant_childs_widget = QtWidgets.QWidget()
        self.variant_childs_layout = QtWidgets.QVBoxLayout()
        self.variant_childs_widget.setLayout(self.variant_childs_layout)
        layout.addWidget(self.variant_childs_widget)
        self.variant_childs_layout.addWidget(QtWidgets.QLabel('WORK'))

        self.work_childs_widget = QtWidgets.QWidget()
        self.work_childs_layout = QtWidgets.QHBoxLayout()
        self.work_childs_widget.setLayout(self.work_childs_layout)
        self.variant_childs_layout.addWidget(self.work_childs_widget)

        self.work_env_listwidget = QtWidgets.QListWidget()
        self.work_env_listwidget.itemClicked.connect(self.work_env_changed)
        self.work_childs_layout.addWidget(self.work_env_listwidget)

        self.launcher_widget = QtWidgets.QWidget()
        self.launcher_layout = QtWidgets.QVBoxLayout()

        self.launcher_widget.setLayout(self.launcher_layout)

        self.versions_listwidget = QtWidgets.QListWidget()
        self.versions_listwidget.itemClicked.connect(self.update_image)
        self.versions_listwidget.currentItemChanged.connect(self.update_image)
        self.versions_listwidget.itemDoubleClicked.connect(self.launch)
        self.launcher_layout.addWidget(self.versions_listwidget)

        self.image_label=QtWidgets.QLabel('')
        self.launcher_layout.addWidget(self.image_label)

        self.work_childs_layout.addWidget(self.launcher_widget)
        
        self.variant_childs_layout.addWidget(QtWidgets.QLabel('EXPORTS'))

        self.export_childs_widget = QtWidgets.QWidget()
        self.export_childs_layout = QtWidgets.QHBoxLayout()
        self.export_childs_widget.setLayout(self.export_childs_layout)
        self.variant_childs_layout.addWidget(self.export_childs_widget)

        self.exports_listwidget = QtWidgets.QListWidget()
        self.exports_listwidget.itemClicked.connect(self.export_changed)
        self.export_childs_layout.addWidget(self.exports_listwidget)

        self.export_versions_listwidget = QtWidgets.QListWidget()
        self.export_versions_listwidget.itemClicked.connect(self.export_version_changed)
        self.export_childs_layout.addWidget(self.export_versions_listwidget)

        self.export_files_listWidget = QtWidgets.QListWidget()
        self.export_childs_layout.addWidget(self.export_files_listWidget)

        # Set the layout on the application's window
        self.setLayout(layout)
        #print(self.children())

    def launch(self, item):
    	launch.launch_work_version(item.id)

    def item_changed(self, item):
        self.variant_listwidget.clear()
        self.work_env_listwidget.clear()
        self.versions_listwidget.clear()
        self.exports_listwidget.clear()
        self.export_versions_listwidget.clear()
        self.export_files_listWidget.clear()
        if item.instance == 'stage':
            variants_list = project.project().get_stage_childs(item.id)
            for variant_row in variants_list:
                variant_item = QtWidgets.QListWidgetItem(f"{variant_row['id']}-{variant_row['name']}")
                variant_item.id = variant_row['id']
                self.variant_listwidget.addItem(variant_item)

    def variant_changed(self, item):
        self.work_env_listwidget.clear()
        self.versions_listwidget.clear()
        self.exports_listwidget.clear()
        self.export_versions_listwidget.clear()
        self.export_files_listWidget.clear()
        work_envs_list = project.project().get_variant_work_envs_childs(item.id)
        for work_env_row in work_envs_list:
            work_env_item = QtWidgets.QListWidgetItem(f"{work_env_row['id']}-{work_env_row['name']}")
            work_env_item.id = work_env_row['id']
            self.work_env_listwidget.addItem(work_env_item)

        exports_list = project.project().get_variant_export_childs(item.id)
        for export_row in exports_list:
            export_item = QtWidgets.QListWidgetItem(f"{export_row['id']}-{export_row['name']}")
            export_item.id = export_row['id']
            self.exports_listwidget.addItem(export_item)

    def work_env_changed(self, item):
        self.versions_listwidget.clear()
        versions_list = project.project().get_work_versions(item.id)
        for version_row in versions_list:
            version_item = QtWidgets.QListWidgetItem(f"{version_row['id']}-{version_row['name']}-{version_row['comment']}-{version_row['creation_user']}-{self.convert_time(version_row['creation_time'])}")
            version_item.id = version_row['id']
            self.versions_listwidget.addItem(version_item)

    def export_changed(self, item):
        self.export_versions_listwidget.clear()
        self.export_files_listWidget.clear()
        export_versions_list = project.project().get_export_versions(item.id)
        for export_version_row in export_versions_list:
            export_version_item = QtWidgets.QListWidgetItem(f"{export_version_row['name']}-{export_version_row['comment']}-{export_version_row['creation_user']}-{self.convert_time(export_version_row['creation_time'])}")
            export_version_item.id = export_version_row['id']
            self.export_versions_listwidget.addItem(export_version_item)

    def export_version_changed(self, item):
        self.export_files_listWidget.clear()
        files = project.project().get_export_version_data(item.id, 'files')
        if files:
            files_list = json.loads(files)
            self.export_files_listWidget.addItems(files_list)

    def update_image(self, item):
    	if item:
	    	image_data = project.project().get_version_data(item.id, 'screenshot')
	    	self.image_label.setPixmap(self.get_tray_icon(image_data))

    def get_tray_icon(self, data):
        pm = QtGui.QPixmap()
        pm.loadFromData(data)
        return pm

    def convert_time(self, time_float):
    	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_float))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    server = communicate.communicate_server()
    server.start()
    sys.exit(app.exec_())