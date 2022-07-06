# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QPieSeries
import statistics
import time
import json
import copy
import logging

# Wizard core modules
from wizard.vars import ressources
from wizard.vars import assets_vars
from wizard.core import environment
from wizard.core import repository
from wizard.core import project
from wizard.core import tools
from wizard.core import image
from wizard.core import assets
from wizard.core import stats

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import chart_utils

class overview_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(overview_widget, self).__init__(parent)
        self.main_progress_widget = main_progress_widget()
        self.user_progress_widget = user_progress_widget()
        self.progress_overview_widget = progress_overview_widget()
        self.progress_curves_widget = progress_curves_widget()
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,11,11,11)
        self.setLayout(self.main_layout)

        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.horizontal_layout)

        self.vertical_widget_1 = QtWidgets.QWidget()
        self.vertical_widget_1.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.vertical_widget_1.setObjectName('transparent_widget')
        self.vertical_layout_1 = QtWidgets.QVBoxLayout()
        self.vertical_layout_1.setContentsMargins(0,0,0,0)
        self.vertical_widget_1.setLayout(self.vertical_layout_1)
        self.horizontal_layout.addWidget(self.vertical_widget_1)

        self.vertical_layout_1.addWidget(self.main_progress_widget)
        self.vertical_layout_1.addWidget(self.progress_overview_widget)

        self.project_quickstats_widget = project_quickstats_widget()
        self.vertical_layout_1.addWidget(self.project_quickstats_widget)

        self.vertical_layout_1.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.vertical_layout_2 = QtWidgets.QVBoxLayout()
        self.vertical_layout_2.setContentsMargins(0,0,0,0)
        self.horizontal_layout.addLayout(self.vertical_layout_2)

        self.vertical_layout_2.addWidget(self.user_progress_widget)
        self.vertical_layout_2.addWidget(self.progress_curves_widget)

        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.footer_layout)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.footer_layout.addWidget(self.refresh_label)

    def showEvent(self, event):
        self.refresh()

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
        self.refresh_label.setText(f" refresh : {refresh_time}s")

    def refresh(self):
        if self.isVisible():
            start_time = time.time()
            self.progress_overview_widget.refresh()
            self.main_progress_widget.refresh()
            self.user_progress_widget.refresh()
            self.progress_curves_widget.refresh()
            self.project_quickstats_widget.refresh()
            self.update_refresh_time(start_time)

