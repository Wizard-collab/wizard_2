# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import traceback
from datetime import datetime, timedelta

# Wizard modules
from wizard.core import calendar_utils

class calendarWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(calendarWidget, self).__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.init_days_range()
        self.display_type = 2
        self.zoom_factor = 1
        self.selection_region_drag = False
        self.selection_region_start = None
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.viewport_pos_y = 0
        self.items = []

    def init_days_range(self):
        today = datetime.today()
        self.start_date = today - timedelta(days=50)
        self.end_date = today + timedelta(days=50)

    def add_item(self, date, duration, color, widget):
        self.item = item_object(date, duration, color, widget, parent=self)
        self.item.select_signal.connect(self.select_item)
        self.items.append(self.item)

    def select_region(self, pos):
        rect = QtCore.QRectF(self.selection_region_start, pos)
        under_region = []
        for item in self.items:
            if rect.contains(QtCore.QRectF(item.x(), item.y(), item.width(), item.height())):
                under_region.append(item)
        self.select_multiple_items(under_region)

    def toggle_item_selection(self, item):
        item.selected = 1-item.selected
        item.update()

    def select_item(self, item):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if not modifiers & QtCore.Qt.ShiftModifier:
            self.deselect_all()
        if modifiers & QtCore.Qt.ShiftModifier:
            item.selected = 1-item.selected
            item.update()
        else:
            item.selected = True
            item.update()

    def select_multiple_items(self, items):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if not modifiers & QtCore.Qt.ShiftModifier:
            self.deselect_all()
        if modifiers & QtCore.Qt.ShiftModifier:
            for item in items:
                item.selected = 1 - item.selected 
                item.update()
        else:
            for item in items:
                item.selected = True
                item.update()

    def deselect_all(self):
        for item in self.items:
            self.deselect_item(item)

    def deselect_item(self, item):
        item.selected = False
        item.update()

    def get_selected_items(self):
        selected_items = []
        for item in self.items:
            if item.selected:
                selected_items.append(item)
        return selected_items

    def paintEvent(self, event):
        self.years_dic, self.months_dic, self.weeks_dic, self.days_dic = calendar_utils.get_days_in_range(self.start_date, self.end_date)
        try:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)

            self.position = 0
            self.main_area = QtCore.QRectF(0,0,self.width(), self.height())
            self.day_width = self.width()/len(self.days_dic.keys())
            self.draw_years()
            self.draw_months()
            self.draw_days()
            self.draw_weeks()
            self.draw_items()
            self.draw_current_day()
            self.draw_selection_region()
        except:
            print(str(traceback.format_exc()))

    def draw_selection_region(self):
        painter = QtGui.QPainter(self)
        if self.selection_region_drag:
            rectangle = QtCore.QRectF(self.selection_region_start, self.mapFromGlobal(QtGui.QCursor.pos()))
            draw_rect(painter, rectangle, bg_color=QtGui.QColor(255,255,255,20))

    def draw_items(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)

        pos_y = self.years_section_height + self.month_section_height + self.day_section_height + self.weeks_section_height

        for item in self.items:
            self.items_height = self.day_width
            #if self.items_height > 40:
            #    self.items_height = 40
            #if self.items_height < 10:
            #    self.items_height = 10
            pos_y += self.items_height#+4
            pos_x_1 = self.get_pos_from_date(item.date)
            width = item.duration * self.day_width
            item.day_width = self.day_width
            item_pos_y = int(pos_y-self.viewport_pos_y)
            item.move(int(pos_x_1), item_pos_y)
            item.resize(int(width), int(self.items_height))
            if item_pos_y < (self.years_section_height + self.month_section_height + self.day_section_height + self.weeks_section_height):
                item.setVisible(False)
            else:
                item.setVisible(True)

    def get_day_position(self, day_id):
        index = list(self.days_dic.keys()).index(day_id)
        pos_x = self.day_width*(index)
        return pos_x

    def draw_current_day(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        today_id = calendar_utils.get_current_day_id()
        if today_id not in self.days_dic.keys():
            return
        rectangle = QtCore.QRectF(self.get_day_position(today_id), self.years_section_height + self.month_section_height, self.day_width, self.height())
        draw_rect(painter, rectangle, QtGui.QColor('transparent'), QtGui.QColor(255,255,255,70), 1, 4)
        if self.day_width<20:
            rectangle = QtCore.QRectF((self.get_day_position(today_id)+self.day_width/2)-10-4, self.years_section_height + self.month_section_height-4, 28, 28)
            draw_rect(painter, rectangle, QtGui.QColor('#52525c'), QtGui.QColor('transparent'), 1, 14)
            draw_text(painter, rectangle, self.days_dic[today_id]['day_number'], bold=True)

    def draw_days(self):
        painter = QtGui.QPainter(self)
        draw_alternate_bg = 1
        for day_id in self.days_dic.keys():
            self.day_section_height = 0
            
            day_pos = self.get_day_position(day_id)
            number = self.days_dic[day_id]['day_number']
            name = self.days_dic[day_id]['day_name'][:3]

            rectangle = QtCore.QRectF(day_pos, self.years_section_height + self.month_section_height, self.day_width, self.height())
            draw_rect(painter, rectangle, bg_color=QtGui.QColor(0,0,0,10*draw_alternate_bg))

            if self.day_width > 20:
                text_color = QtGui.QColor(255,255,255,int(255*0.9))
                if name in ['Sat', 'Sun']:
                    text_color = QtGui.QColor(255,255,255,int(255*0.4))
                text_rect = QtCore.QRectF(day_pos,
                                        self.years_section_height + self.month_section_height,
                                        self.day_width,
                                        20)
                draw_text(painter, text_rect, number, text_color, 12, True)
                self.day_section_height += 20

            if self.day_width > 30:
                text_rect = QtCore.QRectF(day_pos,
                                    self.years_section_height + self.month_section_height + self.day_section_height,
                                    self.day_width,
                                    10)
                draw_text(painter, text_rect, name, QtGui.QColor(255,255,255,int(255*0.4)), 12, False)
                self.day_section_height += 10

            draw_alternate_bg = 1-draw_alternate_bg

    def draw_weeks(self):
        if self.day_width < 5:
            return
        painter = QtGui.QPainter(self)
        margin = 2
        weeks = list(self.weeks_dic.keys())
        
        for week in weeks:
            name = f"Week {week}"
            if self.day_width < 20:
                name = week
            days_range = self.weeks_dic[week]
            point_x_1 = self.get_day_position(days_range[0])
            point_x_2 = self.get_day_position(days_range[-1]) + self.day_width
            rectangle = QtCore.QRectF(point_x_1 + margin,
                            self.years_section_height + self.month_section_height + self.day_section_height + margin,
                            point_x_2-point_x_1-margin*2,
                            20)
            draw_rect(painter, rectangle, bg_color=QtGui.QColor('#232329'), radius=4)
            draw_text(painter, rectangle, name)

        self.weeks_section_height = 30

    def draw_months(self):
        painter = QtGui.QPainter(self)
        margin = 2
        months = list(self.months_dic.keys())
        for month in months:
            days_range = self.months_dic[month]
            name = self.days_dic[days_range[0]]['month_name']
            if self.day_width < 2:
                name = name[:3]
            point_x_1 = self.get_day_position(days_range[0])
            point_x_2 = self.get_day_position(days_range[-1]) + self.day_width

            rectangle = QtCore.QRectF(point_x_1 + margin, self.years_section_height+margin, point_x_2-point_x_1-margin*2, 25)
            draw_rect(painter, rectangle, bg_color=QtGui.QColor('#3d3d43'), radius=4)
            draw_text(painter, rectangle, name, size=15, bold=True)

        self.month_section_height = 29

    def draw_years(self):
        painter = QtGui.QPainter(self)
        margin = 10
        years = list(self.years_dic.keys())
        for year in years:
            days_range = self.years_dic[year]
            name = year
            point_x_1 = self.get_day_position(days_range[0])
            point_x_2 = self.get_day_position(days_range[-1]) + self.day_width
            rectangle = QtCore.QRectF(point_x_1 + margin, margin, point_x_2-point_x_1-margin*2, 40)
            draw_text(painter, rectangle, name, size=20, bold=True, align=QtCore.Qt.AlignLeft)
        self.years_section_height = 40

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.selection_region_drag = False
            self.dragging = True
            self.drag_start_x = event.x()
            self.drag_start_y = event.y()
            return
        if event.button() == QtCore.Qt.LeftButton:
            for item in self.items:
                if item.rect().contains(event.pos()):
                    self.selection_region_drag = False
                    break
            self.dragging = False
            self.selection_region_drag = True
            self.selection_region_start = event.pos()
            return
        self.dragging = False
        self.selection_region_drag = False

    def get_day_from_pos(self, pos_x):
        first_day_dic = self.days_dic[list(self.days_dic.keys())[0]]
        first_day_id = list(self.days_dic.keys())[0]
        first_day_datetime = datetime(int(first_day_dic['year']),
                                        int(first_day_dic['month_number']),
                                        int(first_day_dic['day_number']))
        delta = int(pos_x/self.day_width)
        date = first_day_datetime + timedelta(days=delta)
        return date

    def get_pos_from_date(self, date):
        first_day_dic = self.days_dic[list(self.days_dic.keys())[0]]
        first_day_id = list(self.days_dic.keys())[0]
        first_day_datetime = datetime(int(first_day_dic['year']),
                                        int(first_day_dic['month_number']),
                                        int(first_day_dic['day_number']))
        delta = (date - first_day_datetime).days
        pos = delta*self.day_width
        return pos

    def mouseMoveEvent(self, event):
        selected_items = self.get_selected_items()
        move_items = False
        scale_items = False
        move_offset = 0
        for item in self.items:
            if item.move_dragging:
                date_from_pos = self.get_day_from_pos(event.pos().x() - item.move_dragging_offset)
                if not date_from_pos:
                    continue
                move_offset = date_from_pos - item.date
                move_items = True
            if item.scale_dragging:
                date_from_pos = self.get_day_from_pos(event.pos().x())
                if not date_from_pos:
                    continue
                scale_offset = (date_from_pos - item.date).days - item.duration
                scale_items = True
        if move_items:
            for item in selected_items:
                item.date += move_offset
                item.update()
        if scale_items:
            for item in selected_items:
                item.duration += scale_offset
                if item.duration <= 0:
                    item.duration = 1
                item.update()

        if self.dragging:
            delta_x = event.x() - self.drag_start_x
            delta_y = event.y() - self.drag_start_y

            start_date = self.start_date - timedelta(days=0.2*delta_x/(self.day_width/5))
            end_date = self.end_date - timedelta(days=0.2*delta_x/(self.day_width/5))
            self.update_date_range(start_date, end_date)

            self.viewport_pos_y -= delta_y
            self.drag_start_x = event.x()
            self.drag_start_y = event.y()
            self.update()

        if self.selection_region_drag:
            self.update()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_F:
            self.center_around_selection()
            self.update()

    def update_date_range(self, start_date, end_date):
        old_days_range = (self.end_date - self.start_date).days
        new_days_range = (end_date - start_date).days
        self.start_date = start_date
        self.end_date = end_date
        if new_days_range == old_days_range:
            return
        self.zoom_factor = old_days_range/new_days_range

        header_height = self.years_section_height + self.month_section_height + self.day_section_height + self.weeks_section_height
        mouse_pos = self.mapFromGlobal(QtGui.QCursor().pos()).y() - header_height
        y_range = self.height() - header_height
        mouse_pos_factor = mouse_pos/y_range
        bottom_space = y_range - mouse_pos

        #middle_pos = y_range/2
        #mouse_pos = (mouse_pos)-middle_pos
        #if mouse_pos <=0:
        #    mouse_pos = 0


        if self.zoom_factor < 1:
            self.viewport_pos_y -= ((y_range*self.zoom_factor)*mouse_pos_factor)/12
        else:
            self.viewport_pos_y += ((y_range*self.zoom_factor)*mouse_pos_factor)/12
        self.viewport_pos_y *= self.zoom_factor

    def center_around_selection(self):
        min_pos_x = 10000
        max_pos_x = 0
        selected_items = self.get_selected_items()
        if selected_items:
            for item in selected_items:
                if not item.selected:
                    continue
                if item.x() < min_pos_x:
                    min_pos_x = item.x()
                if item.x()+item.width() > max_pos_x:
                    max_pos_x = item.x()+item.width()

            width = max_pos_x - min_pos_x
            min_pos_x -= width/2
            max_pos_x += width/2

            self.update_date_range(self.get_day_from_pos(min_pos_x),
                                    self.get_day_from_pos(max_pos_x))
        else:
            current_date = datetime.today()
            days_to_center = len(self.days_dic.keys())/2

            self.update_date_range((current_date - timedelta(days=days_to_center)),
                                    (current_date + timedelta(days=days_to_center)))

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
        if self.selection_region_drag:
            self.select_region(event.pos())
            self.selection_region_drag = False
            self.update()

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            delta = event.angleDelta().y() / 10

            left_space = self.width()/event.pos().x()
            right_space = self.width()/(self.width() - event.pos().x())

            start_date = self.start_date + timedelta(days=1*delta/(self.day_width/10)/left_space)
            end_date = self.end_date - timedelta(days=1*delta/(self.day_width/10)/right_space)

            time_delta = end_date - start_date

            if time_delta.days < 8 or time_delta.days > 500:
                return

            self.update_date_range(start_date,
                                    end_date)
            self.update()

class item_object(QtWidgets.QWidget):

    select_signal = pyqtSignal(object)

    def __init__(self, date, duration, color, widget, parent=None):
        super(item_object, self).__init__(parent)
        self.setMouseTracking(True)
        self.setObjectName('transparent_widget')
        self.widget = widget
        self.date = date
        self.duration = duration
        self.color = color
        self.day_width = None

        self.hover = False
        self.selected = False

        self.show_right_handle = False

        self.move_dragging = False
        self.move_dragging_offset = 0
        self.move_drag_start_x = 0

        self.scale_dragging = False
        self.scale_drag_start_x = 0

        self.build_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(6,1,1,1)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.widget)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)

        main_area = QtCore.QRectF(0,0,self.width(), self.height())
        left_rect = QtCore.QRectF(0,0,5, self.height())
        color = QtGui.QColor(self.color)
        alpha_color = QtGui.QColor(color.red(), color.green(), color.blue(), 100)
        if self.hover and not self.selected:
            alpha_color = alpha_color.lighter(110)
        elif self.hover and self.selected:
            alpha_color = QtGui.QColor(color.red(), color.green(), color.blue(), 200)
            alpha_color = alpha_color.lighter(125)
        elif not self.hover and self.selected:
            alpha_color = QtGui.QColor(color.red(), color.green(), color.blue(), 200)
            alpha_color = alpha_color.lighter(120)

        draw_rect(painter, main_area, bg_color = alpha_color, radius=1)
        draw_rect(painter, left_rect, bg_color = color, radius=1)

        if self.show_right_handle:
            rect = QtCore.QRectF(self.width()-5,0,5, self.height())
            draw_rect(painter, rect, bg_color = QtGui.QColor(255,255,255,200), radius=2)
        super().paintEvent(event)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.show_right_handle = False
        self.hover = False
        self.update()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.hover = True
        self.update()

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            super().mouseMoveEvent(event)
            return
        
        if 0 < event.pos().x() < self.width()-10:
            self.move_dragging = True
            self.move_dragging_offset = event.pos().x()
        if self.width()-10 < event.pos().x() < self.width():
            self.move_dragging = False
            self.scale_dragging = True
        if not self.selected:
            self.select_signal.emit(self)

    def mouseReleaseEvent(self, event):
        if self.move_dragging:
            self.move_dragging = False
        if self.scale_dragging:
            self.scale_dragging = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        if self.width()-10 < event.pos().x() < self.width():
            self.show_right_handle = True
        else:
            self.show_right_handle = False
        self.update()

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
