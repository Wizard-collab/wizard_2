# Update and export multiple stages

# Python modules
from PyQt6 import QtWidgets
import logging

# Wizard core modules
from wizard.core import assets
from wizard.core import project
from wizard.core import launch_batch
from wizard.core import tools
from wizard.core import team_client
from wizard.core import environment
from wizard.core import subtask
from wizard.core import deadline
from wizard.vars import ressources

logger = logging.getLogger(__name__)


name = "Propagate stages"
icon = ressources._destination_icon_
description = """Update and export every stage that contains the selected stages
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
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.info_label_1 = QtWidgets.QLabel(
            """Select the stage you want to propagate below""")
        self.main_layout.addWidget(self.info_label_1)

        self.project_tree = QtWidgets.QTreeWidget()
        self.project_tree.setObjectName('tree_widget')
        self.project_tree.setHeaderHidden(True)
        self.project_tree.setAlternatingRowColors(True)
        self.main_layout.addWidget(self.project_tree)

        self.comment_textEdit = QtWidgets.QTextEdit()
        self.comment_textEdit.setPlaceholderText("Your comment")
        self.comment_textEdit.setStyleSheet("background-color:rgba(0,0,0,50)")
        self.comment_textEdit.setFixedHeight(50)
        self.main_layout.addWidget(self.comment_textEdit)

        self.footer_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.footer_layout)

        self.info_label_2 = QtWidgets.QLabel("No stage selected")
        self.footer_layout.addWidget(self.info_label_2)

        self.deadline_checkbox = QtWidgets.QCheckBox("Deadline")
        self.footer_layout.addWidget(self.deadline_checkbox)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

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
            domain_item = QtWidgets.QTreeWidgetItem(
                self.project_tree.invisibleRootItem())
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
                        self.project_tree.setItemWidget(
                            stage_item, 0, check_box)
                        self.stages_dic[stage_row['id']] = dict()
                        self.stages_dic[stage_row['id']]['row'] = stage_row
                        self.stages_dic[stage_row['id']]['item'] = stage_item
                        self.stages_dic[stage_row['id']
                                        ]['check_box'] = check_box

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
        comment = self.comment_textEdit.toPlainText()
        command = "from ressources.batcher_scripts import propagate_stages\n"
        command += f"propagate_stages.main({stage_ids}, comment='''{comment}''')"
        on_deadline = self.deadline_checkbox.isChecked()
        if on_deadline:
            deadline.submit_job(command, "TEST BATCHER")
            return
        task = subtask.subtask(pycmd=command, print_stdout=False)
        task.start()


def main(stages_ids_list, comment=''):
    logger.info("Starting propagate stages batcher script")
    work_env_ids_list = []

    for stage_id in stages_ids_list:
        export_versions_ids = []
        exports_ids = project.get_stage_export_childs(stage_id, 'id')
        for export_id in exports_ids:
            export_version_id = project.get_default_export_version(
                export_id, 'id')
            if not export_version_id:
                continue
            destination_references_rows = project.get_export_version_destinations(
                export_version_id)
            for destination_reference_row in destination_references_rows:
                work_env_ids_list.append(
                    destination_reference_row['work_env_id'])
            destination_grouped_references_rows = project.get_grouped_export_version_destination(
                export_version_id)
            for destination_grouped_reference_row in destination_grouped_references_rows:
                referenced_group_rows = project.get_referenced_groups_by_group_id(
                    destination_grouped_reference_row['group_id'])
                for referenced_group_row in referenced_group_rows:
                    work_env_ids_list.append(
                        referenced_group_row['work_env_id'])
    if len(work_env_ids_list) == 0:
        logger.warning("Stage is not referenced")
        return
    export_work_envs(list(set(work_env_ids_list)), comment)


def export_work_envs(work_env_ids_list, comment=''):
    percent = 0.0
    percent_step = 100/len(work_env_ids_list)
    for work_env_id in work_env_ids_list:
        work_env_row = project.get_work_env_data(work_env_id)
        if not work_env_row:
            continue
        last_version_id = project.get_last_work_version(
            work_env_row['id'], 'id')[0]
        if not last_version_id:
            continue
        variant_row = project.get_variant_data(work_env_row['variant_id'])
        if not variant_row:
            continue
        stage_row = project.get_stage_data(variant_row['stage_id'])
        if not stage_row:
            continue
        asset_row = project.get_asset_data(stage_row['asset_id'])

        frange = [asset_row['inframe'], asset_row['outframe']]
        namespaces_list = []
        if stage_row['name'] in ['animation', 'cfx']:
            references_dic = assets.get_references_files(work_env_row['id'])
            for reference_type in references_dic.keys():
                if reference_type != 'rigging':
                    continue
                for reference_dic in references_dic[reference_type]:
                    namespaces_list.append(reference_dic['namespace'])

        settings_dic = dict()
        settings_dic['batch_type'] = 'export'
        settings_dic['frange'] = frange
        settings_dic['refresh_assets'] = 1
        settings_dic['nspace_list'] = namespaces_list
        settings_dic['comment'] = comment
        settings_dic['stage_to_export'] = stage_row['name']

        print(
            f"wizard_task_name:Exporting {asset_row['name']}/{stage_row['name']}")
        launch_batch.batch_export(last_version_id, settings_dic)
        tools.wait_for_child_processes()

        team_client.refresh_team(environment.get_team_dns())
        percent += percent_step
        print(f"wizard_task_percent:{percent}")
