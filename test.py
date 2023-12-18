from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from wizard.gui import app_utils

import sys
import datetime
import time
import random

class signal_manager(QtCore.QObject):

    movement = pyqtSignal(int)
    stop_movement = pyqtSignal(int)
    start_move = pyqtSignal(int)
    start_scale = pyqtSignal(int)
    select = pyqtSignal(object)

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
        self.setFixedHeight(120)
        self.scene = header_scene()
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
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
        self.today_item.setRect(0,200,int(self.column_width*self.zoom_factor),self.height()-200)

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
            week = day.strftime("%W")
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
        red_color = QtGui.QColor(0, 255, 0, 40)  # Red color
        pen = QtGui.QPen(red_color, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(red_color)

        painter.setPen(pen)
        painter.setBrush(brush)

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
        red_color = QtGui.QColor(0, 255, 0, 40)  # Red color
        pen = QtGui.QPen(red_color, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(red_color)

        painter.setPen(pen)
        painter.setBrush(brush)

        text = f"Week {self.text}"
        if self.width < 100:
            text = self.text

        rect = QtCore.QRectF(self.x + self.margin,
                                self.y + self.margin,
                                self.width - self.margin*2,
                                self.height - self.margin*2)
        draw_rect(painter, rect, bg_color=QtGui.QColor('#232329'), radius=2)
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
        red_color = QtGui.QColor(0, 255, 0, 40)  # Red color
        pen = QtGui.QPen(red_color, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(red_color)

        painter.setPen(pen)
        painter.setBrush(brush)

        rect = QtCore.QRectF(self.x + self.margin,
                                self.y + self.margin,
                                self.width - self.margin*2,
                                self.height - self.margin*2)
        draw_rect(painter, rect, bg_color=QtGui.QColor('#3d3d43'), radius=4)
        draw_text(painter, rect, self.text[4:], bold=False)

class year_item(custom_graphic_item):
    def __init__(self):
        super(year_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.margin = 4
        self.text = ''

    def setText(self, text):
        self.text = text

    def paint(self, painter, option, widget):
        red_color = QtGui.QColor(0, 255, 0, 40)  # Red color
        pen = QtGui.QPen(red_color, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(red_color)

        painter.setPen(pen)
        painter.setBrush(brush)

        rect = QtCore.QRectF(self.x + self.margin,
                                self.y + self.margin,
                                self.width - self.margin*2,
                                self.height - self.margin*2)
        draw_text(painter, rect, self.text, size=20, bold=True, align=QtCore.Qt.AlignLeft)

class calendar_viewport(QtWidgets.QGraphicsView):

    scene_rect_update = pyqtSignal(object)
    scale_factor_update = pyqtSignal(object)
    zoom_factor_update = pyqtSignal(object)

    def __init__(self):
        super(calendar_viewport, self).__init__()

        self.scene = scene()
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
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
        self.items = []
        self.scene.addItem(self.today_item)
        self.scene.zoom_factor = self.zoom_factor
        self.start_selection_drag = None
        self.selection_item = selection_item()

        empty_item = custom_graphic_item()
        self.scene.addItem(empty_item)
        self.move_scene_center_to_top()

    def movement_on_selection(self, delta):
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

    def add_item(self, graphic_item):
        self.items.append(graphic_item)
        self.scene.addItem(graphic_item)
        graphic_item.signal_manager.movement.connect(self.movement_on_selection)
        graphic_item.signal_manager.start_move.connect(self.start_move_on_selection)
        graphic_item.signal_manager.start_scale.connect(self.start_scale_on_selection)
        graphic_item.signal_manager.stop_movement.connect(self.stop_movement_on_selection)
        graphic_item.signal_manager.select.connect(self.update_selection)
        graphic_item.setPos(QtCore.QPointF(graphic_item.pos().x(), (len(self.items)-1)*40))

    def remove_item(self, graphic_item):
        if graphic_item in self.items:
            self.scene.removeItem(graphic_item)

    def update_selection(self, item):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if not modifiers & QtCore.Qt.ShiftModifier:
            self.deselect_all()
        item.set_selected(True)

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.move_scene_center_to_top()

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            self.zoom(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.pan = True
            self.last_mouse_pos = event.pos()
        elif event.button() == QtCore.Qt.LeftButton:
            if self.itemAt(event.pos()) not in self.items:
                self.start_selection_drag = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pan:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            dx = -delta.x() / self.zoom_factor
            dy = -delta.y() / self.zoom_factor
            point = self.mapToScene(QtCore.QPoint(0,0))
            if point.y() + dy <= 0:
                dy = -point.y()
            self.update_scene_rect(self.sceneRect().translated(dx, dy))
        if self.start_selection_drag:
            rect = self.mapToScene(QtCore.QRect(self.start_selection_drag, event.pos()).normalized()).boundingRect()
            if not self.selection_item.scene():
                self.scene.addItem(self.selection_item)
            self.selection_item.setPos(rect.x(), rect.y())
            self.selection_item.set_size(rect.width(), rect.height())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.pan = False

        elif event.button() == QtCore.Qt.LeftButton:
            if self.start_selection_drag:
                rect = self.mapToScene(QtCore.QRect(self.start_selection_drag, event.pos()).normalized()).boundingRect()
                self.start_selection_drag = None
                if self.selection_item.scene():
                    self.scene.removeItem(self.selection_item)
                if not event.modifiers() & QtCore.Qt.ShiftModifier:
                    self.deselect_all()
                for item in self.items:
                    item_scene_rect = QtCore.QRectF(item.pos().x(), item.pos().y(), item.width, item.height)
                    if rect.intersects(item_scene_rect):
                        item.set_selected(True)

        super().mouseReleaseEvent(event)

    def zoom(self, event):
        current_zoom = self.transform().m22()
        delta = event.angleDelta().y() / 120.0
        zoom_in_factor = 1.1  # Adjust as needed
        zoom_out_factor = 1 / zoom_in_factor
        if delta > 0:
            zoom = zoom_in_factor
        else:
            zoom = zoom_out_factor
        min_zoom = 0.04
        max_zoom = 2.0
        new_zoom = current_zoom * zoom
        new_zoom = min(max(new_zoom, min_zoom), max_zoom)
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
        self.move_scene_center_to_top()
        self.scene.zoom_factor = self.zoom_factor

class calendar_item(custom_graphic_item):

    def __init__(self, date, duration, bg_color):
        super(calendar_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)

        self.bg_color = bg_color
        self.date = date
        self.duration = duration
        self.signal_manager = signal_manager()

        self.hover = False
        self.hover_scale_handle = False

        self.start_move_pos = 0

        self.moved = False
        self.move = False

        self.actual_width = 0
        self.scale = False

        self.selected = False
        self.moved_or_scaled = False
        self.init_pos_and_size()

    def init_pos_and_size(self):
        self.prepareGeometryChange()
        self.width = self.duration*100
        self.height = 40
        pos_x = ((datetime.datetime.today() - self.date ).days) * -100
        self.setPos(QtCore.QPointF(pos_x, 0))

    def mousePressEvent(self, event):
        if not self.selected:
            self.signal_manager.select.emit(self)
        self.start_move_pos = event.pos()
        if event.pos().x() < self.width - 20:
            self.signal_manager.start_move.emit(1)
        else:
            self.signal_manager.start_scale.emit(1)

    def start_move(self):
        self.move = True
        self.moved_or_scaled = False
    
    def start_scale(self):
        self.actual_width = self.width
        self.scale = True
        self.moved_or_scaled = False

    def stop_movement(self):
        self.move = False
        self.scale = False

    def mouseReleaseEvent(self, event):
        self.signal_manager.stop_movement.emit(1)
        if not self.moved_or_scaled:
            self.signal_manager.select.emit(self)

    def mouseMoveEvent(self, event):
        delta = int((event.pos().x() - self.start_move_pos.x())/100)*100
        self.signal_manager.movement.emit(delta)

    def hoverLeaveEvent(self, event):
        self.hover = False
        self.hover_scale_handle = False
        self.update()

    def hoverMoveEvent(self, event):
        if event.pos().x() < self.width - 20:
            self.hover = True
            self.hover_scale_handle = False
        else:
            self.hover = False
            self.hover_scale_handle = True
        self.update()

    def movement(self, delta):
        if self.move:
            self.move_item(delta)
        if self.scale:
            self.scale_item(delta)
        self.moved_or_scaled = True

    def move_item(self, delta):
        self.moveBy(delta, 0)
        self.calculate_new_date()

    def scale_item(self, delta):
        if self.actual_width + delta < 100:
            return
        self.prepareGeometryChange()
        self.width = self.actual_width + delta
        self.duration = self.width/100
        self.update()

    def calculate_new_date(self):
        self.date = datetime.datetime.combine(datetime.datetime.today().date(), datetime.time(0, 0)) + datetime.timedelta(self.pos().x()/100)

    def client_rect(self):
        margin = 4
        return QtCore.QRectF(self.x+margin, self.y+margin, self.width - margin*2 - 5, self.height - margin*2)

    def paint(self, painter, option, widget):
        margin = 4
        bg_color = QtGui.QColor(self.bg_color)
        bg_color.setAlpha(100)
        if self.hover:
            bg_color.setAlpha(120)
        if self.selected:
            bg_color.setAlpha(140)
        rect = QtCore.QRectF(self.x+margin, self.y+margin, self.width-margin*2, self.height-margin*2)
        #if self.hover or self.hover_scale_handle:
        #    rect = QtCore.QRectF(self.x+margin, self.y+margin, self.width-margin*2, self.height*1.5-margin*2)
        draw_rect(painter, rect, bg_color = bg_color, radius=2)
        if self.hover_scale_handle:
            rect = QtCore.QRectF(self.width-margin-10, self.y+margin, 10, self.height-margin*2)
            bg_color.setAlpha(160)
            draw_rect(painter, rect, bg_color = bg_color, radius=2)
        self.scene().update()

class header_scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(header_scene, self).__init__()

    def drawBackground(self, painter, rect):
        color1 = QtGui.QColor('transparent')
        color2 = QtGui.QColor(0,0,0,10)
        column_width = 100
        start_x = int(rect.left()) // column_width
        end_x = int(rect.right()) // column_width
        for x in range(start_x, end_x + 1):
            x_pos = x * column_width
            column_rect = QtCore.QRectF(x_pos, rect.top()+140, column_width, rect.height()-140)
            color = color1 if x % 2 == 0 else color2
            painter.fillRect(column_rect, color)

class scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(scene, self).__init__()

    def drawBackground(self, painter, rect):
        color1 = QtGui.QColor('transparent')
        color2 = QtGui.QColor(0, 0, 0, 20)
        line_color = QtGui.QColor(255, 255, 255, 5)
        column_width = 100
        row_height = 40

        if self.zoom_factor > 0.1:
            start_x = int(rect.left()) // column_width
            end_x = int(rect.right()) // column_width

            for x in range(start_x, end_x + 1):
                x_pos = x * column_width
                column_rect = QtCore.QRectF(x_pos, rect.top(), column_width, rect.height())
                color = color1 if x % 2 == 0 else color2
                painter.fillRect(column_rect, color)
        else:
            start_x = int(rect.left()) // column_width*7
            end_x = int(rect.right()) // column_width*7

            for x in range(start_x, end_x + 1):
                x_pos = x * column_width * 7
                column_rect = QtCore.QRectF(x_pos, rect.top(), column_width*7, rect.height())
                color = color1 if x % 2 == 0 else color2
                painter.fillRect(column_rect, color)

        start_y = int(rect.top()) // row_height
        end_y = int(rect.bottom()) // row_height

        if len(list(range(start_y, end_y + 2))) < 50:
            for y in range(start_y, end_y + 2):
                y_pos = y * row_height
                line = QtCore.QLineF(rect.left(), y_pos, rect.right(), y_pos)
                painter.setPen(QtGui.QPen(line_color, 1, QtCore.Qt.SolidLine))
                painter.drawLine(line)

        # Highlight the first column
        first_column_rect = QtCore.QRectF(0, rect.top(), column_width, rect.height())
        draw_rect(painter, first_column_rect, bg_color=QtGui.QColor(255, 255, 255, 3),
                  outline=QtGui.QColor(255, 255, 255, 20))

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
        color = QtGui.QColor(QtGui.QColor(255,255,255,3))
        pen = QtGui.QPen(QtGui.QColor(255,255,255,20), 1, QtCore.Qt.SolidLine)
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