class project_quickstats_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(project_quickstats_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(20,20,20,20)
        self.main_layout.setSpacing(12)
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel('Project stats')
        self.title_label.setObjectName('title_label')
        self.main_layout.addWidget(self.title_label)

        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setSpacing(6)
        self.main_layout.addLayout(self.grid_layout)

        self.assignments_widget = quickstats_widget()
        self.assignments_widget.description_label.setText("Tasks")
        self.grid_layout.addWidget(self.assignments_widget, 0, 0)

        self.total_work_time_widget = quickstats_widget()
        self.total_work_time_widget.description_label.setText("Total work time")
        self.grid_layout.addWidget(self.total_work_time_widget, 0, 1)

        self.average_work_time_widget = quickstats_widget()
        self.average_work_time_widget.description_label.setText("Time per asset")
        self.grid_layout.addWidget(self.average_work_time_widget, 1, 0)

        self.all_versions_widget = quickstats_widget()
        self.all_versions_widget.description_label.setText("Work versions")
        self.grid_layout.addWidget(self.all_versions_widget, 1, 1)

        self.all_exports_widget = quickstats_widget()
        self.all_exports_widget.description_label.setText("Exports")
        self.grid_layout.addWidget(self.all_exports_widget, 2, 0)

        self.tasks_done_widget = quickstats_widget()
        self.tasks_done_widget.description_label.setText("Tasks done")
        self.grid_layout.addWidget(self.tasks_done_widget, 2, 1)

    def refresh(self):
        stage_rows = project.get_all_stages()
        all_work_times = []
        tasks_done = 0
        total_work_time = 0

        stages_dic = dict()

        for stage_row in stage_rows:
            if stage_row['domain_id'] != 2:
                all_work_times.append(stage_row['work_time'])
                total_work_time += stage_row['work_time']
                if stage_row['state'] == 'done':
                    tasks_done+=1

        work_time_mean = statistics.mean(all_work_times)
        self.assignments_widget.stat_label.setText(f"{len(all_work_times)}")
        self.total_work_time_widget.stat_label.setText(f"{tools.convert_seconds_to_string_time(total_work_time)}")
        self.average_work_time_widget.stat_label.setText(f"{tools.convert_seconds_to_string_time(work_time_mean)}")

        all_work_versions = project.get_all_work_versions('id')
        self.all_versions_widget.stat_label.setText(f"{len(all_work_versions)}")

        all_exports = project.get_all_export_versions('id')
        self.all_exports_widget.stat_label.setText(f"{len(all_exports)}")

        self.tasks_done_widget.stat_label.setText(f"{tasks_done}/{len(all_work_times)}")

class main_progress_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(main_progress_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(12)
        self.main_layout.setContentsMargins(20,20,20,20)
        self.setLayout(self.main_layout)

        self.progress_bar = gui_utils.RoundProgress()
        self.progress_bar.setFixedSize(60,60)
        self.progress_bar.lineWidth = 12
        self.progress_bar.setValue(0)
        self.progress_bar.setChunckColor('#d7d7d7')
        self.main_layout.addWidget(self.progress_bar)

        self.main_layout.addWidget(gui_utils.vertical_separator())

        self.text_widget = QtWidgets.QWidget()
        self.text_widget_layout = QtWidgets.QVBoxLayout()
        self.text_widget_layout.setContentsMargins(0,0,0,0)
        self.text_widget_layout.setSpacing(2)
        self.text_widget.setLayout(self.text_widget_layout)
        self.main_layout.addWidget(self.text_widget)

        self.title_label = QtWidgets.QLabel('Total progress')
        self.title_label.setObjectName('title_label')
        self.text_widget_layout.addWidget(self.title_label)

        self.progress_label = QtWidgets.QLabel()
        self.progress_label.setObjectName('title_label_gray')
        self.text_widget_layout.addWidget(self.progress_label)

        self.text_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def refresh(self):
        stage_rows = project.get_all_stages()
        all_progresses = []
        for stage_row in stage_rows:
            if stage_row['domain_id'] != 2:
                all_progresses.append(stage_row['progress'])
        if all_progresses == []:
            all_progresses == [0]
        mean = statistics.mean(all_progresses)
        self.progress_bar.setValue(mean)
        self.progress_label.setText(f"{round(mean, 1)} %")

class user_progress_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(user_progress_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(12)
        self.main_layout.setContentsMargins(20,20,20,20)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.header_widget_layout = QtWidgets.QHBoxLayout()
        self.header_widget_layout.setContentsMargins(0,0,0,0)
        self.header_widget_layout.setSpacing(12)
        self.header_widget.setLayout(self.header_widget_layout)
        self.main_layout.addWidget(self.header_widget)

        self.user_image_label = QtWidgets.QLabel()
        self.user_image_label.setFixedSize(60,60)
        self.header_widget_layout.addWidget(self.user_image_label)

        self.text_widget = QtWidgets.QWidget()
        self.text_widget_layout = QtWidgets.QVBoxLayout()
        self.text_widget_layout.setContentsMargins(0,0,0,0)
        self.text_widget_layout.setSpacing(2)
        self.text_widget.setLayout(self.text_widget_layout)
        self.header_widget_layout.addWidget(self.text_widget)

        self.title_label = QtWidgets.QLabel('User overview')
        self.title_label.setObjectName('title_label')
        self.text_widget_layout.addWidget(self.title_label)

        self.main_progress_widget = QtWidgets.QWidget()
        self.main_progress_widget_layout = QtWidgets.QHBoxLayout()
        self.main_progress_widget_layout.setContentsMargins(0,0,0,0)
        self.main_progress_widget_layout.setSpacing(6)
        self.main_progress_widget.setLayout(self.main_progress_widget_layout)
        self.text_widget_layout.addWidget(self.main_progress_widget)

        self.main_progress_bar = gui_utils.RoundProgress()
        self.main_progress_bar.setFixedSize(30,30)
        self.main_progress_bar.set_line_width(8)
        self.main_progress_bar.setValue(0)
        self.main_progress_bar.setChunckColor('#d7d7d7')
        self.main_progress_widget_layout.addWidget(self.main_progress_bar)

        self.main_progress_label = QtWidgets.QLabel()
        self.main_progress_label.setObjectName('title_label_gray')
        self.main_progress_widget_layout.addWidget(self.main_progress_label)

        self.text_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.main_layout.addWidget(gui_utils.separator())

        self.quick_stats_label = QtWidgets.QLabel('Quick stats')
        self.quick_stats_label.setObjectName("title_label_2")
        self.main_layout.addWidget(self.quick_stats_label)

        self.quick_stats_widget = QtWidgets.QWidget()
        self.quick_stats_widget_layout = QtWidgets.QHBoxLayout()
        self.quick_stats_widget_layout.setContentsMargins(0,0,0,0)
        self.quick_stats_widget_layout.setSpacing(6)
        self.quick_stats_widget.setLayout(self.quick_stats_widget_layout)
        self.main_layout.addWidget(self.quick_stats_widget)

        self.assignments_widget = quickstats_widget()
        self.assignments_widget.description_label.setText("Tasks")
        self.quick_stats_widget_layout.addWidget(self.assignments_widget)

        self.total_work_time_widget = quickstats_widget()
        self.total_work_time_widget.description_label.setText("Total work time")
        self.quick_stats_widget_layout.addWidget(self.total_work_time_widget)

        self.average_work_time_widget = quickstats_widget()
        self.average_work_time_widget.description_label.setText("Time per asset")
        self.quick_stats_widget_layout.addWidget(self.average_work_time_widget)

        self.all_versions_widget = quickstats_widget()
        self.all_versions_widget.description_label.setText("Work versions")
        self.quick_stats_widget_layout.addWidget(self.all_versions_widget)

        self.all_exports_widget = quickstats_widget()
        self.all_exports_widget.description_label.setText("Exports")
        self.quick_stats_widget_layout.addWidget(self.all_exports_widget)

        self.tasks_done_widget = quickstats_widget()
        self.tasks_done_widget.description_label.setText("Tasks done")
        self.quick_stats_widget_layout.addWidget(self.tasks_done_widget)

        self.main_layout.addWidget(gui_utils.separator())

        self.assets_stats_label = QtWidgets.QLabel('Stages stats')
        self.assets_stats_label.setObjectName("title_label_2")
        self.main_layout.addWidget(self.assets_stats_label)

        self.assets_stats_content_widget = QtWidgets.QWidget()
        self.assets_stats_content_layout = QtWidgets.QHBoxLayout()
        self.assets_stats_content_layout.setAlignment(QtCore.Qt.AlignTop)
        self.assets_stats_content_layout.setSpacing(6)
        self.assets_stats_content_layout.setContentsMargins(0,0,0,0)
        self.assets_stats_content_widget.setLayout(self.assets_stats_content_layout)
        self.main_layout.addWidget(self.assets_stats_content_widget)

        self.stages_piechart_widget_layout = QtWidgets.QVBoxLayout()
        self.stages_piechart_widget_layout.setAlignment(QtCore.Qt.AlignTop)
        self.stages_piechart_widget = stages_piechart()
        self.stages_piechart_widget_layout.addWidget(self.stages_piechart_widget)
        self.assets_stats_content_layout.addLayout(self.stages_piechart_widget_layout)

        self.assets_stats_widget = QtWidgets.QWidget()
        self.assets_stats_widget_layout = gui_utils.QFlowLayout()
        self.assets_stats_widget_layout.setSpacing(6)
        self.assets_stats_widget.setLayout(self.assets_stats_widget_layout)
        self.assets_stats_content_layout.addWidget(self.assets_stats_widget)

        self.stages_widgets_dic = dict()
        for stage in assets_vars._assets_stages_list_ + assets_vars._sequences_stages_list_:
            stage_widget = stage_stats_widget(stage)
            self.stages_widgets_dic[stage] = stage_widget
            stage_widget.setVisible(0)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def refresh(self):
        self.stages_piechart_widget.pie_chart.clear()
        user_row = repository.get_user_row_by_name(environment.get_user())
        user_image =  user_row['profile_picture']
        pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 60)
        self.user_image_label.setPixmap(pixmap)

        stage_rows = project.get_all_stages()
        all_progresses = []
        all_work_times = []
        tasks_done = 0
        total_work_time = 0

        stages_dic = dict()

        for stage_row in stage_rows:
            if stage_row['domain_id'] != 2:
                if stage_row['assignment'] == environment.get_user():
                    all_progresses.append(stage_row['progress'])
                    all_work_times.append(stage_row['work_time'])
                    total_work_time += stage_row['work_time']
                    if stage_row['state'] == 'done':
                        tasks_done+=1

                    if stage_row['name'] not in stages_dic.keys():
                        stages_dic[stage_row['name']] = dict()
                        stages_dic[stage_row['name']]['all_progresses'] = []
                        stages_dic[stage_row['name']]['all_work_times'] = []
                        stages_dic[stage_row['name']]['total_work_time'] = 0

                    stages_dic[stage_row['name']]['all_progresses'].append(stage_row['progress'])
                    stages_dic[stage_row['name']]['all_work_times'].append(stage_row['work_time'])
                    stages_dic[stage_row['name']]['total_work_time'] += stage_row['work_time']

        if all_progresses == []:
            all_progresses = [0]
        if all_work_times == []:
            all_work_times = [0]

        mean = statistics.mean(all_progresses)
        self.main_progress_bar.setValue(mean)
        self.main_progress_label.setText(f"{round(mean, 1)} %")

        work_time_mean = statistics.mean(all_work_times)
        self.assignments_widget.stat_label.setText(f"{len(all_progresses)}")
        self.total_work_time_widget.stat_label.setText(f"{tools.convert_seconds_to_string_time(total_work_time)}")
        self.average_work_time_widget.stat_label.setText(f"{tools.convert_seconds_to_string_time(work_time_mean)}")

        all_work_versions = project.get_work_versions_by_user(environment.get_user(), 'id')
        self.all_versions_widget.stat_label.setText(f"{len(all_work_versions)}")

        all_exports = project.get_export_versions_by_user_name(environment.get_user(), 'id')
        self.all_exports_widget.stat_label.setText(f"{len(all_exports)}")

        self.tasks_done_widget.stat_label.setText(f"{tasks_done}/{len(all_progresses)}")

        for stage in stages_dic.keys():
            mean = statistics.mean(stages_dic[stage]['all_progresses'])
            work_time_mean = statistics.mean(stages_dic[stage]['all_work_times'])
            total_work_time = stages_dic[stage]['total_work_time']
            self.stages_widgets_dic[stage].progress_bar.setValue(mean)
            self.stages_widgets_dic[stage].progress_label.setText(f"{int(mean)}%")
            self.stages_widgets_dic[stage].total_work_time.setText(f"{tools.convert_seconds_to_string_time(total_work_time)}")
            self.stages_widgets_dic[stage].tasks_count.setText(f"{len(stages_dic[stage]['all_progresses'])}")
            self.stages_widgets_dic[stage].average_work_time.setText(f"{tools.convert_seconds_to_string_time(work_time_mean)}")
            self.assets_stats_widget_layout.addWidget(self.stages_widgets_dic[stage])
            self.stages_widgets_dic[stage].setVisible(1)

            stage_repartition_percent = (len(stages_dic[stage]['all_progresses'])/len(all_progresses))*100
            self.stages_piechart_widget.pie_chart.add_pie(stage_repartition_percent, ressources._stages_colors_[stage])
        stages_list = list(self.stages_widgets_dic.keys())
        for stage in stages_list:
            if stage not in stages_dic.keys():
                self.remove_stage(stage)

    def remove_stage(self, stage):
        self.stages_widgets_dic[stage].setVisible(0)
        self.stages_widgets_dic[stage].setParent(self)

class quickstats_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(quickstats_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setObjectName("quickstats_widget")
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.stat_label = QtWidgets.QLabel()
        self.stat_label.setAlignment(QtCore.Qt.AlignCenter)
        self.stat_label.setObjectName("title_label")
        self.main_layout.addWidget(self.stat_label)

        self.description_label = QtWidgets.QLabel()
        self.description_label.setAlignment(QtCore.Qt.AlignCenter)
        self.description_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.description_label)

class stages_piechart(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(stages_piechart, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setFixedSize(140,140)
        self.setObjectName("quickstats_widget")
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(20,20,20,20)
        self.setLayout(self.main_layout)

        self.pie_chart = chart_utils.pie_chart()

        self.main_layout.addWidget(self.pie_chart)

class progress_curves_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(progress_curves_widget, self).__init__(parent)
        self.data_dic = dict()
        self.contexts = []
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.setMinimumHeight(400)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(20,20,20,20)
        self.main_layout.setSpacing(12)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget_layout = QtWidgets.QHBoxLayout()
        self.header_widget_layout.setContentsMargins(0,0,0,0)
        self.header_widget.setLayout(self.header_widget_layout)
        self.main_layout.addWidget(self.header_widget)

        self.title_label = QtWidgets.QLabel("Progress chart")
        self.title_label.setObjectName("title_label")
        self.header_widget_layout.addWidget(self.title_label)

        self.header_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(30,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        self.context_comboBox = gui_utils.QComboBox()
        self.context_comboBox.setFixedWidth(140)
        self.header_widget_layout.addWidget(self.context_comboBox)

        self.header_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.chart_layout = QtWidgets.QHBoxLayout()
        self.chart_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.chart_layout)

        self.chart = chart_utils.curves_chart()
        self.chart.setObjectName('quickstats_widget')
        self.chart.set_ordonea_headers(["0%", "25%", "50%", "75%", "100%"])
        self.chart.set_margin(40)
        self.chart.set_points_thickness(4)
        self.chart.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.chart_layout.addWidget(self.chart)

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.setContentsMargins(0,0,0,0)
        self.chart_layout.addLayout(self.settings_layout)

        self.settings_content_layout = QtWidgets.QVBoxLayout()
        self.settings_content_layout.setContentsMargins(0,0,0,0)
        self.settings_content_layout.setSpacing(2)
        self.settings_layout.addLayout(self.settings_content_layout)

        self.prevision_check_box = QtWidgets.QCheckBox("Show projection")
        self.prevision_check_box.setChecked(True)
        self.settings_content_layout.addWidget(self.prevision_check_box)

        self.settings_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def connect_functions(self):
        self.prevision_check_box.stateChanged.connect(self.chart.set_prevision_visibility)
        self.context_comboBox.currentTextChanged.connect(lambda:self.context_changed(None))

    def refresh(self):
        all_progress_events_rows = project.get_all_progress_events()
        self.refresh_contexts(all_progress_events_rows)

    def refresh_contexts(self, all_progress_events_rows):
        self.apply_context_changed = False
        contexts = []
        for progress_event_row in all_progress_events_rows:
            contexts.append(progress_event_row['name'])
            self.add_context(progress_event_row['name'])
        contexts_list = copy.deepcopy(self.contexts)
        for context in contexts_list:
            if context not in contexts:
                self.remove_context(context)
        self.apply_context_changed = True
        self.context_changed(all_progress_events_rows)

    def context_changed(self, all_progress_events_rows=None):
        if self.apply_context_changed:
            self.context = self.context_comboBox.currentText()
            if all_progress_events_rows is None:
                all_progress_events_rows = project.get_all_progress_events()
            self.refresh_datas(all_progress_events_rows)

    def refresh_datas(self, all_progress_events_rows):
        self.chart.clear()
        datas_dic = dict()
        total_progress = []

        start_time = all_progress_events_rows[0]['creation_time']
        end_time = all_progress_events_rows[-1]['creation_time']
        #end_time = time.time()+3600*12
        time_range = end_time - start_time

        if time_range > 0:
            for progress_event_row in all_progress_events_rows:
                if progress_event_row['name'] == self.context:
                    time_percent = (progress_event_row['creation_time'] - start_time)/time_range*100
                    project_datas_dic = json.loads(progress_event_row['datas_dic'])
                    for data_name in project_datas_dic.keys():
                        if data_name not in datas_dic.keys():
                            datas_dic[data_name] = []
                        datas_dic[data_name].append((time_percent, project_datas_dic[data_name]))

        for data_name in datas_dic.keys():
            if data_name == 'total':
                color = 'gray'
                width = 2
            else:
                color = ressources._stages_colors_[data_name]
                width = 1
            self.chart.add_line(datas_dic[data_name], color, width, data_name)
            self.add_data(data_name, color)
        
        data_list = list(self.data_dic.keys())
        for data in data_list:
            if data not in datas_dic.keys():
                self.remove_data(data)

        month = tools.get_month(start_time)
        day = tools.get_day(start_time)
        abscissa_headers = [f"{month} {day}"]
        time_step = time_range/8
        for t in range(1, 7):
            time_header = start_time + time_step*t
            month = tools.get_month(time_header)
            day = tools.get_day(time_header)
            abscissa_headers.append(f"{month} {day}")
        month = tools.get_month(end_time)
        day = tools.get_day(end_time)
        abscissa_headers.append(f"{month} {day}")
        self.chart.set_abscissa_headers(abscissa_headers)
        self.update_data_visibility()

    def add_context(self, context_name):
        if context_name not in self.contexts:
            self.context_comboBox.addItem(context_name)
            self.contexts.append(context_name)

    def remove_context(self, context_name):
        if context_name in self.contexts:
            self.contexts.remove(context_name)
            item_index = self.context_comboBox.findText(context_name)
            if item_index != -1:
                self.context_comboBox.removeItem(item_index)

    def add_data(self, data, color):
        if data not in self.data_dic.keys():
            item = data_item(data, color)
            item.stateChanged.connect(self.update_data_visibility)
            item.setChecked(True)
            self.settings_content_layout.addWidget(item)
            self.data_dic[data] = item

    def clear_data(self):
        data_list = list(self.data_dic.keys())
        for data in data_list:
            self.remove_data(data)

    def remove_data(self, data):
        if data in self.data_dic.keys():
            self.data_dic[data].setVisible(False)
            self.data_dic[data].setParent(None)
            self.data_dic[data].deleteLater()
            del self.data_dic[data]

    def update_data_visibility(self):
        pass
        for data in self.data_dic.keys():
            self.chart.set_data_visible(data, self.data_dic[data].isChecked())

class data_item(QtWidgets.QFrame):

    stateChanged = pyqtSignal(bool)

    def __init__(self, data_name, data_color, parent=None):
        super(data_item, self).__init__(parent)
        self.data_name = data_name
        self.data_color = data_color
        self.checked = False
        self.setObjectName('quickstats_widget')
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(4,4,4,4)
        self.setLayout(self.main_layout)
        self.color_frame = QtWidgets.QFrame()
        self.color_frame.setFixedSize(8,8)
        self.main_layout.addWidget(self.color_frame)
        self.data_name_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.data_name_label)

    def mouseReleaseEvent(self, event):
        self.checked = 1-self.checked
        self.stateChanged.emit(self.checked)
        self.update_state()

    def fill_ui(self):
        self.color_frame.setStyleSheet(f"background-color:{self.data_color};border-radius:4px;")
        self.data_name_label.setText(self.data_name)

    def update_state(self):
        if self.checked:
            self.setStyleSheet("#quickstats_widget{background-color:rgba(255,255,255,20);}")
        else:
            self.setStyleSheet("")

    def setChecked(self, state):
        self.checked = state
        self.update_state()

    def isChecked(self):
        return self.checked

class stage_stats_widget(QtWidgets.QWidget):
    def __init__(self, stage, parent=None):
        super(stage_stats_widget, self).__init__(parent)
        self.stage = stage
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setFixedWidth(250)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.content_widget = QtWidgets.QFrame()
        self.content_widget.setObjectName("quickstats_widget")
        self.content_widget_widget_layout = QtWidgets.QHBoxLayout()
        self.content_widget_widget_layout.setContentsMargins(0,0,0,0)
        self.content_widget_widget_layout.setSpacing(4)
        self.content_widget.setLayout(self.content_widget_widget_layout)
        self.main_layout.addWidget(self.content_widget)

        self.color_frame = QtWidgets.QFrame()
        self.color_frame.setFixedWidth(4)
        self.content_widget_widget_layout.addWidget(self.color_frame)

        self.content_1_widget = QtWidgets.QWidget()
        self.content_1_widget.setObjectName("transparent_widget")
        self.content_1_widget_layout = QtWidgets.QVBoxLayout()
        self.content_1_widget.setLayout(self.content_1_widget_layout)
        self.content_widget_widget_layout.addWidget(self.content_1_widget)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName("transparent_widget")
        self.header_widget_layout = QtWidgets.QHBoxLayout()
        self.header_widget_layout.setContentsMargins(0,0,0,0)
        self.header_widget_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_widget_layout)
        self.content_1_widget_layout.addWidget(self.header_widget)

        self.stage_icon_label = QtWidgets.QLabel()
        self.stage_icon_label.setFixedSize(18,18)
        self.header_widget_layout.addWidget(self.stage_icon_label)

        self.stage_name_label = QtWidgets.QLabel()
        self.stage_name_label.setObjectName('title_label_2')
        self.header_widget_layout.addWidget(self.stage_name_label)

        self.header_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.progress_label = QtWidgets.QLabel()
        #self.progress_label.setObjectName('title_label_gray')
        self.header_widget_layout.addWidget(self.progress_label)

        self.progress_bar = gui_utils.QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar::chunk{background-color:#d7d7d7;}")
        self.progress_bar.setFixedHeight(6)
        self.content_1_widget_layout.addWidget(self.progress_bar)

        self.additionnal_infos_widget = QtWidgets.QWidget()
        self.additionnal_infos_widget.setObjectName("transparent_widget")
        self.additionnal_infos_widget_layout = QtWidgets.QHBoxLayout()
        self.additionnal_infos_widget_layout.setContentsMargins(0,0,0,0)
        self.additionnal_infos_widget_layout.setSpacing(2)
        self.additionnal_infos_widget.setLayout(self.additionnal_infos_widget_layout)
        self.content_1_widget_layout.addWidget(self.additionnal_infos_widget)

        self.total_work_time = QtWidgets.QLabel()
        self.additionnal_infos_widget_layout.addWidget(self.total_work_time)

        self.total_work_time_label = QtWidgets.QLabel("-")
        self.total_work_time_label.setObjectName('gray_label')
        self.additionnal_infos_widget_layout.addWidget(self.total_work_time_label)

        self.additionnal_infos_widget_layout.addWidget(gui_utils.vertical_separator())

        self.average_work_time = QtWidgets.QLabel()
        self.additionnal_infos_widget_layout.addWidget(self.average_work_time)

        self.average_work_time_label = QtWidgets.QLabel("/ asset")
        self.average_work_time_label.setObjectName('gray_label')
        self.additionnal_infos_widget_layout.addWidget(self.average_work_time_label)

        self.additionnal_infos_widget_layout.addWidget(gui_utils.vertical_separator())

        self.tasks_count = QtWidgets.QLabel()
        self.additionnal_infos_widget_layout.addWidget(self.tasks_count)

        self.tasks_count_label = QtWidgets.QLabel("Tasks")
        self.tasks_count_label.setObjectName('gray_label')
        self.additionnal_infos_widget_layout.addWidget(self.tasks_count_label)

        self.additionnal_infos_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def fill_ui(self):
        self.stage_icon_label.setPixmap(QtGui.QIcon(ressources._stage_icons_dic_[self.stage]).pixmap(18))
        self.stage_name_label.setText(self.stage.capitalize())
        self.color_frame.setStyleSheet(f"border-top-left-radius:4px;border-bottom-left-radius:4px;background-color:{ressources._stages_colors_[self.stage]}")

class progress_overview_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(progress_overview_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(30,30,30,30)
        self.main_layout.setSpacing(18)
        self.setLayout(self.main_layout)

        self.domains_dic = dict()
        self.stages_dic = dict()

        for domain in assets_vars._domains_list_no_lib_:
            domain_header = QtWidgets.QWidget()
            domain_header.setObjectName('transparent_widget')
            domain_header_layout = QtWidgets.QHBoxLayout()
            domain_header_layout.setContentsMargins(0,0,0,0)
            domain_header_layout.setSpacing(10)
            domain_header.setLayout(domain_header_layout)
            self.main_layout.addWidget(domain_header)

            domain_icon_label = QtWidgets.QLabel()
            domain_icon_label.setPixmap(QtGui.QIcon(ressources._domains_icons_dic_[domain]).pixmap(24))
            domain_header_layout.addWidget(domain_icon_label)

            domain_title_label = QtWidgets.QLabel(domain.capitalize())
            domain_title_label.setObjectName('title_label_2')
            domain_title_label.setFixedWidth(80)
            domain_header_layout.addWidget(domain_title_label)

            domain_header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

            domain_progress_label = QtWidgets.QLabel()
            domain_header_layout.addWidget(domain_progress_label)
            self.domains_dic[domain] = dict()
            self.domains_dic[domain]['progress_label'] = domain_progress_label

            progress_bar = gui_utils.RoundProgress()
            progress_bar.setChunckColor("#d7d7d7")
            progress_bar.setFixedSize(22,22)
            progress_bar.set_line_width(6)
            progress_bar.setValue(0)
            domain_header_layout.addWidget(progress_bar)
            self.domains_dic[domain]['progress_bar'] = progress_bar

            self.main_layout.addWidget(gui_utils.separator())

            domain_stages_widget = QtWidgets.QWidget()
            domain_stages_widget_layout = QtWidgets.QVBoxLayout()
            domain_stages_widget_layout.setContentsMargins(0,0,0,0)
            domain_stages_widget.setLayout(domain_stages_widget_layout)
            self.main_layout.addWidget(domain_stages_widget)

            for stage in assets_vars._stages_list_[domain]:
                main_widget = QtWidgets.QWidget()
                main_widget_layout = QtWidgets.QHBoxLayout()
                main_widget_layout.setContentsMargins(0,0,0,0)
                main_widget.setLayout(main_widget_layout)
                main_widget.setVisible(0)
                domain_stages_widget_layout.addWidget(main_widget)
                self.stages_dic[stage] = dict()
                self.stages_dic[stage]['widget'] = main_widget

                icon_label = QtWidgets.QLabel()
                icon_label.setPixmap(QtGui.QIcon(ressources._stage_icons_dic_[stage]).pixmap(20))
                main_widget_layout.addWidget(icon_label)

                title_label = QtWidgets.QLabel(stage.capitalize())
                title_label.setFixedWidth(80)
                main_widget_layout.addWidget(title_label)

                main_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

                progress_label = QtWidgets.QLabel()
                main_widget_layout.addWidget(progress_label)
                self.stages_dic[stage]['progress_label'] = progress_label

                progress_bar = gui_utils.QProgressBar()
                progress_bar.setStyleSheet("QProgressBar::chunk{background-color:#d7d7d7;}")
                progress_bar.setFixedHeight(6)
                main_widget_layout.addWidget(progress_bar)
                self.stages_dic[stage]['progress_bar'] = progress_bar

                color_frame = QtWidgets.QFrame()
                color_frame.setFixedSize(8,8)
                color_frame.setStyleSheet(f"background-color:{ressources._stages_colors_[stage]};border-radius:4px;")
                main_widget_layout.addWidget(color_frame)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def refresh(self):
        stages_rows = project.get_all_stages()
        stages_progresses_dic = dict()
        domains_progresses_dic = dict()

        for stage_row in stages_rows:
            if stage_row['name'] not in stages_progresses_dic.keys():
                stages_progresses_dic[stage_row['name']] = []
            stages_progresses_dic[stage_row['name']].append(stage_row['progress'])
            if stage_row['name'] in assets_vars._assets_stages_list_:
                if 'assets' not in domains_progresses_dic.keys():
                    domains_progresses_dic['assets'] = []
                domains_progresses_dic['assets'].append(stage_row['progress'])
            elif stage_row['name'] in assets_vars._sequences_stages_list_:
                if 'sequences' not in domains_progresses_dic.keys():
                    domains_progresses_dic['sequences'] = []
                domains_progresses_dic['sequences'].append(stage_row['progress'])

        for stage in stages_progresses_dic.keys():
            mean = statistics.mean(stages_progresses_dic[stage])
            self.stages_dic[stage]['progress_bar'].setValue(mean)
            self.stages_dic[stage]['progress_label'].setText(f"{round(mean, 1)} %")
            self.stages_dic[stage]['widget'].setVisible(True)

        for domain in domains_progresses_dic.keys():
            mean = statistics.mean(domains_progresses_dic[domain])
            self.domains_dic[domain]['progress_bar'].setValue(mean)
            self.domains_dic[domain]['progress_label'].setText(f"{round(mean, 1)} %")
