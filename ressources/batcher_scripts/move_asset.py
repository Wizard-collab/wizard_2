# Update and export multiple stages

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import logging
logger = logging.getLogger(__name__)

# Wizard core modules
from wizard.core import assets
from wizard.core import project
from wizard.core import launch_batch
from wizard.core import tools
from wizard.core import team_client
from wizard.core import environment
from wizard.core import subtask
from wizard.core import deadline
from wizard.vars import assets_vars
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_server

name = "Move asset"
icon = ressources._move_icon_
description = """Move the selected asset to the selected category ( New name is optionnal )
"""

class widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(widget, self).__init__(parent)
        self.build_ui()
        self.fill_ui()
        self.refresh()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('transparent_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.trees_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.trees_layout)

        self.original_asset_layout = QtWidgets.QVBoxLayout()
        self.trees_layout.addLayout(self.original_asset_layout)
        self.original_asset_label = QtWidgets.QLabel("Select here the asset to move")
        self.original_asset_layout.addWidget(self.original_asset_label)

        self.original_asset_tree = QtWidgets.QTreeWidget()
        self.original_asset_tree.setObjectName('tree_widget')
        self.original_asset_tree.setHeaderHidden(True)
        self.original_asset_tree.setAlternatingRowColors(True)
        self.original_asset_layout.addWidget(self.original_asset_tree)

        self.original_asset_tree_info_label = QtWidgets.QLabel()
        self.original_asset_layout.addWidget(self.original_asset_tree_info_label)

        self.destination_category_layout = QtWidgets.QVBoxLayout()
        self.trees_layout.addLayout(self.destination_category_layout)
        self.destination_category_label = QtWidgets.QLabel("Select here destination category")
        self.destination_category_layout.addWidget(self.destination_category_label)

        self.destination_category_tree = QtWidgets.QTreeWidget()
        self.destination_category_tree.setObjectName('tree_widget')
        self.destination_category_tree.setHeaderHidden(True)
        self.destination_category_tree.setAlternatingRowColors(True)
        self.destination_category_layout.addWidget(self.destination_category_tree)

        self.new_name_lineEdit = QtWidgets.QLineEdit()
        self.new_name_lineEdit.setPlaceholderText("Enter a new name (Optional)")
        self.new_name_lineEdit.setStyleSheet("background-color:rgba(0,0,0,50)")
        self.destination_category_layout.addWidget(self.new_name_lineEdit)

        self.destination_category_tree_info_label = QtWidgets.QLabel()
        self.destination_category_layout.addWidget(self.destination_category_tree_info_label)

        self.footer_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.footer_layout)

        self.deadline_checkbox = QtWidgets.QCheckBox("Deadline")
        self.footer_layout.addWidget(self.deadline_checkbox)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.execute_button = QtWidgets.QPushButton("Execute")
        self.execute_button.setObjectName("blue_button")
        self.main_layout.addWidget(self.execute_button)

    def fill_ui(self):
        self.fill_original_asset_tree()
        self.fill_destination_category_tree()

    def fill_original_asset_tree(self):
        self.assets_dic = dict()
        all_domains = project.get_domains()
        for domain_row in all_domains:
            categories = project.get_domain_childs(domain_row['id'])
            domain_item = QtWidgets.QTreeWidgetItem(self.original_asset_tree.invisibleRootItem())
            domain_item.setText(0, domain_row['name'])
            for category_row in categories:
                assets = project.get_category_childs(category_row['id'])
                category_item = QtWidgets.QTreeWidgetItem(domain_item)
                category_item.setText(0, category_row['name'])
                for asset_row in assets:
                    stages = project.get_asset_childs(asset_row['id'])
                    asset_item = QtWidgets.QTreeWidgetItem(category_item)
                    check_box = QtWidgets.QCheckBox(asset_row['name'])
                    check_box.stateChanged.connect(self.refresh)
                    self.original_asset_tree.setItemWidget(asset_item, 0, check_box)
                    self.assets_dic[asset_row['id']] = dict()
                    self.assets_dic[asset_row['id']]['row'] = asset_row
                    self.assets_dic[asset_row['id']]['item'] = asset_item
                    self.assets_dic[asset_row['id']]['check_box'] = check_box

    def fill_destination_category_tree(self):
        self.destination_category_dic = dict()
        all_domains = project.get_domains()
        for domain_row in all_domains:
            categories = project.get_domain_childs(domain_row['id'])
            domain_item = QtWidgets.QTreeWidgetItem(self.destination_category_tree.invisibleRootItem())
            domain_item.setText(0, domain_row['name'])
            for category_row in categories:
                category_item = QtWidgets.QTreeWidgetItem(domain_item)
                check_box = QtWidgets.QCheckBox(category_row['name'])
                check_box.stateChanged.connect(self.refresh)
                self.destination_category_tree.setItemWidget(category_item, 0, check_box)
                self.destination_category_dic[category_row['id']] = dict()
                self.destination_category_dic[category_row['id']]['row'] = category_row
                self.destination_category_dic[category_row['id']]['item'] = category_item
                self.destination_category_dic[category_row['id']]['check_box'] = check_box

    def refresh(self):
        assets_ids = self.get_selected_original_asset_id()
        if len(assets_ids) == 0:
            self.original_asset_tree_info_label.setText("No asset selected")
            self.original_asset_tree_info_label.setStyleSheet("color:#f79360")
        if len(assets_ids) > 1:
            self.original_asset_tree_info_label.setText("Please select only one asset to move")
            self.original_asset_tree_info_label.setStyleSheet("color:#f79360")
        if len(assets_ids) == 1:
            self.original_asset_tree_info_label.setText("")
            self.original_asset_tree_info_label.setStyleSheet("")

        categories_ids = self.get_selected_destination_category()
        if len(categories_ids) == 0:
            self.destination_category_tree_info_label.setText("No destination category selected")
            self.destination_category_tree_info_label.setStyleSheet("color:#f79360")
        if len(categories_ids) > 1:
            self.destination_category_tree_info_label.setText("Please select only one destination category")
            self.destination_category_tree_info_label.setStyleSheet("color:#f79360")
        if len(categories_ids) == 1:
            self.destination_category_tree_info_label.setText("")
            self.destination_category_tree_info_label.setStyleSheet("")

    def connect_functions(self):
        self.execute_button.clicked.connect(self.execute)

    def get_selected_original_asset_id(self):
        assets_ids = []
        for asset_id in self.assets_dic.keys():
            if not self.assets_dic[asset_id]['check_box'].isChecked():
                continue
            assets_ids.append(asset_id)
        return assets_ids

    def get_selected_destination_category(self):
        categories_ids = []
        for category_id in self.destination_category_dic.keys():
            if not self.destination_category_dic[category_id]['check_box'].isChecked():
                continue
            categories_ids.append(category_id)
        return categories_ids

    def execute(self):
        original_asset_id = self.get_selected_original_asset_id()
        destination_category_id = self.get_selected_destination_category()
        if len(original_asset_id) != 1:
            return
        original_asset_id = original_asset_id[0]
        if len(destination_category_id) != 1:
            return
        destination_category_id = destination_category_id[0]
        new_name = self.new_name_lineEdit.text()
        command = "from ressources.batcher_scripts import move_asset\n"
        command += f"""move_asset.main({original_asset_id}, {destination_category_id}, "{new_name}")"""
        on_deadline = self.deadline_checkbox.isChecked()
        if on_deadline:
            deadline.submit_job(command, "TEST BATCHER")
            return
        task = subtask.subtask(pycmd=command, print_stdout=False)
        task.start()

