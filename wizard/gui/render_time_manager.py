# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtGui
import time

# Wizard core modules
from wizard.vars import ressources
from wizard.core import project
from wizard.core import tools
from wizard.core import stats

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server


class render_time_manager_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(render_time_manager_widget, self).__init__(parent)
        self.main_progress_widget = main_progress_widget()
        self.infos_subwidget = infos_subwidget()
        self.success_subwidget = success_subwidget()
        self.settings_subwidget = settings_subwidget()
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 11, 11, 11)
        self.setLayout(self.main_layout)

        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.horizontal_layout)

        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.horizontal_layout.addLayout(self.vertical_layout)

        self.vertical_layout.addWidget(self.main_progress_widget)
        self.vertical_layout.addWidget(self.infos_subwidget)
        self.vertical_layout.addWidget(self.settings_subwidget)

        self.vertical_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.horizontal_layout.addWidget(self.success_subwidget)

        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.footer_layout)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.footer_layout.addWidget(self.refresh_label)

    def showEvent(self, event):
        self.refresh()

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f" refresh : {refresh_time}s")

    def refresh(self):
        if self.isVisible():
            start_time = time.perf_counter()
            self.main_progress_widget.refresh()
            self.infos_subwidget.refresh()
            self.success_subwidget.refresh()
            self.settings_subwidget.refresh()
            self.update_refresh_time(start_time)


class main_progress_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(main_progress_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setFixedWidth(450)
        self.setObjectName('round_frame')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(6)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.main_layout)

        self.progress_bar = gui_utils.RoundProgress()
        self.progress_bar.setFixedSize(60, 60)
        self.progress_bar.lineWidth = 12
        self.progress_bar.setValue(0)
        self.progress_bar.setChunckColor('#d7d7d7')
        self.main_layout.addWidget(self.progress_bar)

        self.main_layout.addWidget(gui_utils.vertical_separator())

        self.text_widget = QtWidgets.QWidget()
        self.text_widget_layout = QtWidgets.QVBoxLayout()
        self.text_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.text_widget_layout.setSpacing(2)
        self.text_widget.setLayout(self.text_widget_layout)
        self.main_layout.addWidget(self.text_widget)

        self.title_label = QtWidgets.QLabel('Render progress')
        self.title_label.setObjectName('title_label')
        self.text_widget_layout.addWidget(self.title_label)

        self.progress_label = QtWidgets.QLabel()
        self.progress_label.setObjectName('title_label_gray')
        self.text_widget_layout.addWidget(self.progress_label)

        self.infos_label = QtWidgets.QLabel()
        self.text_widget_layout.addWidget(self.infos_label)

        self.text_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

    def refresh(self):
        all_frames = stats.get_all_frames()
        rendered_frames = stats.get_rendered_frames()
        if all_frames == 0:
            return
        rendered_percent = 100*(rendered_frames/all_frames)
        frames_left = all_frames-rendered_frames

        self.progress_label.setText(f"{int(rendered_percent)}%")
        self.infos_label.setText(
            f"{rendered_frames} frames rendered / {all_frames} frames\n{frames_left} frames to render")
        self.progress_bar.setValue(int(rendered_percent))
        if rendered_percent < 100:
            self.progress_bar.setChunckColor('#b6864e')
        else:
            self.progress_bar.setChunckColor('#7ca657')


