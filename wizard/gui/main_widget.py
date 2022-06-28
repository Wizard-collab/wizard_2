# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time
import os
import subprocess
import sys
import logging
import webbrowser

# Wizard modules
from wizard.vars import ressources
from wizard.core import application
from wizard.core import user
from wizard.core import project
from wizard.core import environment
from wizard.core import communicate
from wizard.core import launch
from wizard.core import team_client
from wizard.core import path_utils

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import tree_widget
from wizard.gui import references_widget
from wizard.gui import versions_widget
from wizard.gui import exports_widget
from wizard.gui import context_widget
from wizard.gui import tabs_widget
from wizard.gui import launcher_widget
from wizard.gui import wall_widget
from wizard.gui import user_widget
from wizard.gui import quotes_widget
from wizard.gui import shelf_widget
from wizard.gui import footer_widget
from wizard.gui import console_widget
from wizard.gui import header_widget
from wizard.gui import subtask_manager
from wizard.gui import team_widget
from wizard.gui import popup_wall_widget
from wizard.gui import user_preferences_widget
from wizard.gui import project_preferences_widget
from wizard.gui import softwares_widget
from wizard.gui import locks_widget
from wizard.gui import asset_tracking_widget
from wizard.gui import championship_widget
from wizard.gui import license_widget
from wizard.gui import production_manager_widget
from wizard.gui import confirm_widget
from wizard.gui import whatsnew_widget
from wizard.gui import groups_manager_widget
from wizard.gui import quotes_manager
from wizard.gui import table_viewer_widget

logger = logging.getLogger(__name__)

