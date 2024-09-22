# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import logging
import os
import sys
import subprocess
import traceback

# Wizard core modules
from wizard.core import user
from wizard.core import db_core
from wizard.core import db_utils
from wizard.core import environment
from wizard.core import repository
from wizard.core import project
from wizard.core import hooks
from wizard.core import stats
from wizard.core import tools
from wizard.core import create_project
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import warning_tooltip
from wizard.gui import logging_widget
from wizard.gui import psql_widget
from wizard.gui import repository_widget
from wizard.gui import user_log_widget
from wizard.gui import project_manager_widget

logger = logging.getLogger(__name__)

def get_app():
    os.environ["QT_SCALE_FACTOR"] = user.user().get_app_scale()

    if not os.path.isdir("binaries/ffmpeg/bin"):
        logger.error("FFmpeg not found")
        sys.exit()
    os.environ['PATH'] += os.pathsep + "binaries/ffmpeg/bin"

    app = QtWidgets.QApplication(sys.argv)

    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Black.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-BlackItalic.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Bold.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-BoldItalic.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Light.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-LightItalic.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Medium.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-MediumItalic.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Regular.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Thin.ttf")
    QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-ThinItalic.ttf")
    with open(ressources._stylesheet_, 'r') as f:
        app.setStyleSheet(f.read())
    QtCore.qInstallMessageHandler(customQtMsgHandler)
    return app

def customQtMsgHandler(msg_type, msg_log_context, msg_string):
    if msg_string.startswith('QWindowsWindow::setGeometry:'):
        pass
    else:
        print(msg_string)

def set_wizard_gui():
    print('Wizard Gui')
    environment.set_gui(1)

def set_wizard_cmd():
    print('Wizard CMD')
    environment.set_gui(0)

def set_pywizard():
    print('PyWizard')
    print('Enter Ctrl+Z to quit...')
    environment.set_gui(0)

def init_warning_tooltip():
    tooltip = warning_tooltip.warning_tooltip()
    custom_handler = logging_widget.custom_handler(long_formatter=False, parent=None)
    custom_handler.log_record.connect(tooltip.invoke)
    logging.getLogger().addHandler(custom_handler)
    return [tooltip, custom_handler]

def init_psql_dns(app, change_psql=False):
    if (not user.user().get_psql_dns()) or change_psql:
        if environment.is_gui():
                _psql_widget = psql_widget.psql_widget()
                if _psql_widget.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                    app.quit()
        else:
            while not user.user().get_psql_dns():
                psql_host = tools.flushed_input("PostgreSQL host : ")
                psql_port = tools.flushed_input("PostgreSQL port : ")
                psql_user = tools.flushed_input("PostgreSQL user : ")
                psql_password = tools.flushed_input("PostgreSQL password : ")
                user.user().set_psql_dns(psql_host,
                                        psql_port,
                                        psql_user,
                                        psql_password)

def init_repository(app, change_repo=False):
    if (not user.user().get_repository()) or change_repo:
        if environment.is_gui():
            _repository_widget = repository_widget.repository_widget()
            if _repository_widget.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                app.quit()
                return None
        else:
            while not user.user().get_repository():
                repository_name = tools.flushed_input("Repository : ")
                if repository.is_repository_database(repository_name):
                    user.user().set_repository(repository_name)

    db_core.db_access_singleton().set_repository(environment.get_repository())
    repository.add_ip_user()
    return 1

def init_user(app, log_user=False):
    if (not user.get_user()) or log_user:
        if environment.is_gui():
            _user_log_widget = user_log_widget.user_log_widget()
            if _user_log_widget.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                app.quit()
        else:
            while not user.get_user():
                do_create_user = tools.flushed_input('Create user (y/n) ? : ')
                if do_create_user == 'y':
                    user_name = tools.flushed_input('User name : ')
                    password = tools.flushed_input('Password : ')
                    email = tools.flushed_input('Email : ')
                    profile_picture = tools.flushed_input('Profile picture ( without any "\\" ) ( Optional ) : ')
                    administrator_pass = tools.flushed_input('Administrator pass ( Optional ) : ')
                    repository.create_user(user_name,
                                            password,
                                            email,
                                            administrator_pass,
                                            profile_picture)
                else:
                    user_name = tools.flushed_input('User name : ')
                    password = tools.flushed_input('Password : ')
                    user.log_user(user_name, password)
    user.user().get_team_dns()

def init_project(app, project_manager=False):
    if (not user.get_project()) or project_manager:
        if environment.is_gui():
            _project_manager_widget = project_manager_widget.project_manager_widget()
            if _project_manager_widget.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                app.quit()
        else:
            while not user.get_project():
                do_create_project = tools.flushed_input('Create project (y/n) ? : ')
                if do_create_project == 'y':
                    project_name = tools.flushed_input('Project name : ')
                    project_path = tools.flushed_input('Project path : ')
                    project_password = tools.flushed_input('Project password : ')
                    create_project.create_project(project_name, project_path, project_password)
                else:
                    project_name = tools.flushed_input('Project name : ')
                    project_password = tools.flushed_input('Project password : ')
                    user.log_project(project_name, project_password)

    db_core.db_access_singleton().set_project(environment.get_project_name())
    project.add_user(repository.get_user_row_by_name(environment.get_user(), 'id'))
    hooks.init_wizard_hooks()

def init_OCIO():
    OCIO = project.get_OCIO()
    if not OCIO:
        logger.info("No OCIO config file defined")
    else:
        environment.set_OCIO(OCIO)

def init_stats():
    stats.add_progress_event()
    stats_schedule = stats.schedule()
    stats_schedule.start()
    return stats_schedule

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    QtWidgets.QApplication.closeAllWindows()
    logger.critical(tb)
    command = f'error_handler.exe "{tb}"'
    if sys.argv[0].endswith('.py'):
        command = f'python error_handler.py "{tb}"'
    subprocess.Popen(command, start_new_session=True)