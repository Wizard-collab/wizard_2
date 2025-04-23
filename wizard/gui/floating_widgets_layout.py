# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal

# Wizard core modules
from wizard.core import user


def save_widget_pos(widget, widget_name):
    pos_dic = dict()
    pos_dic['coord'] = [widget.x(), widget.y(), widget.width(),
                        widget.height()]
    pos_dic['visibility'] = widget.isVisible()
    pos_dic['is_maximized'] = widget.isMaximized()
    user.user().set_widget_pos(widget_name, pos_dic)


def init_widget_pos(widget, widget_name, force_show=0, maximized=0):
    pos_dic = user.user().get_widget_pos(widget_name)
    if pos_dic:
        widget.move(pos_dic['coord'][0], pos_dic['coord'][1])
        widget.resize(pos_dic['coord'][2], pos_dic['coord'][3])
        if pos_dic['visibility'] or force_show:
            if pos_dic['is_maximized']:
                widget.showMaximized()
            else:
                widget.show()
    else:
        if force_show:
            if maximized:
                widget.showMaximized()
            else:
                widget.show()