class settings_subwidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(settings_subwidget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setFixedWidth(450)
        self.setObjectName('round_frame')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.content_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        self.machines_count_settings_layout = QtWidgets.QHBoxLayout()
        self.machines_count_settings_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.machines_count_settings_layout)

        self.render_nodes_icon = QtWidgets.QLabel()
        self.render_nodes_icon.setPixmap(QtGui.QIcon(
            ressources._render_node_icon_).pixmap(30))
        self.machines_count_settings_layout.addWidget(self.render_nodes_icon)

        self.machine_count_spinBox = QtWidgets.QSpinBox()
        self.machine_count_spinBox.setRange(1, 1000000)
        self.machine_count_spinBox.setFixedWidth(100)
        self.machine_count_spinBox.setButtonSymbols(
            QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.machines_count_settings_layout.addWidget(
            self.machine_count_spinBox)

        self.machines_count_label = QtWidgets.QLabel('render nodes')
        self.machines_count_settings_layout.addWidget(
            self.machines_count_label)

        self.machines_count_settings_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.render_time_settings_layout = QtWidgets.QHBoxLayout()
        self.render_time_settings_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.render_time_settings_layout)

        self.render_time_icon = QtWidgets.QLabel()
        self.render_time_icon.setPixmap(QtGui.QIcon(
            ressources._render_time_icon_).pixmap(30))
        self.render_time_settings_layout.addWidget(self.render_time_icon)

        self.render_time_spinBox = QtWidgets.QSpinBox()
        self.render_time_spinBox.setRange(1, 10000000)
        self.render_time_spinBox.setFixedWidth(100)
        self.render_time_spinBox.setButtonSymbols(
            QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.render_time_settings_layout.addWidget(self.render_time_spinBox)

        self.render_time_label = QtWidgets.QLabel('min / frame')
        self.render_time_settings_layout.addWidget(self.render_time_label)

        self.render_time_settings_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

    def refresh(self):
        mean_render_time = project.get_mean_render_time()
        render_nodes_number = project.get_render_nodes_number()
        self.machine_count_spinBox.setValue(render_nodes_number)

        render_time_in_min = int(mean_render_time/60)
        self.render_time_spinBox.setValue(render_time_in_min)

    def connect_functions(self):
        self.machine_count_spinBox.valueChanged.connect(self.set_machine_count)
        self.render_time_spinBox.valueChanged.connect(self.set_render_time)

    def set_machine_count(self, machines_count):
        project.set_render_nodes_number(machines_count)
        gui_server.refresh_ui()

    def set_render_time(self, render_time):
        render_time_in_seconds = int(render_time*60)
        project.set_mean_render_time(render_time_in_seconds)
        gui_server.refresh_ui()


class infos_subwidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(infos_subwidget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setFixedWidth(450)
        self.setObjectName('round_frame')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.content_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        self.header_layout = QtWidgets.QFormLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addLayout(self.header_layout)

        self.render_nodes_icon = QtWidgets.QLabel()
        self.render_nodes_icon.setPixmap(QtGui.QIcon(
            ressources._render_node_icon_).pixmap(30))

        self.render_nodes_label = QtWidgets.QLabel()
        self.header_layout.addRow(
            self.render_nodes_icon, self.render_nodes_label)

        self.frames_left_icon = QtWidgets.QLabel()
        self.frames_left_icon.setPixmap(
            QtGui.QIcon(ressources._frame_icon_).pixmap(30))

        self.frames_left_label = QtWidgets.QLabel()
        self.header_layout.addRow(
            self.frames_left_icon, self.frames_left_label)

        self.render_time_icon = QtWidgets.QLabel()
        self.render_time_icon.setPixmap(QtGui.QIcon(
            ressources._render_time_icon_).pixmap(30))

        self.frame_time_label = QtWidgets.QLabel()
        self.header_layout.addRow(self.render_time_icon, self.frame_time_label)

        self.total_time_icon = QtWidgets.QLabel()
        self.total_time_icon.setPixmap(QtGui.QIcon(
            ressources._render_time_icon_).pixmap(30))

        self.total_time_label = QtWidgets.QLabel()
        self.header_layout.addRow(self.total_time_icon, self.total_time_label)

        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

    def refresh(self):
        all_frames = stats.get_all_frames()
        rendered_frames = stats.get_rendered_frames()
        frames_left = all_frames-rendered_frames
        mean_render_time = project.get_mean_render_time()
        render_nodes_number = project.get_render_nodes_number()
        estimated_render_time = tools.convert_seconds_to_string_time(
            (frames_left*mean_render_time)/render_nodes_number)

        self.render_nodes_label.setText(f"{render_nodes_number} render nodes")
        self.frame_time_label.setText(
            f"{tools.convert_seconds_to_string_time(mean_render_time)}/frame")
        self.total_time_label.setText(
            f"{estimated_render_time} to render all ( With {render_nodes_number} render nodes)")
        self.frames_left_label.setText(f"{frames_left} frames to render")


class success_subwidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(success_subwidget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.content_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        self.success_label = QtWidgets.QLabel()
        self.success_label.setObjectName("title_label_2")
        self.content_layout.addWidget(self.success_label)

        self.content_layout.addWidget(gui_utils.separator())

        self.time_left_label = QtWidgets.QLabel()
        self.content_layout.addWidget(self.time_left_label)

        self.time_left_bar = gui_utils.QProgressBar()
        self.time_left_bar.setStyleSheet(
            'QProgressBar{background-color:transparent;}QProgressBar::chunk{background-color:#ffffff;}')
        self.content_layout.addWidget(self.time_left_bar)

        self.render_time_label = QtWidgets.QLabel()
        self.content_layout.addWidget(self.render_time_label)

        self.render_time_bar = gui_utils.QProgressBar()
        self.render_time_bar.setStyleSheet(
            'QProgressBar{background-color:transparent;}QProgressBar::chunk{background-color:#ffffff;}')
        self.content_layout.addWidget(self.render_time_bar)

        self.content_layout.addWidget(gui_utils.separator())

        self.optimisation_label = QtWidgets.QLabel("How to optimize ?")
        self.optimisation_label.setObjectName("title_label_2")
        self.content_layout.addWidget(self.optimisation_label)

        self.grid_layout = QtWidgets.QGridLayout()
        self.content_layout.addLayout(self.grid_layout)

        self.machines_icon_label = QtWidgets.QLabel()
        self.machines_icon_label.setPixmap(QtGui.QIcon(
            ressources._render_node_icon_).pixmap(30))
        self.grid_layout.addWidget(self.machines_icon_label, 1, 0)

        self.machines_status_label = QtWidgets.QLabel()
        self.grid_layout.addWidget(self.machines_status_label, 1, 1)

        self.machines_optimisation_label = QtWidgets.QLabel()
        self.machines_optimisation_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.grid_layout.addWidget(self.machines_optimisation_label, 1, 2)

        self.render_time_icon_label = QtWidgets.QLabel()
        self.render_time_icon_label.setPixmap(
            QtGui.QIcon(ressources._render_time_icon_).pixmap(30))
        self.grid_layout.addWidget(self.render_time_icon_label, 2, 0)

        self.render_time_status_label = QtWidgets.QLabel()
        self.grid_layout.addWidget(self.render_time_status_label, 2, 1)

        self.render_time_optimisation_label = QtWidgets.QLabel()
        self.grid_layout.addWidget(self.render_time_optimisation_label, 2, 2)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

    def refresh(self):
        time_left = project.get_deadline()-time.time()
        all_frames = stats.get_all_frames()
        if all_frames == 0:
            return
        rendered_frames = stats.get_rendered_frames()
        rendered_percent = 100*(rendered_frames/all_frames)
        frames_left = all_frames-rendered_frames
        mean_render_time = project.get_mean_render_time()
        render_nodes_number = project.get_render_nodes_number()
        render_time_1_machine = tools.convert_seconds_to_string_time(
            frames_left*mean_render_time)
        estimated_render_time = tools.convert_seconds_to_string_time(
            (frames_left*mean_render_time)/render_nodes_number)
        MACHINES_REQUIRED_TO_FINISH = round(
            (frames_left*mean_render_time)/time_left)
        RENDER_TIME_REQUIRED_TO_FINISH = time_left/frames_left*render_nodes_number

        render_time = (frames_left*mean_render_time)/render_nodes_number

        color = '#7ca657'
        success_text = "Your project should render on time"
        if (render_time > time_left):
            success_text = "Your project will not render on time"
            color = '#d16666'
        self.success_label.setText(success_text)
        self.success_label.setStyleSheet(f'color:{color}')
        self.time_left_label.setText(
            f"{tools.convert_seconds_to_string_time(time_left)} until deadline")
        self.render_time_label.setText(
            f"{tools.convert_seconds_to_string_time(render_time)} to render all")

        if render_time < time_left:
            render_time_proportion = int(render_time/time_left*100)
            self.time_left_bar.setValue(100)
            self.render_time_bar.setValue(render_time_proportion)
            self.render_time_bar.setStyleSheet(
                'QProgressBar{background-color:transparent;}QProgressBar::chunk{background-color:#7ca657;}')
        else:
            time_left_proportion = int(time_left/render_time*100)
            self.render_time_bar.setValue(100)
            self.time_left_bar.setValue(time_left_proportion)
            self.render_time_bar.setStyleSheet(
                'QProgressBar{background-color:transparent;}QProgressBar::chunk{background-color:#d16666;}')

        if MACHINES_REQUIRED_TO_FINISH < render_nodes_number:
            self.machines_status_label.setPixmap(
                QtGui.QIcon(ressources._down_arrow_).pixmap(30))
            self.machines_optimisation_label.setText(
                f"You can decrease the render nodes number to {MACHINES_REQUIRED_TO_FINISH}")
        elif MACHINES_REQUIRED_TO_FINISH > render_nodes_number:
            self.machines_status_label.setPixmap(
                QtGui.QIcon(ressources._up_arrow_).pixmap(30))
            self.machines_optimisation_label.setText(
                f"You can increase the render nodes number to {MACHINES_REQUIRED_TO_FINISH}")
        else:
            self.machines_status_label.setPixmap(
                QtGui.QIcon(ressources._check_icon_).pixmap(30))
            self.machines_optimisation_label.setText(
                f"Render nodes count looks optimised")

        if RENDER_TIME_REQUIRED_TO_FINISH < mean_render_time:
            self.render_time_status_label.setPixmap(
                QtGui.QIcon(ressources._down_arrow_).pixmap(30))
            self.render_time_optimisation_label.setText(
                f"You can decrease the render time to {tools.convert_seconds_to_string_time(RENDER_TIME_REQUIRED_TO_FINISH)} / frame")
        else:
            self.render_time_status_label.setPixmap(
                QtGui.QIcon(ressources._check_icon_).pixmap(30))
            self.render_time_optimisation_label.setText(
                f"Render time looks optimised")
