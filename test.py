from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from wizard.gui import app_utils

import sys
import datetime

class CalendarHeader(QtWidgets.QGraphicsView):
    def __init__(self):
        super(CalendarHeader, self).__init__()
        self.setFixedHeight(60)
        self.scene = header_scene()
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.pan = False
        self.column_width = 30
        self.last_mouse_pos = None
        self.zoom_factor = 1.0

        x, y, width, height = 0, 0, 30, 60  # Adjust the position and size as needed
        red_box_item = RedBoxItem(x, y, width, height)
        self.scene.addItem(red_box_item)

        # Define the number of days to display in the header
        self.all_days = []
        self.day_items = []
        self.update_days()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_days()

    def update_days(self):
        leftmost_column, visible_columns = self.get_visible_columns()
        self.today = datetime.date.today()
        self.days_range = range(leftmost_column, leftmost_column + visible_columns)

        while len(self.day_items) < visible_columns:
            text_item = day_item()
            self.day_items.append(text_item)
            self.scene.addItem(text_item)

        for i, day_column_pos in enumerate(self.days_range):
            day_text = (self.today - datetime.timedelta(days=day_column_pos)).strftime("%d")
            x_pos = (day_column_pos * self.column_width)
            self.day_items[i].setRect(x_pos*self.zoom_factor, 0, self.column_width*self.zoom_factor, 60)
            self.day_items[i].setDate((self.today - datetime.timedelta(days=day_column_pos)))

        while len(self.day_items) > visible_columns:
            item = self.day_items.pop()
            self.scene.removeItem(item)

    def get_visible_columns(self):
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        leftmost_column = int(visible_rect.left() // self.column_width)
        rightmost_column = int(visible_rect.right() // self.column_width)
        visible_columns = rightmost_column - leftmost_column +1
        return leftmost_column, visible_columns

    def update_rect(self, rect):
        self.setSceneRect(rect.x(), self.sceneRect().y(), rect.width(), self.sceneRect().height())
        self.update_days()

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

        rect = QtCore.QRectF(self.x, self.y, self.width, self.height)
        #painter.drawRect(rect)
        draw_text(painter, rect, self.date.strftime("%d"))


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
        self.pan = False
        self.last_mouse_pos = None
        self.zoom_factor = 1.0

        x, y, width, height = 0, 0, 10, 10  # Adjust the position and size as needed
        red_box_item = RedBoxItem(x, y, width, height)
        self.scene.addItem(red_box_item)    

    def update_scene_rect(self, rect):
        self.setSceneRect(rect)
        self.scene_rect_update.emit(rect)

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
            # Translate the scene to achieve panning
            self.update_scene_rect(self.sceneRect().translated(-delta.x()/self.zoom_factor, -delta.y()/self.zoom_factor))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.pan = False
        else:
            super().mouseReleaseEvent(event)

    def zoom(self, event):
        current_zoom = self.transform().m22()
        # Calculate the zoom factor
        delta = event.angleDelta().y() / 120.0
        zoom_in_factor = 1.1  # Adjust as needed
        zoom_out_factor = 1 / zoom_in_factor
        if delta > 0:
            zoom = zoom_in_factor
        else:
            zoom = zoom_out_factor
        # Limit the zoom factor to a certain range if desired
        min_zoom = 0.2
        max_zoom = 8.0
        new_zoom = current_zoom * zoom
        new_zoom = min(max(new_zoom, min_zoom), max_zoom)
        # Calculate the scaling factor
        scale_factor = new_zoom / current_zoom
        self.scale_factor_update.emit(scale_factor)
        self.zoom_factor_update.emit(new_zoom)
        # Get the mouse position in view coordinates
        mouse_view_pos = event.pos()
        # Map the mouse position to scene coordinates
        mouse_scene_pos = self.mapToScene(mouse_view_pos)
        # Apply the zoom transformation to the view, centered around the mouse position
        self.scale(scale_factor, scale_factor)
        # Calculate the new position of the mouse in scene coordinates
        new_mouse_scene_pos = self.mapToScene(mouse_view_pos)
        # Calculate the difference in position
        diff = new_mouse_scene_pos - mouse_scene_pos
        # Adjust the scene to keep the mouse position fixed
        self.update_scene_rect(QtCore.QRectF(self.sceneRect().x() - diff.x(), self.sceneRect().y() - diff.y(), self.sceneRect().width(), self.sceneRect().height()))
        self.zoom_factor = new_zoom

class header_scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(header_scene, self).__init__()

    def drawBackground(self, painter, rect):
        # Define the alternating background colors
        color1 = QtGui.QColor('transparent')
        color2 = QtGui.QColor(0,0,0,10)
        
        # Define the width of each background column
        column_width = 30  # Adjust as needed

        # Calculate the starting and ending column positions
        start_x = int(rect.left()) // column_width
        end_x = int(rect.right()) // column_width

        # Iterate through the visible area and draw alternating columns
        for x in range(start_x, end_x + 1):
            x_pos = x * column_width
            column_rect = QtCore.QRectF(x_pos, rect.top(), column_width, rect.height())
            color = color1 if x % 2 == 0 else color2
            painter.fillRect(column_rect, color)

class scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(scene, self).__init__()

    def drawBackground(self, painter, rect):
        # Define the alternating background colors
        color1 = QtGui.QColor('transparent')
        color2 = QtGui.QColor(0,0,0,20)
        
        # Define the width of each background column
        column_width = 30  # Adjust as needed

        # Calculate the starting and ending column positions
        start_x = int(rect.left()) // column_width
        end_x = int(rect.right()) // column_width

        # Iterate through the visible area and draw alternating columns
        for x in range(start_x, end_x + 1):
            x_pos = x * column_width
            column_rect = QtCore.QRectF(x_pos, rect.top(), column_width, rect.height())
            color = color1 if x % 2 == 0 else color2
            painter.fillRect(column_rect, color)
        
class RedBoxItem(QtWidgets.QGraphicsItem):
    def __init__(self, x, y, width, height):
        super(RedBoxItem, self).__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        red_color = QtGui.QColor(255, 0, 0, 30)  # Red color
        pen = QtGui.QPen(red_color, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(red_color)

        painter.setPen(pen)
        painter.setBrush(brush)

        painter.drawRect(self.x, self.y, self.width, self.height)

class calendarWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(calendarWidget, self).__init__(parent)

        self.header_view = CalendarHeader()
        self.view = CalendarViewport()

        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.view.scene_rect_update.connect(self.header_view.update_rect)
        self.view.scale_factor_update.connect(self.header_view.update_scale)
        self.view.zoom_factor_update.connect(self.header_view.update_zoom_factor)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
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

app = app_utils.get_app()

w= calendarWidget()
w.show()

app.exec_()