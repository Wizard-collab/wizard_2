# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import sys
import datetime
import time
import random
import logging

logger = logging.getLogger(__name__)

# Wizard modules
from wizard.vars import ressources

class signal_manager(QtCore.QObject):

    movement = pyqtSignal(int)
    stop_movement = pyqtSignal(int)
    start_move = pyqtSignal(int)
    start_scale = pyqtSignal(int)
    select = pyqtSignal(object)
    duration_modified = pyqtSignal(int)
    start_date_modified = pyqtSignal(int)

    def __init__(self, parent=None):
        super(signal_manager, self).__init__(parent)

class custom_graphic_item(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(custom_graphic_item, self).__init__()

        self.selected = False
        self.x = 0
        self.y = 0
        self.width = 1
        self.height = 1

    def set_selected(self, selection):
        self.selected = selection

    def toggle_selection(self):
        self.selected = 1-self.selected

    def setRect(self, x, y , width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def set_size(self, width, height):
        self.prepareGeometryChange()
        self.width = width
        self.height = height
        self.update()

    def setVisible(self, visible):
        if not visible:
            self.selected = False
        super().setVisible(visible)

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        color = QtGui.QColor('transparent')
        pen = QtGui.QPen(QtGui.QColor('transparent'), 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.x, self.y, self.width, self.height)

class calendar_header(QtWidgets.QGraphicsView):
    def __init__(self):
        super(calendar_header, self).__init__()
        self.setObjectName('dark_widget')
        self.setFixedHeight(120)
        self.scene = header_scene()
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing, False)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.pan = False
        self.column_width = 100
        self.last_mouse_pos = None
        self.zoom_factor = 1.0
        self.today_item = today_item()
        self.today_item.setZValue(1.0)
        self.scene.addItem(self.today_item)

        self.day_items = []
        self.week_items = []
        self.month_items = []
        self.year_items = []
        self.update_header()

    def set_column_width(self, column_width):
        self.column_width = column_width
        self.scene.set_column_width(column_width)
        self.update_header()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_header()

    def update_header(self):
        leftmost_column, visible_columns = self.get_visible_columns()
        self.today = datetime.date.today()
        self.days_range = range(leftmost_column, leftmost_column + visible_columns)
        self.pos_y = 0
        self.create_dics()
        self.update_years()
        self.update_months()
        self.update_days()
        self.update_weeks()
        self.update_today_item()
        self.resize_header()

    def update_today_item(self):
        self.today_item.setRect(0,0,int(self.column_width*self.zoom_factor),self.height())

    def resize_header(self):
        self.setFixedHeight(self.pos_y)
        scene_rect = self.sceneRect()
        scene_rect.setHeight(self.viewport().height())
        self.setSceneRect(scene_rect)

    def create_dics(self):
        self.months_dic = dict()
        self.years_dic = dict()
        self.weeks_dic = dict()

        for day_offset in self.days_range:
            day = self.today + datetime.timedelta(days=day_offset)
            year = day.strftime("%Y")
            month = day.strftime("%Y%B")
            week = day.strftime("%Y%W")
            if month not in self.months_dic.keys():
                self.months_dic[month] = []
            self.months_dic[month].append(day)
            if year not in self.years_dic.keys():
                self.years_dic[year] = []
            self.years_dic[year].append(day)
            if week not in self.weeks_dic.keys():
                self.weeks_dic[week] = []
            self.weeks_dic[week].append(day)

    def update_days(self):
        if self.column_width * self.zoom_factor <= 20:
            for item in self.day_items:
                self.scene.removeItem(item)
            self.day_items = []
            return
        
        while len(self.day_items) < len(self.days_range):
            text_item = day_item()
            self.day_items.append(text_item)
            self.scene.addItem(text_item)

        for i, day_column_pos in enumerate(self.days_range):
            day_text = (self.today - datetime.timedelta(days=day_column_pos)).strftime("%d")
            x_pos = (day_column_pos * self.column_width)
            height = 30
            if self.column_width*self.zoom_factor <= 100:
                height = 15
            self.day_items[i].setRect(x_pos*self.zoom_factor,
                                                self.pos_y,
                                                self.column_width*self.zoom_factor,
                                                height)
            self.day_items[i].setDate((self.today + datetime.timedelta(days=day_column_pos)))

        while len(self.day_items) > len(self.days_range):
            item = self.day_items.pop()
            self.scene.removeItem(item)

        self.pos_y += height

    def get_day_position(self, day):
        pos = (day - self.today).days * self.column_width
        return pos

    def update_weeks(self):
        if self.column_width * self.zoom_factor <= 5:
            for item in self.week_items:
                self.scene.removeItem(item)
            self.week_items = []
            return

        while len(self.week_items) < len(self.weeks_dic.keys()):
            item = week_item()
            self.week_items.append(item)
            self.scene.addItem(item)

        for week in self.weeks_dic.keys():
            index = list(self.weeks_dic.keys()).index(week)
            x_pos = self.get_day_position(self.weeks_dic[week][0])
            left = self.mapToScene(self.viewport().rect()).boundingRect().left()
            right = self.mapToScene(self.viewport().rect()).boundingRect().right()
            if x_pos < left:
                x_pos = left
            x_2_pos = self.get_day_position(self.weeks_dic[week][-1]+datetime.timedelta(days=1))
            if x_2_pos > right:
                x_2_pos = right
            width = x_2_pos-x_pos
            self.week_items[index].setRect(x_pos*self.zoom_factor,
                                            self.pos_y,
                                            width*self.zoom_factor,
                                            20)
            self.week_items[index].setText(week)

        while len(self.week_items) > len(self.weeks_dic.keys()):
            item = self.week_items.pop()
            self.scene.removeItem(item)

        self.pos_y += 20

    def update_months(self):
        if self.column_width * self.zoom_factor <= 1:
            for item in self.month_items:
                self.scene.removeItem(item)
            self.month_items = []
            return

        while len(self.month_items) < len(self.months_dic.keys()):
            item = month_item()
            self.month_items.append(item)
            self.scene.addItem(item)

        for month in self.months_dic.keys():
            index = list(self.months_dic.keys()).index(month)
            x_pos = self.get_day_position(self.months_dic[month][0])
            left = self.mapToScene(self.viewport().rect()).boundingRect().left()
            right = self.mapToScene(self.viewport().rect()).boundingRect().right()
            if x_pos < left:
                x_pos = left
            x_2_pos = self.get_day_position(self.months_dic[month][-1]+datetime.timedelta(days=1))
            if x_2_pos > right:
                x_2_pos = right
            width = x_2_pos-x_pos
            self.month_items[index].setRect(x_pos*self.zoom_factor,
                                            self.pos_y,
                                            width*self.zoom_factor,
                                            20)
            self.month_items[index].setText(month)

        while len(self.month_items) > len(self.months_dic.keys()):
            item = self.month_items.pop()
            self.scene.removeItem(item)

        self.pos_y += 20

    def update_years(self):
        while len(self.year_items) < len(self.years_dic.keys()):
            item = year_item()
            self.year_items.append(item)
            self.scene.addItem(item)

        for year in self.years_dic.keys():
            index = list(self.years_dic.keys()).index(year)
            x_pos = self.get_day_position(self.years_dic[year][0])
            left = self.mapToScene(self.viewport().rect()).boundingRect().left()
            right = self.mapToScene(self.viewport().rect()).boundingRect().right()
            if x_pos < left:
                x_pos = left
            x_2_pos = self.get_day_position(self.years_dic[year][-1]+datetime.timedelta(days=1))
            if x_2_pos > right:
                x_2_pos = right
            width = x_2_pos-x_pos
            self.year_items[index].setRect(x_pos*self.zoom_factor,
                                                self.pos_y,
                                                width*self.zoom_factor,
                                                30)
            self.year_items[index].setText(year)

        while len(self.year_items) > len(self.years_dic.keys()):
            item = self.year_items.pop()
            self.scene.removeItem(item)
        self.pos_y += 30

    def get_visible_columns(self):
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        leftmost_column = int(visible_rect.left() // self.column_width)
        rightmost_column = int(visible_rect.right() // self.column_width)
        visible_columns = rightmost_column - leftmost_column + 1
        return leftmost_column, visible_columns

    def update_rect(self, rect):
        self.setSceneRect(rect.x(),
                        self.sceneRect().y(),
                        rect.width(),
                        self.sceneRect().height())
        self.update_header()

    def update_scale(self, scale_factor):
        self.scale(scale_factor, 1)

    def update_zoom_factor(self, zoom_factor):
        self.zoom_factor = zoom_factor

class day_item(custom_graphic_item):
    def __init__(self):
        super(day_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.date = datetime.date.today()

    def setDate(self, date):
        self.date = date

    def paint(self, painter, option, widget):
        number_height = self.height/2
        if self.width <= 100:
            number_height = self.height
        rect = QtCore.QRectF(self.x, self.y, self.width, number_height)
        color = QtGui.QColor(255,255,255, int(255*0.85))
        if self.date.strftime("%A") in ['Saturday', 'Sunday']:
            color = QtGui.QColor(255,255,255,50)
        draw_text(painter, rect, self.date.strftime("%d"), color=color, bold=True)
        if self.width > 100:
            rect = QtCore.QRectF(self.x, self.y+self.height/2, self.width, self.height/2)
            draw_text(painter,
                        rect,
                        self.date.strftime("%A")[:3],
                        color=QtGui.QColor(255,255,255,50),
                        bold=False)

class week_item(custom_graphic_item):
    def __init__(self):
        super(week_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.margin = 1
        self.text = ''

    def setText(self, text):
        self.text = text

    def paint(self, painter, option, widget):
        text = f"Week {self.text[4:]}"
        if self.width < 100:
            text = self.text[4:]

        rect = QtCore.QRectF(self.x + self.margin,
                                self.y + self.margin,
                                self.width - self.margin*2,
                                self.height - self.margin*2)
        draw_rect(painter, rect, bg_color=QtGui.QColor(0,0,5,20), radius=2)
        draw_text(painter, rect, text, bold=False)

class month_item(custom_graphic_item):
    def __init__(self):
        super(month_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.margin = 2
        self.text = ''

    def setText(self, text):
        self.text = text

    def paint(self, painter, option, widget):
        text = self.text[4:]
        if self.width < 50:
            text = text[:3]

        rect = QtCore.QRectF(self.x + self.margin,
                                self.y + self.margin,
                                self.width - self.margin*2,
                                self.height - self.margin*2)
        draw_rect(painter, rect, bg_color=QtGui.QColor(61,61,67,60), radius=4)
        draw_text(painter, rect, text, bold=False)

class year_item(custom_graphic_item):
    def __init__(self):
        super(year_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.margin = 4
        self.text = ''

    def setText(self, text):
        self.text = text

    def paint(self, painter, option, widget):
        rect = QtCore.QRectF(self.x + self.margin,
                                self.y + self.margin,
                                self.width - self.margin*2,
                                self.height - self.margin*2)
        draw_text(painter, rect, self.text, size=20, bold=True, align=QtCore.Qt.AlignLeft)

class viewport_helper(QtWidgets.QWidget):

    reset_view = pyqtSignal(int)
    goto_today = pyqtSignal(int)

    def __init__(self, parent=None):
        super(viewport_helper, self).__init__(parent)
        self.setObjectName('transparent_widget')
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.reset_button.clicked.connect(self.reset_view.emit)
        self.today_button.clicked.connect(self.goto_today.emit)

    def build_ui(self):
        self.all_layout = QtWidgets.QHBoxLayout()
        self.all_layout.setContentsMargins(4,4,4,4)
        self.setLayout(self.all_layout)
        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setObjectName('light_round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.all_layout.setContentsMargins(6,6,6,6)
        self.main_widget.setLayout(self.main_layout)
        self.all_layout.addWidget(self.main_widget)

        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.infos_layout)

        self.selected_label = QtWidgets.QLabel()
        self.items_number_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.selected_label)
        self.infos_layout.addWidget(self.items_number_label)
        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.helper_layout = QtWidgets.QHBoxLayout()
        self.helper_layout.setContentsMargins(0,0,0,0)
        self.helper_layout.setSpacing(5)
        self.main_layout.addLayout(self.helper_layout)

        self.pan_image = QtWidgets.QLabel()
        self.pan_image.setPixmap(QtGui.QIcon(ressources._pan_icon_).pixmap(20))
        self.pan_label = QtWidgets.QLabel('Wheel button')
        self.pan_label.setObjectName('gray_label')

        self.zoom_image = QtWidgets.QLabel()
        self.zoom_image.setPixmap(QtGui.QIcon(ressources._zoom_icon_).pixmap(20))
        self.zoom_label = QtWidgets.QLabel('Wheel')
        self.zoom_label.setObjectName('gray_label')

        self.horizontal_zoom_image = QtWidgets.QLabel()
        self.horizontal_zoom_image.setPixmap(QtGui.QIcon(ressources._zoom_horizontal_icon_).pixmap(20))
        self.horizontal_zoom_label = QtWidgets.QLabel('Shift + Wheel')
        self.horizontal_zoom_label.setObjectName('gray_label')

        self.vertical_zoom_image = QtWidgets.QLabel()
        self.vertical_zoom_image.setPixmap(QtGui.QIcon(ressources._zoom_vertical_icon_).pixmap(20))
        self.vertical_zoom_label = QtWidgets.QLabel('Ctrl + Wheel')
        self.vertical_zoom_label.setObjectName('gray_label')

        self.focus_image = QtWidgets.QLabel()
        self.focus_image.setPixmap(QtGui.QIcon(ressources._focus_icon_).pixmap(20))
        self.focus_label = QtWidgets.QLabel('F')
        self.focus_label.setObjectName('gray_label')

        self.helper_layout.addWidget(self.pan_image)
        self.helper_layout.addWidget(self.pan_label)
        self.helper_layout.addSpacerItem(QtWidgets.QSpacerItem(12, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.helper_layout.addWidget(self.zoom_image)
        self.helper_layout.addWidget(self.zoom_label)
        self.helper_layout.addSpacerItem(QtWidgets.QSpacerItem(12, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.helper_layout.addWidget(self.horizontal_zoom_image)
        self.helper_layout.addWidget(self.horizontal_zoom_label)
        self.helper_layout.addSpacerItem(QtWidgets.QSpacerItem(12, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.helper_layout.addWidget(self.vertical_zoom_image)
        self.helper_layout.addWidget(self.vertical_zoom_label)
        self.helper_layout.addSpacerItem(QtWidgets.QSpacerItem(12, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.helper_layout.addWidget(self.focus_image)
        self.helper_layout.addWidget(self.focus_label)
        self.helper_layout.addSpacerItem(QtWidgets.QSpacerItem(12, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.reset_button = QtWidgets.QPushButton("Default")
        self.reset_button.setFixedHeight(30)
        self.reset_button.setStyleSheet("QPushButton{padding:0px;padding-left:5px;padding-right:5px;}")
        self.helper_layout.addWidget(self.reset_button)

        self.today_button = QtWidgets.QPushButton("Today")
        self.today_button.setFixedHeight(30)
        self.today_button.setStyleSheet("QPushButton{padding:0px;padding-left:5px;padding-right:5px;}")
        self.helper_layout.addWidget(self.today_button)

class calendar_viewport(QtWidgets.QGraphicsView):

    scene_rect_update = pyqtSignal(object)
    scale_factor_update = pyqtSignal(object)
    zoom_factor_update = pyqtSignal(object)
    column_width_update = pyqtSignal(object)
    row_height_update = pyqtSignal(object)
    current_selection_changed = pyqtSignal(object)
    movement_stopped = pyqtSignal(object)

    def __init__(self):
        super(calendar_viewport, self).__init__()

        self.scene = scene()
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing, False)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.pan = False
        self.column_width = 100
        self.row_height = 40
        self.last_mouse_pos = None
        self.min_zoom = 0.01
        self.max_zoom = 2.0
        self.zoom_factor = 1.0
        self.y_pos = 0
        self.items = []
        self.frames = []
        self.scene.zoom_factor = self.zoom_factor
        self.start_selection_drag = None
        self.movement = False
        self.selection_item = selection_item()

        empty_item = custom_graphic_item()
        self.scene.addItem(empty_item)
        self.move_scene_center_to_top()

        self.viewport_helper = viewport_helper(self)
        self.viewport_helper.move(0, self.height()-self.viewport_helper.height())
        self.connect_functions()
        self.update_infos()

    def connect_functions(self):
        self.viewport_helper.reset_view.connect(self.reset_view)
        self.viewport_helper.goto_today.connect(self.goto_today)

    def update_infos(self):
        selection_list = []
        visible_list = []
        for item in self.items:
            if item.selected:
                selection_list.append(item)
            if item.isVisible():
                visible_list.append(item)
        self.viewport_helper.selected_label.setText(f"{len(selection_list)} selected")
        self.viewport_helper.items_number_label.setText(f"{len(visible_list)}/{len(self.items)} items")

    def reset_view(self):
        self.set_column_width(100)
        self.set_row_height(40)
        self.deselect_all()
        self.selection_changed()
        self.focus_on_selection()

    def goto_today(self):
        point = self.mapToScene(QtCore.QPoint(0,0))
        #self.update_scene_rect(self.sceneRect().translated(-point.x(), 0))
        viewport_center_scene = self.mapToScene(self.viewport().rect().center())
        translation = point - viewport_center_scene
        self.update_scene_rect(self.sceneRect().translated(-viewport_center_scene.x(), 0))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.viewport_helper.move(0, self.height()-self.viewport_helper.height())

    def set_column_width(self, column_width):
        for item in self.items:
            item.set_column_width(column_width)
        self.column_width = column_width
        self.scene.set_column_width(column_width)
        self.column_width_update.emit(column_width)
        self.update()

    def set_row_height(self, row_height):
        for item in self.items:
            item.set_row_height(row_height)
        for frame in self.frames:
            frame.set_row_height(row_height)
        self.row_height = row_height
        self.scene.set_row_height(row_height)
        self.row_height_update.emit(row_height)
        self.update()

    def movement_on_selection(self, delta):
        self.movement = True
        for item in self.items:
            if item.selected:
                item.movement(delta)

    def start_move_on_selection(self):
        for item in self.items:
            if item.selected:
                item.start_move()

    def start_scale_on_selection(self):
        for item in self.items:
            if item.selected:
                item.start_scale()

    def stop_movement_on_selection(self):
        for item in self.items:
            if item.selected:
                item.stop_movement()
        if not self.movement:
            return
        self.movement_stopped.emit(1)
        self.movement = False

    def add_item(self, graphic_item):
        self.items.append(graphic_item)
        self.scene.addItem(graphic_item)
        graphic_item.set_column_width(self.column_width)
        graphic_item.set_row_height(self.row_height)
        graphic_item.signal_manager.movement.connect(self.movement_on_selection)
        graphic_item.signal_manager.start_move.connect(self.start_move_on_selection)
        graphic_item.signal_manager.start_scale.connect(self.start_scale_on_selection)
        graphic_item.signal_manager.stop_movement.connect(self.stop_movement_on_selection)
        graphic_item.signal_manager.select.connect(self.update_selection)
        graphic_item.setPos(QtCore.QPointF(graphic_item.pos().x(), 0))

    def add_space(self, number=1):
        self.y_pos += number*self.row_height

    def reset_y_pos(self):
        self.y_pos = 0

    def organize_items(self, items):
        for item in items:
            if not item.isVisible():
                continue
            item.setPos(item.pos().x(), self.y_pos)
            self.add_space(1)

    def add_frame(self, graphic_item):
        self.frames.append(graphic_item)
        self.scene.addItem(graphic_item)
        graphic_item.set_row_height(self.row_height)

    def remove_item(self, graphic_item):
        if graphic_item in self.items:
            self.items.remove(graphic_item)
            self.scene.removeItem(graphic_item)

    def remove_frame(self, graphic_item):
        if graphic_item in self.frames:
            self.frames.remove(graphic_item)
            self.scene.removeItem(graphic_item)

    def update_selection(self, items):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if not modifiers & QtCore.Qt.ShiftModifier:
            self.deselect_all()
        for item in items:
            if not item.isVisible():
                continue
            item.set_selected(True)
        self.selection_changed()
        self.update_infos()

    def get_selected_items(self):
        selected_items = []
        for item in self.items:
            if item.selected:
                selected_items.append(item)
        return selected_items

    def selection_changed(self):
        self.current_selection_changed.emit(1)

    def update_frames_selection(self, frames):
        items = []
        for frame in frames:
            frame_scene_rect = QtCore.QRectF(frame.pos().x(), frame.pos().y(), frame.width, frame.height)
            for item in self.items:
                item_scene_rect = QtCore.QRectF(item.pos().x(), item.pos().y(), item.width, item.height)
                if not item_scene_rect.intersects(frame_scene_rect):
                    continue
                if item in items:
                    continue
                items.append(item)
        self.update_selection(items)

    def deselect_all(self):
        for item in self.items:
            item.set_selected(False)

    def move_scene_center_to_top(self):
        point = self.mapToScene(QtCore.QPoint(0,0))
        if point.y() <= 0:
            self.update_scene_rect(self.sceneRect().translated(0, -point.y()))

    def update_scene_rect(self, rect):
        self.setSceneRect(rect)
        self.scene_rect_update.emit(rect)

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            self.zoom_column_width(event)
        elif event.modifiers() & QtCore.Qt.ControlModifier:
            self.zoom_row_height(event)
        else:
            self.zoom(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == QtCore.Qt.MiddleButton:
            self.pan = True
            self.last_mouse_pos = event.pos()
        elif event.button() == QtCore.Qt.LeftButton:
            if self.itemAt(event.pos()) not in self.items:
                self.start_selection_drag = event.pos()

    def mouseMoveEvent(self, event):
        if self.pan:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            dx = -delta.x() / self.zoom_factor
            dy = -delta.y() / self.zoom_factor
            point = self.mapToScene(QtCore.QPoint(0,0))
            self.update_scene_rect(self.sceneRect().translated(dx, dy))
        if self.start_selection_drag:
            rect = self.mapToScene(QtCore.QRect(self.start_selection_drag, event.pos()).normalized()).boundingRect()
            if not self.selection_item.scene():
                self.scene.addItem(self.selection_item)
            self.selection_item.setPos(rect.x(), rect.y())
            self.selection_item.set_size(rect.width(), rect.height())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.pan = False
        elif event.button() == QtCore.Qt.LeftButton:
            if self.start_selection_drag:
                rect = self.mapToScene(QtCore.QRect(self.start_selection_drag, event.pos()).normalized()).boundingRect()
                items_intersected = []
                frames_intersected = []
                for item in self.items:
                    item_scene_rect = QtCore.QRectF(item.pos().x(), item.pos().y(), item.width, item.height)
                    if rect.intersects(item_scene_rect):
                        items_intersected.append(item)
                for frame in self.frames:
                    frame_scene_rect = QtCore.QRectF(frame.pos().x(), frame.pos().y(), frame.width, frame.height)
                    if rect.intersects(frame_scene_rect):
                        frames_intersected.append(frame)
                self.start_selection_drag = None
                if self.selection_item.scene():
                    self.scene.removeItem(self.selection_item)
                if len(items_intersected) == 0 and len(frames_intersected) > 0:
                    self.update_frames_selection(frames_intersected)
                else:
                    self.update_selection(items_intersected)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.focus_on_selection()
        else:
            super().keyPressEvent(event)

    def focus_on_selection(self):
        if len(self.items) == 0:
            return
        selected_items = []
        for item in self.items:
            if item.selected:
                selected_items.append(item)
        if len(selected_items) == 0:
            for item in self.items:
                if not item.isVisible():
                    continue
                selected_items.append(item)
        if len(selected_items) == 0:
            return
        bounding_rect = selected_items[0].sceneBoundingRect()
        for item in selected_items[1:]:
            bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        self.focus_on_rect(bounding_rect)

    def zoom_column_width(self, event):
        delta = event.angleDelta().y() / 60.0
        column_width = int(self.column_width+delta*3)
        column_width = min(max(column_width, 20), 500)
        mouse_view_pos = event.pos()
        mouse_scene_pos = self.mapToScene(mouse_view_pos).x() / self.column_width
        self.set_column_width(column_width)
        new_mouse_scene_pos = self.mapToScene(mouse_view_pos).x() / self.column_width
        diff = (new_mouse_scene_pos - mouse_scene_pos) * self.column_width
        self.update_scene_rect(QtCore.QRectF(self.sceneRect().x() - diff,
                                        self.sceneRect().y(),
                                        self.sceneRect().width(),
                                        self.sceneRect().height()))

    def zoom_row_height(self, event):
        delta = event.angleDelta().y() / 60.0
        row_height = int(self.row_height+delta*2)
        row_height = min(max(row_height, 40), 200)
        mouse_view_pos = event.pos()
        mouse_scene_pos = self.mapToScene(mouse_view_pos).y() / self.row_height
        self.set_row_height(row_height)
        new_mouse_scene_pos = self.mapToScene(mouse_view_pos).y() / self.row_height
        diff = (new_mouse_scene_pos - mouse_scene_pos) * self.row_height
        self.update_scene_rect(QtCore.QRectF(self.sceneRect().x(),
                                        self.sceneRect().y()- diff,
                                        self.sceneRect().width(),
                                        self.sceneRect().height()))

    def zoom(self, event):
        current_zoom = self.transform().m22()
        delta = event.angleDelta().y() / 60.0
        zoom_in_factor = 1.1  # Adjust as needed
        zoom_out_factor = 1 / zoom_in_factor
        if delta > 0:
            zoom = zoom_in_factor
        else:
            zoom = zoom_out_factor
        new_zoom = current_zoom * zoom
        new_zoom = min(max(new_zoom, self.min_zoom), self.max_zoom)
        scale_factor = new_zoom / current_zoom
        self.scale_factor_update.emit(scale_factor)
        self.zoom_factor_update.emit(new_zoom)
        mouse_view_pos = event.pos()
        mouse_scene_pos = self.mapToScene(mouse_view_pos)
        self.scale(scale_factor, scale_factor)
        new_mouse_scene_pos = self.mapToScene(mouse_view_pos)
        diff = new_mouse_scene_pos - mouse_scene_pos
        self.zoom_factor = new_zoom
        self.update_scene_rect(QtCore.QRectF(self.sceneRect().x() - diff.x(),
                                self.sceneRect().y() - diff.y(),
                                self.sceneRect().width(),
                                self.sceneRect().height()))
        self.scene.zoom_factor = self.zoom_factor

    def set_zoom(self, zoom_factor):
        if zoom_factor != self.zoom_factor:
            zoom_factor = min(max(zoom_factor, self.min_zoom), self.max_zoom)
            scale_factor = zoom_factor / self.zoom_factor
            self.scale_factor_update.emit(scale_factor)
            self.zoom_factor_update.emit(zoom_factor)
            self.scale(scale_factor, scale_factor)
            self.update_scene_rect(self.sceneRect())
            self.zoom_factor = zoom_factor
            self.scene.zoom_factor = self.zoom_factor

    def focus_on_rect(self, focus_rect):
        if focus_rect is not None:
            target_width = focus_rect.width()
            target_height = focus_rect.height()
            view_width = self.viewport().width()
            view_height = self.viewport().height()
            zoom_factor_width = view_width / (target_width+200)
            zoom_factor_height = view_height / (target_height+200)
            zoom_factor = min(zoom_factor_width, zoom_factor_height)
            self.set_zoom(zoom_factor)
            focus_rect_center_scene = focus_rect.center().toPoint()
            viewport_center_scene = self.mapToScene(self.viewport().rect().center())
            translation = focus_rect_center_scene - viewport_center_scene
            self.update_scene_rect(self.sceneRect().translated(translation.x(), translation.y()))

class calendar_item(custom_graphic_item):

    def __init__(self, date, duration, bg_color):
        super(calendar_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)

        self.column_width = 100
        self.row_height = 40

        self.bg_color = bg_color
        self.date = date
        self.duration = duration
        self.signal_manager = signal_manager()

        self.hover = False
        self.hover_scale_handle = False
        self.handle_size = 20

        self.start_move_pos = 0

        self.moved = False
        self.move = False

        self.actual_width = 0
        self.scale = False

        self.selected = False
        self.moved = False
        self.scaled = False
        self.init_pos_and_size()
        self.cache_scene_painting()

    def set_column_width(self, column_width):
        self.column_width = column_width
        self.recalculate_pos_and_size()
        self.update()

    def set_row_height(self, row_height):
        self.row_height = row_height
        self.recalculate_pos_and_size()
        self.update()

    def recalculate_pos_and_size(self):
        self.prepareGeometryChange()
        self.width = self.duration*self.column_width
        self.height = self.row_height
        pos_x = ((datetime.datetime.today() - self.date ).days) * -self.column_width
        self.setPos(QtCore.QPointF(pos_x, self.pos().y()))

    def init_pos_and_size(self):
        self.prepareGeometryChange()
        self.width = self.duration*self.column_width
        self.height = self.row_height
        pos_x = ((datetime.datetime.today() - self.date ).days) * -self.column_width
        self.setPos(QtCore.QPointF(pos_x, 0))

    def mousePressEvent(self, event):
        if not self.selected and event.button() == QtCore.Qt.LeftButton:
            self.signal_manager.select.emit([self])
        self.start_move_pos = event.pos()
        if event.pos().x() < self.width - self.handle_size:
            self.signal_manager.start_move.emit(1)
        else:
            self.signal_manager.start_scale.emit(1)

    def start_move(self):
        self.move = True
        self.moved = False
        self.scaled = False
    
    def start_scale(self):
        self.actual_width = self.width
        self.scale = True
        self.scaled = False
        self.moved = False

    def stop_movement(self):
        self.move = False
        self.scale = False
        if self.moved:
            self.signal_manager.start_date_modified.emit(1)
        if self.scaled:
            self.signal_manager.duration_modified.emit(1)

    def mouseReleaseEvent(self, event):
        self.signal_manager.stop_movement.emit(1)
        if event.button() == QtCore.Qt.LeftButton:
            if not self.moved and not self.scaled:
                self.signal_manager.select.emit([self])

    def mouseMoveEvent(self, event):
        delta = int((event.pos().x() - self.start_move_pos.x())/self.column_width)*self.column_width
        self.signal_manager.movement.emit(delta)

    def hoverLeaveEvent(self, event):
        self.hover = False
        self.hover_scale_handle = False
        self.update()

    def hoverMoveEvent(self, event):
        self.handle_size = min(max(int(self.width/10+self.margin), 5), 20)
        if event.pos().x() < self.width - self.handle_size:
            self.hover = True
            self.hover_scale_handle = False
        else:
            self.hover = False
            self.hover_scale_handle = True
        self.update()

    def movement(self, delta):
        if self.move:
            self.move_item(delta)
            self.moved = True
        if self.scale:
            self.scale_item(delta)
            self.scaled = True

    def move_item(self, delta):
        self.moveBy(delta, 0)
        self.calculate_new_date()

    def scale_item(self, delta):
        if self.actual_width + delta < self.column_width:
            return
        self.prepareGeometryChange()
        self.width = self.actual_width + delta
        self.duration = self.width/self.column_width
        self.update()

    def calculate_new_date(self):
        self.date = datetime.datetime.combine(datetime.datetime.today().date(), datetime.time(0, 0)) + datetime.timedelta(self.pos().x()/self.column_width)

    def client_rect(self):
        return QtCore.QRectF(self.x+self.margin, self.y+self.margin, self.width - self.margin*2 - 5, self.height - self.margin*2)

    def cache_scene_painting(self):
        self.margin = 4
        self.qt_bg_color = QtGui.QColor(self.bg_color)
        self.qt_handle_color = QtGui.QColor('white')
        self.qt_handle_color.setAlpha(120)
        self.brush = QtGui.QBrush(self.qt_bg_color)
        self.pen = QtGui.QPen(QtGui.QColor('transparent'), 0)
        self.text_pen = QtGui.QPen(QtGui.QColor('white'), 1)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)

        color = self.qt_bg_color.darker(100)
        if self.hover:
            color = self.qt_bg_color.darker(120)
        if self.selected:
            color = self.qt_bg_color.darker(255)
        
        rect = QtCore.QRectF(self.x+self.margin, self.y+self.margin, self.width-self.margin*2, self.height-self.margin*2)
        self.brush.setColor(color)
        painter.setBrush(self.brush)
        painter.drawRoundedRect(rect, self.row_height/10, self.row_height/10)

        if self.hover_scale_handle:
            rect = QtCore.QRectF(self.width-self.margin-self.handle_size, self.y+self.margin, self.handle_size, self.height-self.margin*2)
            self.brush.setColor(self.qt_handle_color)
            painter.setBrush(self.brush)
            painter.drawRoundedRect(rect, self.handle_size/4, self.handle_size/4)

        self.scene().update()

class frame_item(custom_graphic_item):
    def __init__(self, bg_color, frame_label):
        super(frame_item, self).__init__()
        self.bg_color = bg_color
        self.row_height = 40
        self.frame_label = frame_label
        self.signal_manager = signal_manager()
        self.cache_scene_painting()

    def set_row_height(self, row_height):
        self.row_height = row_height
        self.cache_scene_painting()

    def cache_scene_painting(self):
        self.bg_color = QtGui.QColor(self.bg_color)
        self.bg_color.setAlpha(160)
        self.font = QtGui.QFont()
        self.font.setPixelSize(int(self.row_height*1.5))
        self.font.setBold(True)
        font_metrics = QtGui.QFontMetrics(self.font)
        self.text_height = font_metrics.height()
        self.brush = QtGui.QBrush(self.bg_color)
        self.pen = QtGui.QPen(QtGui.QColor('transparent'), 0)
        self.text_pen = QtGui.QPen(QtGui.QColor('white'), 1)

    def paint(self, painter, option, widget):
        rect = self.boundingRect().toRect()
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRoundedRect(rect, 10, 10)
        text_rect = QtCore.QRect(rect.x(), rect.y()-self.text_height-10, 1000, self.text_height)
        painter.setPen(self.text_pen)
        painter.setFont(self.font)
        painter.drawText(text_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, self.frame_label)

class header_scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(header_scene, self).__init__()
        self.column_width = 100

    def set_column_width(self, column_width):
        self.column_width = column_width
        self.update()

    def drawBackground(self, painter, rect):
        color1 = QtGui.QColor('transparent')
        color2 = QtGui.QColor(0,0,0,10)
        start_x = int(rect.left()) // self.column_width
        end_x = int(rect.right()) // self.column_width
        for x in range(start_x, end_x + 1):
            x_pos = x * self.column_width
            column_rect = QtCore.QRectF(x_pos, rect.top()+140, self.column_width, rect.height()-140)
            color = color1 if x % 2 == 0 else color2
            painter.fillRect(column_rect, color)

class scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(scene, self).__init__()
        self.cache_scene_painting()

    def cache_scene_painting(self):
        self.color1 = QtGui.QColor('#2c2c33')
        self.color2 = QtGui.QColor('#29292f')
        self.line_color = QtGui.QColor('#36363b')
        self.today_color = QtGui.QColor(255, 255, 255, 6)
        self.today_line_color = QtGui.QColor(255, 255, 255, 40)
        self.column_width = 100
        self.row_height = 40

    def set_column_width(self, column_width):
        self.column_width = column_width
        self.update()

    def set_row_height(self, row_height):
        self.row_height = row_height
        self.update()

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, self.color1)
        start_x = int(rect.left()) // self.column_width
        end_x = int(rect.right()) // self.column_width
        for x in range(start_x, end_x + 1):
            x_pos = x * self.column_width
            column_rect = QtCore.QRectF(x_pos, rect.top(), self.column_width, rect.height())
            if x % 2 == 0:
                painter.fillRect(column_rect, self.color2)
        first_column_rect = QtCore.QRectF(0, rect.top(), self.column_width, rect.height())
        draw_rect(painter, first_column_rect, bg_color=self.today_color,
                  outline=self.today_line_color)

class selection_item(custom_graphic_item):
    def __init__(self):
        super(selection_item, self).__init__()

    def paint(self, painter, option, widget):
        bg_color = QtGui.QColor(255,255,255,20)
        rect = QtCore.QRectF(self.x, self.y, self.width, self.height)
        draw_rect(painter, rect, bg_color=bg_color)

class today_item(custom_graphic_item):
    def __init__(self):
        super(today_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)

    def paint(self, painter, option, widget):
        color = QtGui.QColor(QtGui.QColor(255,255,255,20))
        pen = QtGui.QPen(QtGui.QColor(255,255,255,60), 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.x, self.y, self.width, self.height)

def draw_text(painter, rectangle, text, color=QtGui.QColor(255,255,255,int(255*0.85)), size=12, bold=False, align=QtCore.Qt.AlignCenter):
    font = QtGui.QFont()
    font.setBold(bold)
    font.setPixelSize(size)
    painter.setFont(font)
    painter.setPen(QtGui.QPen(color, 1))
    painter.drawText(rectangle, align, text)

def draw_rect(painter, rectangle, bg_color, outline=QtGui.QColor('transparent'), outline_width=0, radius=0):
    painter.setPen(QtGui.QPen(outline, outline_width))
    painter.setBrush(QtGui.QBrush(bg_color))
    painter.drawRoundedRect(rectangle, radius, radius)