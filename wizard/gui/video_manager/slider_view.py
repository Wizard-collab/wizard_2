# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import sys
import uuid
import ffmpeg
from PyQt6 import QtWidgets, QtMultimedia, QtMultimediaWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal

class signal_manager(QtCore.QObject):

    on_seek = pyqtSignal(int)
    on_play_pause = pyqtSignal(int)
    on_next_frame = pyqtSignal(int)
    on_prev_frame = pyqtSignal(int)

    def __init__(self, parent=None):
        super(signal_manager, self).__init__(parent)

class timeline_viewport(QtWidgets.QGraphicsView):

    def __init__(self):
        super(timeline_viewport, self).__init__()
        self.setAcceptDrops(True)
        self.setFixedHeight(40)
        self.timeline_scene = timeline_scene()
        self.signal_manager = signal_manager()
        self.setScene(self.timeline_scene)
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing, True)
        self.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.move_cursor = False
        self.frame_width = 2
        self.frame_range = [0,1000]
        self.fps = 24

        empty_item = custom_graphic_item()
        self.timeline_scene.addItem(empty_item)
        self.cursor_item = cursor_item()
        self.timeline_scene.addItem(self.cursor_item)
        self.connect_functions()

    def adapt_frame_width(self):
        self.set_frame_width(max(1,int(self.width()/(self.frame_range[-1]+10))))

    def connect_functions(self):
        self.cursor_item.signal_manager.on_seek.connect(self.signal_manager.on_seek.emit)

    def set_fps(self, fps):
        self.fps = fps
        self.timeline_scene.set_fps(fps)

    def set_frame_range(self, frame_range):
        self.frame_range = frame_range
        self.timeline_scene.set_frame_range(frame_range)
        self.cursor_item.set_frame_range(frame_range)
        self.adapt_frame_width()

    def set_frame_width(self, frame_width=2):
        self.frame_width = frame_width
        self.timeline_scene.set_frame_width(frame_width)
        self.cursor_item.set_frame_width(frame_width)

    def showEvent(self, event):
        self.init_scene()
        self.update()

    def init_scene(self):
        self.move_scene_center_to_left(force = True)
        self.cursor_item.set_frame(0)

    def set_frame(self, frame):
        self.cursor_item.set_frame(frame)
        self.update()

    def move_scene_center_to_left(self, force=False):
        delta_x = self.mapToScene(QtCore.QPoint(0,0)).x() + 20
        #if (delta_x >= 0) and not force:
        #    return
        self.update_scene_rect(self.sceneRect().translated(-delta_x, 0))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adapt_frame_width()
        self.move_scene_center_to_left()

    def update_scene_rect(self, rect):
        self.setSceneRect(rect)
        self.update()

    def mousePressEvent(self, event):
        self.move_cursor = None
        super().mousePressEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.timeline_scene.is_in_cursor_zone(self.mapToScene(event.pos())):
                self.cursor_item.move_item(self.mapToScene(event.pos()).x())
                self.move_cursor = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.move_cursor = None

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.move_cursor:
            self.cursor_item.move_item(self.mapToScene(event.pos()).x())

