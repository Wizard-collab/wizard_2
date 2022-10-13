from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


class customLabel(QtWidgets.QWidget):
    def __init__(self, text='', parent=None):
        super(customLabel, self).__init__(parent)
        #self.setStyleSheet('background-color:red;')
        self.text = text

    def setText(self, text):
        self.text = text
        self.calculate_size()

    def resizeEvent(self, event):
        self.calculate_size()

    def calculate_size(self):
        pos = [0, 0]
        font = QtGui.QFont("Roboto", 8)
        font_metric = QtGui.QFontMetrics(font)
        font_height = font_metric.height()
        pos[1] += font_height
        space_width = font_metric.width(' ')

        start=1
        for line in self.text.split('\n'):
            if not start:
                pos[1] += font_height + 3
                pos[0] = 0
            start=0
            for word in line.split(' '):
                item_width = font_metric.width(word)
                if item_width >= self.width():
                    for letter in word:
                        item_width = font_metric.width(letter)
                        pos = self.get_pos(letter, pos, item_width, font_height)
                else:
                    pos = self.get_pos(word, pos, item_width, font_height)
                    pos = self.get_pos(' ', pos, space_width, font_height)
        self.setMinimumHeight(pos[1]+3+3)

    def get_pos(self, item, pos, item_width, font_height):
        if item != ' ':
            if pos[0]+item_width >= self.width():
                pos[1] += font_height + 3
                pos[0] = 0
        if item.startswith('@'):
            pos[0] += 8 + 4
        pos[0] += item_width 
        return pos

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor('#d7d7d7'), 0))
        painter.setBrush(QtGui.QBrush(QtGui.QColor('#ffffff')))
        pos = [0, 0]

        font = QtGui.QFont("Roboto", 8)
        font_metric = QtGui.QFontMetrics(font)
        font_height = font_metric.height()
        pos[1] += font_height
        space_width = font_metric.width(' ')
        painter.setFont(font)

        start=1
        for line in self.text.split('\n'):
            if not start:
                pos[1] += font_height + 3
                pos[0] = 0
            start=0
            for word in line.split(' '):
                item_width = font_metric.width(word)
                if item_width >= self.width():
                    for letter in word:
                        item_width = font_metric.width(letter)
                        pos = self.draw_item(letter, pos, item_width, painter, font_height, font_metric)
                else:
                    pos = self.draw_item(word, pos, item_width, painter, font_height, font_metric)
                    pos = self.draw_item(' ', pos, space_width, painter, font_height, font_metric)
                    
    def draw_item(self, item, pos, item_width, painter, font_height, font_metric):
        if item != ' ':
            if pos[0]+item_width >= self.width():
                pos[1] += font_height + 3
                pos[0] = 0
        if item.startswith('@'):
            pos[0] += 2
            painter.setBrush(QtGui.QBrush(QtGui.QColor(119, 133, 222, 255)))
            pen = QtGui.QPen()
            pen.setBrush(QtGui.QColor('transparent'))
            pen.setCapStyle(QtCore.Qt.RoundCap)
            pen.setJoinStyle(QtCore.Qt.RoundJoin)
            pen.setWidth(0)
            painter.setPen(pen)

            bouding_rect = font_metric.boundingRect(item)
            rect = QtCore.QRect((pos[0]+bouding_rect.x()),
                                    (pos[1]+bouding_rect.y())-3,
                                    (bouding_rect.width())+8,
                                    (bouding_rect.height())+6)
            painter.drawRoundedRect(rect, 3, 3)
            painter.setPen(QtGui.QPen(QtGui.QColor('white'), 0))
            pos[0] += 4
        painter.drawText(pos[0], pos[1], item)
        if item.startswith('@'):
            pos[0] += 4 + 2
        pos[0] += item_width 
        return pos

'''
w=QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
w.setLayout(layout)
text = customLabel("@all vous pouvez check ca ? et aussi, @j.dupont pense a retake l'oeil")
layout.addWidget(text)
w.show()
w.resize(400,200)
'''