class main_widget(QtWidgets.QWidget):

    stop_threads = pyqtSignal(int)

    def __init__(self, parent=None):
        super(main_widget, self).__init__(parent)
        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - {environment.get_repository()[11:]} - {environment.get_project_name()}")

        self.tree_widget = tree_widget.tree_widget(self)
        self.shelf_widget = shelf_widget.shelf_widget(self)
        self.console_widget = console_widget.console_widget()
        self.user_preferences_widget = user_preferences_widget.user_preferences_widget()
        self.project_preferences_widget = project_preferences_widget.project_preferences_widget()
        self.asset_tracking_widget = asset_tracking_widget.asset_tracking_widget(self)
        self.launcher_widget = launcher_widget.launcher_widget(self)
        self.references_widget = references_widget.references_widget('work_env', self)
        self.versions_widget = versions_widget.versions_widget(self)
        self.exports_widget = exports_widget.exports_widget(self)
        self.context_widget = context_widget.context_widget(self)
        self.tabs_widget = tabs_widget.tabs_widget(self)
        self.wall_widget = wall_widget.wall_widget(self)
        self.popup_wall_widget = popup_wall_widget.popup_wall_widget()
        self.footer_widget = footer_widget.footer_widget(self)
        self.header_widget = header_widget.header_widget(self)
        self.subtask_manager = subtask_manager.subtask_manager()
        self.team_widget = team_widget.team_widget()
        self.team_client = team_client.team_client()
        self.gui_server = gui_server.gui_server()
        self.communicate_server = communicate.communicate_server()
        self.softwares_server = launch.softwares_server()
        self.softwares_widget = softwares_widget.softwares_widget()
        self.locks_widget = locks_widget.locks_widget()
        self.championship_widget = championship_widget.championship_widget()
        self.license_widget = license_widget.license_widget()
        self.whatsnew_widget = whatsnew_widget.whatsnew_widget()
        self.production_manager_widget = production_manager_widget.production_manager_widget()
        self.groups_manager_widget = groups_manager_widget.groups_manager_widget()
        self.quotes_manager = quotes_manager.quotes_manager()
        self.table_viewer_widget = table_viewer_widget.table_viewer_widget()
        self.build_ui()
        self.connect_functions()
        self.init_gui_server()
        self.init_communicate_server()
        self.init_team_client()
        self.init_popup_wall_widget()
        self.init_softwares_server()

    def whatsnew(self):
        current_build = application.get_version()['builds']
        last_user_build = user.user().get_user_build()
        show_whatsnew = user.user().get_show_whatsnew()

        if current_build != last_user_build:
            self.whatsnew_widget.toggle()
            user.user().set_user_build(current_build)
        else:
            if show_whatsnew:
                self.whatsnew_widget.toggle()

    def init_popup_wall_widget(self):
        self.popup_wall_widget.show()

    def init_gui_server(self):
        self.gui_server.start()

    def init_communicate_server(self):
        self.communicate_server.start()

    def init_team_client(self):
        self.team_client.start()

    def init_softwares_server(self):
        self.softwares_server.start()

    def init_contexts(self):
        self.tree_widget.get_context()
        self.tabs_widget.get_context()
        self.versions_widget.get_context()
        self.asset_tracking_widget.get_context()
        self.console_widget.get_context()

    def save_contexts(self):
        self.tree_widget.set_context()
        self.tabs_widget.set_context()
        self.versions_widget.set_context()
        self.wall_widget.set_context()
        self.asset_tracking_widget.set_context()
        self.console_widget.set_context()

    def connect_functions(self):
        self.header_widget.show_console.connect(self.console_widget.toggle)
        self.header_widget.show_subtask_manager.connect(self.subtask_manager.toggle)
        self.header_widget.show_user_preferences.connect(self.user_preferences_widget.toggle)
        self.header_widget.show_quotes_manager.connect(self.quotes_manager.toggle)
        self.header_widget.show_project_preferences.connect(self.project_preferences_widget.toggle)
        self.header_widget.show_production_manager.connect(self.production_manager_widget.toggle)
        self.header_widget.show_groups_manager.connect(self.groups_manager_widget.toggle)
        self.header_widget.show_tables_viewer.connect(self.table_viewer_widget.toggle)
        self.header_widget.close_signal.connect(self.close)
        self.header_widget.show_championship.connect(self.championship_widget.toggle)
        self.header_widget.show_pywizard.connect(self.show_pywizard)
        self.header_widget.show_license.connect(self.license_widget.toggle)
        self.header_widget.show_whatsnew.connect(self.whatsnew_widget.toggle)
        self.header_widget.show_documentation.connect(self.show_documentation)

        self.tree_widget.stage_changed_signal.connect(self.stage_changed)
        self.tree_widget.launch_stage_signal.connect(self.launcher_widget.launch)
        self.context_widget.work_env_changed_signal.connect(self.work_env_changed)
        self.context_widget.variant_changed_signal.connect(self.variant_changed)
        self.versions_widget.version_changed_signal.connect(self.launcher_widget.focus_version)
        self.tabs_widget.currentChanged.connect(self.tab_changed)
        self.footer_widget.show_console.connect(self.console_widget.toggle)
        self.footer_widget.show_wall.connect(self.wall_widget.toggle)
        self.footer_widget.show_subtask_manager.connect(self.subtask_manager.toggle)
        self.footer_widget.connect_team.connect(self.init_team_client)
        self.footer_widget.show_team_widget.connect(self.team_widget.toggle)
        self.footer_widget.show_user_preferences.connect(self.user_preferences_widget.toggle)
        self.footer_widget.refresh_signal.connect(self.refresh)
        self.footer_widget.show_softwares_widget.connect(self.softwares_widget.toggle)
        self.footer_widget.show_locks_widget.connect(self.locks_widget.toggle)
        self.console_widget.notification.connect(self.footer_widget.update_console_button)
        self.wall_widget.notification.connect(self.footer_widget.update_wall_button)
        self.wall_widget.popup.connect(self.popup_wall_widget.add_popup)
        self.subtask_manager.global_status_signal.connect(self.footer_widget.update_subtask_manager_button)
        self.references_widget.focus_export.connect(self.focus_export_version)
        self.references_widget.focus_on_group_signal.connect(self.focus_on_group)

        self.team_client.team_connection_status_signal.connect(self.footer_widget.set_team_connection)
        self.team_client.team_connection_status_signal.connect(self.team_widget.set_team_connection)
        self.team_client.refresh_signal.connect(self.refresh)
        self.team_client.new_user_signal.connect(self.team_widget.add_user)
        self.team_client.remove_user_signal.connect(self.team_widget.remove_user)

        self.gui_server.refresh_signal.connect(self.refresh)
        self.gui_server.refresh_team_signal.connect(self.team_client.refresh_team)
        self.gui_server.restart_signal.connect(self.restart)
        self.gui_server.tooltip_signal.connect(self.footer_widget.update_tooltip)
        self.gui_server.stdout_signal.connect(self.update_stdout)
        self.gui_server.focus_instance_signal.connect(self.focus_instance)
        self.gui_server.export_version_focus_signal.connect(self.focus_export_version)
        self.gui_server.work_version_focus_signal.connect(self.focus_work_version)
        self.gui_server.save_popup_signal.connect(self.popup_wall_widget.add_save_popup)
        self.gui_server.raise_ui_signal.connect(self.raise_window)
        self.gui_server.popup_signal.connect(self.popup_wall_widget.add_custom_popup)

    def show_documentation(self):
        webbrowser.open_new_tab(ressources._documentation_url_)

    def show_pywizard(self):
        if sys.argv[0].endswith('.py'):
            subprocess.Popen('python PyWizard.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif sys.argv[0].endswith('.exe'):
            path_utils.startfile('PyWizard.exe')

    def restart(self):
        self.close()
        command = 'wizard.exe'
        if sys.argv[0].endswith('.py'):
            command = 'python app.py'
        subprocess.Popen(command, shell=True)

    def raise_window(self):
        self.raise_()
        self.show()
        self.activateWindow()

    def focus_export_version(self, export_version_id):
        export_version_row = project.get_export_version_data(export_version_id)
        if export_version_row is not None:
            self.tree_widget.focus_instance(('stage', export_version_row['stage_id']))
            self.tabs_widget.setCurrentIndex(self.exports_tab_index)
            self.exports_widget.focus_export_version(export_version_id)

    def focus_work_version(self, work_version_id):
        work_version_row = project.get_version_data(work_version_id)
        work_env_row = project.get_work_env_data(work_version_row['work_env_id'])
        variant_row = project.get_variant_data(work_env_row['variant_id'])
        stage_row = project.get_stage_data(variant_row['stage_id'])
        if stage_row is not None:
            self.tree_widget.focus_instance(('stage', stage_row['id']))
            self.tabs_widget.setCurrentIndex(self.work_versions_tab_index)
            self.context_widget.focus_variant(variant_row['id'])
            self.context_widget.focus_work_env(work_env_row['id'])
            self.versions_widget.focus_work_version(work_version_id)

    def focus_on_group(self, group_id):
        self.groups_manager_widget.toggle()
        self.groups_manager_widget.set_group_id(group_id)

    def focus_instance(self, instance_tuple):
        instance_type = instance_tuple[0]
        instance_id = instance_tuple[-1]
        if instance_type == 'domain':
            self.focus_domain(instance_id)
        elif instance_type == 'category':
            self.focus_category(instance_id)
        elif instance_type == 'asset':
            self.focus_asset(instance_id)
        elif instance_type == 'stage':
            self.focus_stage(instance_id)
        elif instance_type == 'variant':
            self.focus_variant(instance_id)

    def focus_domain(self, domain_id):
        self.tree_widget.focus_instance(('domain', domain_id))

    def focus_category(self, category_id):
        self.tree_widget.focus_instance(('category', category_id))

    def focus_asset(self, asset_id):
        self.tree_widget.focus_instance(('asset', asset_id))

    def focus_stage(self, stage_id):
        self.tree_widget.focus_instance(('stage', stage_id))

    def focus_variant(self, variant_id):
        self.tree_widget.focus_instance(('variant', variant_id))
        self.context_widget.focus_variant(variant_id)

    def update_stdout(self, tuple):
        self.footer_widget.handle_record(tuple)
        self.console_widget.handle_record(tuple)

    def stage_changed(self, stage_id):
        self.context_widget.change_stage(stage_id)
        self.asset_tracking_widget.change_stage(stage_id)

    def variant_changed(self, variant_id):
        self.exports_widget.change_variant(variant_id)

    def work_env_changed(self, work_env_id):
        self.versions_widget.change_work_env(work_env_id)
        self.launcher_widget.change_work_env(work_env_id)
        self.references_widget.change_work_env(work_env_id)

    def tab_changed(self):
        self.references_widget.refresh()
        self.versions_widget.refresh()
        self.exports_widget.refresh()

    def quit_threads(self):
        self.stop_threads.emit(1)
        self.gui_server.stop()
        self.team_client.stop()
        self.header_widget.quotes_widget.timer.stop()
        self.footer_widget.hardware_infos_widget.timer.stop()
        self.communicate_server.stop()
        self.subtask_manager.tasks_server.stop()
        self.softwares_server.stop()

    def prepare_close(self):
        close = False
        if launch.get() == []:
            close = True
        else:
            self.confirm_widget = confirm_widget.confirm_widget('Softwares are running...\nKill all softwares ?',
                                                                accept_text='Kill')
            if self.confirm_widget.exec_() == QtWidgets.QDialog.Accepted:
                launch.kill_all()
                close = True
        if close:
            self.quit_threads()
            self.save_contexts()
        return close

    def closeEvent(self, event):
        if self.prepare_close():
            QtWidgets.QApplication.closeAllWindows()
        else:
            event.ignore()

    def refresh(self):
        start_time = time.time()
        self.tree_widget.refresh()
        self.context_widget.refresh()
        self.launcher_widget.refresh()
        self.header_widget.refresh()
        self.references_widget.refresh()
        self.versions_widget.refresh()
        self.exports_widget.refresh()
        self.wall_widget.refresh()
        self.softwares_widget.refresh()
        self.locks_widget.refresh()
        self.asset_tracking_widget.refresh()
        self.production_manager_widget.refresh()
        self.table_viewer_widget.refresh()
        self.shelf_widget.refresh()
        self.groups_manager_widget.refresh()
        self.project_preferences_widget.refresh()
        self.quotes_manager.refresh()
        self.footer_widget.update_refresh_time(start_time)

    def build_ui(self):
        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(0,0,0,0)
        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setObjectName('main_widget')
        self.main_widget_layout.addWidget(self.main_widget)
        self.setLayout(self.main_widget_layout)
        
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(1)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_widget.setLayout(self.main_layout)

        self.main_layout.addWidget(self.header_widget)
        self.main_layout.addWidget(self.shelf_widget)

        self.contents_widget = QtWidgets.QWidget()
        self.contents_widget.setObjectName('main_widget')
        self.contents_layout = QtWidgets.QHBoxLayout()
        self.contents_layout.setSpacing(1)
        self.contents_layout.setContentsMargins(0,0,0,0)
        self.contents_widget.setLayout(self.contents_layout)
        self.main_layout.addWidget(self.contents_widget)

        self.contents_layout.addWidget(self.tree_widget)

        self.contents_1_widget = QtWidgets.QWidget()
        self.contents_1_widget.setObjectName('main_widget')
        self.contents_1_layout = QtWidgets.QHBoxLayout()
        self.contents_1_layout.setSpacing(1)
        self.contents_1_layout.setContentsMargins(0,0,0,0)
        self.contents_1_widget.setLayout(self.contents_1_layout)
        self.contents_layout.addWidget(self.contents_1_widget)

        self.contents_2_widget = QtWidgets.QWidget()
        self.contents_2_widget.setObjectName('main_widget')
        self.contents_2_layout = QtWidgets.QVBoxLayout()
        self.contents_2_layout.setSpacing(1)
        self.contents_2_layout.setContentsMargins(0,0,0,0)
        self.contents_2_widget.setLayout(self.contents_2_layout)
        self.contents_1_layout.addWidget(self.contents_2_widget)

        self.contents_2_layout.addWidget(self.context_widget)
        self.contents_2_layout.addWidget(self.tabs_widget)
        self.references_tab_index = self.tabs_widget.addTab(self.references_widget, QtGui.QIcon(ressources._references_icon_), 'References')
        self.work_versions_tab_index = self.tabs_widget.addTab(self.versions_widget, QtGui.QIcon(ressources._work_icon_), 'Work versions')
        self.exports_tab_index = self.tabs_widget.addTab(self.exports_widget, QtGui.QIcon(ressources._exports_icon_), 'Exports')
        
        self.contents_3_widget = QtWidgets.QWidget()
        self.contents_3_widget.setObjectName('main_widget')
        self.contents_3_layout = QtWidgets.QVBoxLayout()
        self.contents_3_layout.setSpacing(1)
        self.contents_3_layout.setContentsMargins(0,0,0,0)
        self.contents_3_widget.setLayout(self.contents_3_layout)
        self.contents_1_layout.addWidget(self.contents_3_widget)

        self.contents_3_layout.addWidget(self.asset_tracking_widget)
        self.contents_3_layout.addWidget(self.launcher_widget)
        
        self.contents_layout.addWidget(self.wall_widget)
        self.wall_widget.setVisible(0)

        self.main_layout.addWidget(self.footer_widget)