class timeline_scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(timeline_scene, self).__init__()
        self.frame_width = 2
        self.fps = 24
        self.frame_range = [0,1000]
        self.cache_scene_painting()

    def cache_scene_painting(self):
        self.color1 = QtGui.QColor(0,0,10,60)
        self.color2 = QtGui.QColor(245,245,255,10)

    def set_frame_width(self, frame_width):
        self.frame_width = frame_width
        self.update()

    def set_fps(self, fps=24):
        self.fps = fps

    def set_frame_range(self, frame_range):
        self.frame_range = frame_range
        self.update()

    def is_in_cursor_zone(self, pos):
        cursor_zone_rect = QtCore.QRectF(self.sceneRect().left(),10,self.sceneRect().width(),20)
        return cursor_zone_rect.contains(pos)

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, self.color1)

        time_rect = QtCore.QRectF(rect.left(),10,rect.width(),20)
        painter.fillRect(time_rect, QtGui.QColor(0,0,10,10))

        frame_range_rect = QtCore.QRectF(self.frame_range[0]*self.frame_width,10,(self.frame_range[1]-self.frame_range[0]+1)*self.frame_width,20)
        painter.fillRect(frame_range_rect, QtGui.QColor(245,245,255,10))

        in_rect = QtCore.QRectF((self.frame_range[0]*self.frame_width),10,1,20)
        painter.fillRect(in_rect, QtGui.QColor(100,100,110,150))

        out_rect = QtCore.QRectF((self.frame_range[1]+1)*self.frame_width,10,1,20)
        painter.fillRect(out_rect, QtGui.QColor(100,100,110,150))

        start_x = 0
        end_x = int(rect.right() // self.frame_width)

        # Adjust frames display
        step = int(self.fps)
        if self.frame_width >= 4:
            step = int(self.fps/2)
        if self.frame_width >= 10:
            step = int(self.fps/4)
        if self.frame_width >= 15:
            step = int(self.fps/6)
        if self.frame_width >= 20:
            step = 1
        if self.frame_width <= 1:
            step = self.fps*2
        if self.frame_width <= 0.5:
            step = self.fps*6
        if self.frame_width <= 0.2:
            step = self.fps*8
        if self.frame_width <= 0.15:
            step = self.fps*12
        if self.frame_width <= 0.1:
            step = self.fps*18
        
        for x in range(start_x, end_x + 1, step):
            x_pos = int(x * self.frame_width)
            rect = QtCore.QRectF(x_pos-25+int(self.frame_width/2), 10, 50, 20)
            pen = QtGui.QPen(QtGui.QColor(255,255,255,int(255*0.2)), 1, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignHCenter, str(x))
            pen = QtGui.QPen(QtGui.QColor(255,255,255,int(255*0.05)), 1, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawLine(x_pos, 30, x_pos, 80)

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
        pen = QtGui.QPen(QtGui.QColor('transparent'), 1, QtCore.Qt.PenStyle.SolidLine)
        brush = QtGui.QBrush(color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.x, self.y, self.width, self.height)

class cursor_item(custom_graphic_item):
    def __init__(self):
        super(cursor_item, self).__init__()
        self.signal_manager = signal_manager()
        self.height = 70
        self.width = 40
        self.frame_width = 2
        self.frame = 0
        self.start_move_pos = None
        self.frame_range = [0,1000]
        self.setZValue(1000)
        self.setPos(self.pos().x(), 10)

    def set_frame(self, frame):
        self.frame = int(frame)
        self.update_pos()
        self.update()

    def set_frame_range(self, frame_range):
        self.frame_range = frame_range

    def update_pos(self):
        self.setPos((self.frame*self.frame_width)- int(self.width/2) + int(self.frame_width/2), self.pos().y())

    def update_frame(self):
        self.frame = int((self.pos().x() + self.width/2 - int(self.frame_width/2))/self.frame_width)
        self.update()

    def set_frame_width(self, frame_width):
        self.frame_width = frame_width
        self.update_pos()

    def get_pos(self):
        return int(self.pos().x() + self.width/2 + int(self.frame_width/2))

    def get_frame_from_pos(self, pos_x):
        return int(pos_x/self.frame_width)

    def move_item(self, pos_x):
        frame = self.get_frame_from_pos(pos_x)
        if frame > (self.frame_range[1]):
            self.set_frame(self.frame_range[1])
        elif frame < self.frame_range[0]:
            self.set_frame(self.frame_range[0])
        else:
            self.set_frame(frame)
            self.update_frame()
        self.signal_manager.on_seek.emit(self.frame)

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(QtGui.QColor(255,100,100,200), max(self.frame_width, 2), QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.x+int(self.width/2), 20, self.x+int(self.width/2), self.height)
        frame_rect = QtCore.QRectF(self.x, 0, self.width, 20)
        pen = QtGui.QPen(QtGui.QColor(255,255,255,0), 1, QtCore.Qt.PenStyle.SolidLine)
        brush = QtGui.QBrush(QtGui.QColor(255,100,100,255))
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawRoundedRect(frame_rect, 4, 4)
        pen = QtGui.QPen(QtGui.QColor(255,255,255,int(255*0.85)), 1, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        font = QtGui.QFont()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(frame_rect, QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignHCenter, str(self.frame))
