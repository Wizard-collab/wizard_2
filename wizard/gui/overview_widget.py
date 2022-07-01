# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtChart import QChart, QChartView, QPieSeries
import statistics
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
        self.resize(1400,800)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.vertical_widget_1 = QtWidgets.QWidget()
        self.vertical_widget_1.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.vertical_widget_1.setObjectName('transparent_widget')
        self.vertical_layout_1 = QtWidgets.QVBoxLayout()
        self.vertical_layout_1.setContentsMargins(0,0,0,0)
        self.vertical_widget_1.setLayout(self.vertical_layout_1)
        self.main_layout.addWidget(self.vertical_widget_1)

        self.vertical_layout_1.addWidget(self.main_progress_widget)
        self.vertical_layout_1.addWidget(self.progress_overview_widget)

        self.vertical_layout_1.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.vertical_layout_2 = QtWidgets.QVBoxLayout()
        self.vertical_layout_2.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.vertical_layout_2)

        self.vertical_layout_2.addWidget(self.user_progress_widget)
        self.vertical_layout_2.addWidget(self.progress_curves_widget)

    def refresh(self):
        self.progress_overview_widget.refresh()
        self.main_progress_widget.refresh()
        self.user_progress_widget.refresh()
        self.progress_curves_widget.refresh()

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
        self.main_progress_bar.lineWidth = 8
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
        self.build_ui()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.setMinimumHeight(400)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(20,20,20,20)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget_layout = QtWidgets.QHBoxLayout()
        self.header_widget_layout.setContentsMargins(0,0,0,0)
        self.header_widget.setLayout(self.header_widget_layout)
        self.main_layout.addWidget(self.header_widget)

        self.title_label = QtWidgets.QLabel("Progress chart")
        self.title_label.setObjectName("title_label")
        self.header_widget_layout.addWidget(self.title_label)

        self.chart = chart_utils.curves_chart()
        self.chart.set_ordonea_headers(["0%", "25%", "50%", "75%", "100%"])
        self.chart.setObjectName('quickstats_widget')
        self.chart.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addWidget(self.chart)

    def refresh(self):
        all_progress_events_rows = project.get_all_progress_events()
        stages_dic = dict()
        total_progress = []

        start_time = all_progress_events_rows[0]['creation_time']
        end_time = all_progress_events_rows[-1]['creation_time']
        time_range = end_time - start_time

        for progress_event_row in all_progress_events_rows:
            time_percent = (progress_event_row['creation_time'] - start_time)/time_range*100
            if progress_event_row['type'] == 'stage':
                if progress_event_row['name'] not in stages_dic.keys():
                    stages_dic[progress_event_row['name']] = []
                stages_dic[progress_event_row['name']].append((time_percent, progress_event_row['progress']))
            if progress_event_row['type'] == 'total':
                total_progress.append((time_percent, progress_event_row['progress']))

        self.chart.add_line(total_progress, '#d7d7d7', 3, 'total', QtCore.Qt.DashLine)

        for stage in stages_dic.keys():
            self.chart.add_line(stages_dic[stage], ressources._stages_colors_[stage], 1, stage)

class stage_stats_widget(QtWidgets.QWidget):
    def __init__(self, stage, parent=None):
        super(stage_stats_widget, self).__init__(parent)
        self.stage = stage
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setFixedWidth(350)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.content_widget = QtWidgets.QFrame()
        self.content_widget.setObjectName("quickstats_widget")
        self.content_widget_widget_layout = QtWidgets.QHBoxLayout()
        self.content_widget_widget_layout.setContentsMargins(0,0,0,0)
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
        self.stage_icon_label.setFixedSize(24,24)
        self.header_widget_layout.addWidget(self.stage_icon_label)

        self.stage_name_label = QtWidgets.QLabel()
        self.stage_name_label.setObjectName('title_label')
        self.header_widget_layout.addWidget(self.stage_name_label)

        self.header_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.progress_label = QtWidgets.QLabel()
        self.progress_label.setObjectName('title_label_gray')
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

        self.total_work_time_label = QtWidgets.QLabel("Total work time")
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
        self.stage_icon_label.setPixmap(QtGui.QIcon(ressources._stage_icons_dic_[self.stage]).pixmap(24))
        self.stage_name_label.setText(self.stage.capitalize())
        self.color_frame.setStyleSheet(f"border-top-left-radius:4px;border-bottom-left-radius:4px;background-color:{ressources._stages_colors_[self.stage]}")

class progress_overview_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(progress_overview_widget, self).__init__(parent)
        self.build_ui()
        self.refresh()

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
            progress_bar.lineWidth = 14
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
                domain_stages_widget_layout.addWidget(main_widget)

                icon_label = QtWidgets.QLabel()
                icon_label.setPixmap(QtGui.QIcon(ressources._stage_icons_dic_[stage]).pixmap(20))
                main_widget_layout.addWidget(icon_label)

                title_label = QtWidgets.QLabel(stage.capitalize())
                title_label.setFixedWidth(80)
                main_widget_layout.addWidget(title_label)

                main_widget_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

                progress_label = QtWidgets.QLabel()
                main_widget_layout.addWidget(progress_label)
                self.stages_dic[stage] = dict()
                self.stages_dic[stage]['progress_label'] = progress_label

                progress_bar = gui_utils.QProgressBar()
                progress_bar.setStyleSheet("QProgressBar::chunk{background-color:#d7d7d7;}")
                progress_bar.setFixedHeight(6)
                main_widget_layout.addWidget(progress_bar)
                self.stages_dic[stage]['progress_bar'] = progress_bar

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

        for domain in domains_progresses_dic.keys():
            mean = statistics.mean(domains_progresses_dic[domain])
            self.domains_dic[domain]['progress_bar'].setValue(mean)
            self.domains_dic[domain]['progress_label'].setText(f"{round(mean, 1)} %")

w=overview_widget()
w.show()