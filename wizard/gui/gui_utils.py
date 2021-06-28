# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

def move_ui(widget):
    desktop = QtWidgets.QApplication.desktop()
    screenRect = desktop.screenGeometry()

    screen_minX = screenRect.topLeft().x()
    screen_minY = screenRect.topLeft().y()
    screen_maxX = screenRect.bottomRight().x()
    screen_maxY = screenRect.bottomRight().y()
    cursor_x = QtGui.QCursor.pos().x()
    cursor_y = QtGui.QCursor.pos().y()
    win_width = widget.frameSize().width()
    win_heigth = widget.frameSize().height()

    if (cursor_y - 20 - win_heigth) <= screen_minY:
        posy = cursor_y - 10
        angley = 'top'
    else:
        posy = cursor_y - win_heigth + 10
        angley = 'bottom'
    if (cursor_x + 20 + win_width) >= screen_maxX:
        posx = cursor_x - win_width + 10
        anglex = 'right'
    else:
        posx = cursor_x - 10
        anglex = 'left'

    widget.move(posx, posy)
    return f"{angley}-{anglex}"