def main(original_asset_id, destination_category_id, new_name):

        if new_name == '' or new_name is None:
            new_name = project.get_asset_data(original_asset_id, 'name')

        # CREATE DESTINATION ASSET
        destination_asset_id = assets.create_asset(new_name, destination_category_id)
        destination_asset_row = project.get_asset_data(destination_asset_id)

        stages_list = project.get_asset_childs(original_asset_id)
        for stage_row in stages_list:

            # CREATING STAGES
            destination_stage_id = assets.create_stage(stage_row['name'], destination_asset_id)
            original_variants = project.get_stage_childs(stage_row['id'])
            for variant_row in original_variants:

                # CREATING VARIANTS
                if variant_row['name'] != 'main':
                    assets.create_variant(variant_row['name'], destination_stage_id)
                destination_variant_id = project.get_variant_by_name(destination_stage_id, variant_row['name'], column='id')
                original_work_envs = project.get_variant_work_envs_childs(variant_row['id'])

                # CREATING WORK ENVS
                for work_env_row in original_work_envs:
                    destination_work_env_id = assets.create_work_env(work_env_row['software_id'], destination_variant_id)

                    # COPY WORK VERSIONS
                    work_versions = project.get_work_versions(work_env_row['id'])
                    new_work_versions = []
                    for work_version_row in work_versions:
                        new_version_id = assets.duplicate_version(work_version_row['id'], destination_work_env_id)
                        new_work_versions.append(new_version_id)

        team_client.refresh_team(environment.get_team_dns())
        gui_server.refresh_ui()