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

name = "Export cameras"
icon = ressources._tool_batch_camera_
description = """Export the camera for each selected stage, if a camrig is referenced
"""

class widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(widget, self).__init__(parent)
        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('transparent_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.info_label_1 = QtWidgets.QLabel("""Select the stages to export cameras from and
then click on execute""")
        self.main_layout.addWidget(self.info_label_1)

        self.project_tree = QtWidgets.QTreeWidget()
        self.project_tree.setObjectName('tree_widget')
        self.project_tree.setHeaderHidden(True)
        self.project_tree.setAlternatingRowColors(True)
        self.main_layout.addWidget(self.project_tree)

        self.footer_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.footer_layout)

        self.info_label_2 = QtWidgets.QLabel("No stage selected")
        self.footer_layout.addWidget(self.info_label_2)

        self.refresh_assets_checkbox = QtWidgets.QCheckBox("Refresh assets")
        self.footer_layout.addWidget(self.refresh_assets_checkbox)

        self.deadline_checkbox = QtWidgets.QCheckBox("Deadline")
        self.footer_layout.addWidget(self.deadline_checkbox)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.execute_button = QtWidgets.QPushButton("Execute")
        self.execute_button.setObjectName("blue_button")
        self.main_layout.addWidget(self.execute_button)

    def fill_ui(self):
        self.fill_project_tree()

    def fill_project_tree(self):
        self.stages_dic = dict()
        all_domains = project.get_domains()
        for domain_row in all_domains:
            categories = project.get_domain_childs(domain_row['id'])
            domain_item = QtWidgets.QTreeWidgetItem(self.project_tree.invisibleRootItem())
            domain_item.setText(0, domain_row['name'])
            for category_row in categories:
                assets = project.get_category_childs(category_row['id'])
                category_item = QtWidgets.QTreeWidgetItem(domain_item)
                category_item.setText(0, category_row['name'])
                for asset_row in assets:
                    stages = project.get_asset_childs(asset_row['id'])
                    asset_item = QtWidgets.QTreeWidgetItem(category_item)
                    asset_item.setText(0, asset_row['name'])
                    for stage_row in stages:
                        stage_item = QtWidgets.QTreeWidgetItem(asset_item)
                        check_box = QtWidgets.QCheckBox(stage_row['name'])
                        check_box.stateChanged.connect(self.refresh)
                        self.project_tree.setItemWidget(stage_item, 0, check_box)
                        self.stages_dic[stage_row['id']] = dict()
                        self.stages_dic[stage_row['id']]['row'] = stage_row
                        self.stages_dic[stage_row['id']]['item'] = stage_item
                        self.stages_dic[stage_row['id']]['check_box'] = check_box

    def refresh(self):
        stage_ids = self.get_selected_stages_ids()
        if len(stage_ids) == 0:
            self.info_label_2.setText("No stages selected")
        self.info_label_2.setText(f"{len(stage_ids)} stages selected")

    def connect_functions(self):
        self.execute_button.clicked.connect(self.execute)

    def get_selected_stages_ids(self):
        stage_ids = []
        for stage_id in self.stages_dic.keys():
            if not self.stages_dic[stage_id]['check_box'].isChecked():
                continue
            stage_ids.append(stage_id)
        return stage_ids

    def execute(self):
        stage_ids = self.get_selected_stages_ids()
        refresh_assets = self.refresh_assets_checkbox.isChecked()
        command = "from ressources.batcher_scripts import export_cameras\n"
        command += f"export_cameras.main({stage_ids}, {refresh_assets})"
        on_deadline = self.deadline_checkbox.isChecked()
        if on_deadline:
            deadline.submit_job(command, "TEST BATCHER")
            return
        task = subtask.subtask(pycmd=command, print_stdout=False)
        task.start()

def main(stages_ids_list, refresh_assets):
    logger.info("Starting update_and_export batcher script")
    percent = 0.0
    percent_step = 100/len(stages_ids_list)
    for stage_id in stages_ids_list:
        stage_row = project.get_stage_data(stage_id)
        if not stage_row:
            logger.info(f"Stage id {stage_row['name']} not found, skipping.")
            continue
        asset_row = project.get_asset_data(stage_row['asset_id'])
        default_variant_row = project.get_variant_data(stage_row['default_variant_id'])
        if not default_variant_row:
            logger.info(f"Default variant of {stage_row['name']} not found, skipping.")
            continue
        default_work_env_row = project.get_work_env_data(default_variant_row['default_work_env_id'])
        if not default_work_env_row:
            logger.info(f"Default work environment of {stage_row['name']}/{default_variant_row['name']} not found, skipping.")
            continue
        last_version_id = project.get_last_work_version(default_work_env_row['id'], 'id')[0]
        if not last_version_id:
            logger.info(f"No work version found for {stage_row['name']}/{default_variant_row['name']}/{default_work_env_row['name']}, skipping.")
            continue

        frange = [asset_row['inframe'], asset_row['outframe']]
        namespaces_list = []
        references_dic = assets.get_references_files(default_work_env_row['id'])
        for reference_type in references_dic.keys():
            if reference_type not in ['camrig']:
                continue
            for reference_dic in references_dic[reference_type]: 
                namespaces_list.append(reference_dic['namespace'])

        settings_dic = dict()
        settings_dic['batch_type'] = 'export'
        settings_dic['frange'] = frange
        settings_dic['refresh_assets'] = refresh_assets
        settings_dic['nspace_list'] = namespaces_list
        settings_dic['stage_to_export'] = "camera"

        print(f"wizard_task_name:Exporting camera for {asset_row['name']}/{stage_row['name']}")
        launch_batch.batch_export(last_version_id, settings_dic)
        tools.wait_for_child_processes()

        team_client.refresh_team(environment.get_team_dns())
        percent+=percent_step
        print(f"wizard_task_percent:{percent}")