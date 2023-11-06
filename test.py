from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from wizard.gui import app_utils

import sys
import datetime

class CalendarHeader(QtWidgets.QGraphicsView):
    def __init__(self):
        super(CalendarHeader, self).__init__()
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
        self.column_width = 30
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
        self.today_item.setRect(0,70,int(self.column_width*self.zoom_factor),self.height()-70)

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
            if self.column_width*self.zoom_factor <= 30:
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
                                            30)
            self.week_items[index].setText(week)

        while len(self.week_items) > len(self.weeks_dic.keys()):
            item = self.week_items.pop()
            self.scene.removeItem(item)

        self.pos_y += 30

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
                                            30)
            self.month_items[index].setText(month)

        while len(self.month_items) > len(self.months_dic.keys()):
            item = self.month_items.pop()
            self.scene.removeItem(item)

        self.pos_y += 30

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
                                                40)
            self.year_items[index].setText(year)

        while len(self.year_items) > len(self.years_dic.keys()):
            item = self.year_items.pop()
            self.scene.removeItem(item)
        self.pos_y += 40

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

class day_item(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(day_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.date = datetime.date.today()

    def setRect(self, x, y , width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def setDate(self, date):
        self.date = date

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        red_color = QtGui.QColor(0, 255, 0, 30)  # Red color
        pen = QtGui.QPen(red_color, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(red_color)

        painter.setPen(pen)
        painter.setBrush(brush)

        number_height = self.height/2
        if self.width <= 30:
            number_height = self.height
        rect = QtCore.QRectF(self.x, self.y, self.width, number_height)
        color = QtGui.QColor(255,255,255, int(255*0.85))
        if self.date.strftime("%A") in ['Saturday', 'Sunday']:
            color = QtGui.QColor(255,255,255,50)
        draw_text(painter, rect, self.date.strftime("%d"), color=color, bold=True)
        if self.width > 30:
            rect = QtCore.QRectF(self.x, self.y+self.height/2, self.width, self.height/2)
            draw_text(painter,
                        rect,
                        self.date.strftime("%A")[:3],
                        color=QtGui.QColor(255,255,255,50),
                        bold=False)

class week_item(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(week_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.margin = 1
        self.text = ''

    def setRect(self, x, y , width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def setText(self, text):
        self.text = text

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        red_color = QtGui.QColor(0, 255, 0, 30)  # Red color
        pen = QtGui.QPen(red_color, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(red_color)

        painter.setPen(pen)
        painter.setBrush(brush)

        text = f"Week {self.text}"
        if self.width < 50:
            text = self.text

        rect = QtCore.QRectF(self.x + self.margin,
                                self.y + self.margin,
                                self.width - self.margin*2,
                                self.height - self.margin*2)
        draw_rect(painter, rect, bg_color=QtGui.QColor('#232329'), radius=2)
        draw_text(painter, rect, text, bold=False)

class month_item(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(month_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.margin = 1
        self.text = ''

    def setRect(self, x, y , width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def setText(self, text):
        self.text = text

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        red_color = QtGui.QColor(0, 255, 0, 30)  # Red color
        pen = QtGui.QPen(red_color, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(red_color)

        painter.setPen(pen)
        painter.setBrush(brush)

        rect = QtCore.QRectF(self.x + self.margin,
                                self.y + self.margin,
                                self.width - self.margin*2,
                                self.height - self.margin*2)
        draw_rect(painter, rect, bg_color=QtGui.QColor('#3d3d43'), radius=2)
        draw_text(painter, rect, self.text[4:], bold=False)

class year_item(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(year_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.margin = 8
        self.text = ''

    def setRect(self, x, y , width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def setText(self, text):
        self.text = text

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        red_color = QtGui.QColor(0, 255, 0, 30)  # Red color
        pen = QtGui.QPen(red_color, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(red_color)

        painter.setPen(pen)
        painter.setBrush(brush)

        rect = QtCore.QRectF(self.x + self.margin,
                                self.y + self.margin,
                                self.width - self.margin*2,
                                self.height - self.margin*2)
        draw_text(painter, rect, self.text, size=20, bold=True, align=QtCore.Qt.AlignLeft)

class CalendarViewport(QtWidgets.QGraphicsView):

    scene_rect_update = pyqtSignal(object)
    scale_factor_update = pyqtSignal(object)
    zoom_factor_update = pyqtSignal(object)

    def __init__(self):
        super(CalendarViewport, self).__init__()

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
        self.column_width = 30
        self.last_mouse_pos = None
        self.zoom_factor = 1.0
        self.today_item = today_item()
        self.today_item.setZValue(1.0)
        self.scene.addItem(self.today_item)

        item = empty_item()
        self.scene.addItem(item)
        self.move_scene_center_to_top()

        date_item_1 = calendar_item(datetime.datetime(2023, 11, 6), 8)
        self.scene.addItem(date_item_1)
        date_item_2 = calendar_item(datetime.datetime(2023, 10, 2), 1)
        self.scene.addItem(date_item_2)

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
        else:
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
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.pan = False
        else:
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
        min_zoom = 0.15
        max_zoom = 8.0
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


class header_scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(header_scene, self).__init__()

    def drawBackground(self, painter, rect):
        color1 = QtGui.QColor('transparent')
        color2 = QtGui.QColor(0,0,0,10)
        column_width = 30
        start_x = int(rect.left()) // column_width
        end_x = int(rect.right()) // column_width
        for x in range(start_x, end_x + 1):
            x_pos = x * column_width
            column_rect = QtCore.QRectF(x_pos, rect.top()+70, column_width, rect.height()-70)
            color = color1 if x % 2 == 0 else color2
            painter.fillRect(column_rect, color)

class scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(scene, self).__init__()

    def drawBackground(self, painter, rect):
        color1 = QtGui.QColor('transparent')
        color2 = QtGui.QColor(0,0,0,20)
        line_color = QtGui.QColor(255, 255, 255, 5)
        column_width = 30 
        row_height = 30
        start_y = int(rect.top()) // row_height
        end_y = int(rect.bottom()) // row_height
        for y in range(start_y, end_y + 2):
            y_pos = y * row_height
            line = QtCore.QLineF(rect.left(), y_pos, rect.right(), y_pos)
            painter.setPen(QtGui.QPen(line_color, 1, QtCore.Qt.SolidLine))
            painter.drawLine(line)
        start_x = int(rect.left()) // column_width
        end_x = int(rect.right()) // column_width
        for x in range(start_x, end_x + 1):
            x_pos = x * column_width
            column_rect = QtCore.QRectF(x_pos, rect.top(), column_width, rect.height())
            color = color1 if x % 2 == 0 else color2
            painter.fillRect(column_rect, color)
            if x_pos == 0:
                draw_rect(painter, column_rect, bg_color=QtGui.QColor(255,255,255,3), outline=QtGui.QColor(255,255,255,20))
        
class empty_item(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(empty_item, self).__init__()
        self.x = 0
        self.y = 0
        self.width = 1
        self.height = 1

    def setRect(self, x, y , width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        color = QtGui.QColor('transparent')
        pen = QtGui.QPen(QtGui.QColor('red'), 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.x, self.y, self.width, self.height)

class today_item(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(today_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    def setRect(self, x, y , width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        color = QtGui.QColor(QtGui.QColor(255,255,255,3))
        pen = QtGui.QPen(QtGui.QColor(255,255,255,20), 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.x, self.y, self.width, self.height)

class calendar_item(QtWidgets.QGraphicsItem):
    def __init__(self, date, duration):
        super(calendar_item, self).__init__()
        self.date = date
        self.duration = duration
        self.move = False
        self.set_rect()

    def set_rect(self):
        self.x = ((datetime.datetime.today() - self.date ).days) * -30
        self.y = 0
        self.width = (self.duration) * 30
        self.height = 30

    def mousePressEvent(self, event):
        print('ZIZI')
        if event.button() == QtCore.Qt.LeftButton:
            self.move = True
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.move:
            print(self.mapToItem(self, event.pos()).x())
            delta = int((self.mapToScene(event.pos()).x())/30)
            self.date = datetime.datetime.today() + datetime.timedelta(days=delta)
            self.set_rect()
            self.scene().update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.move = False
        else:
            super().mouseReleaseEvent(event)

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        color = QtGui.QColor(QtGui.QColor(255,255,255,3))
        rect = QtCore.QRectF(self.x, self.y, self.width, self.height)
        draw_rect(painter, rect, bg_color = QtGui.QColor(255,0,0,60))

class calendarWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(calendarWidget, self).__init__(parent)

        self.resize(800, 600)

        self.header_view = CalendarHeader()
        self.view = CalendarViewport()

        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.view.scene_rect_update.connect(self.header_view.update_rect)
        self.view.scale_factor_update.connect(self.header_view.update_scale)
        self.view.zoom_factor_update.connect(self.header_view.update_zoom_factor)

    def build_ui(self):
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.header_view)
        self.main_layout.addWidget(self.view)

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

app = app_utils.get_app()

w= calendarWidget()
w.show()

app.exec_()