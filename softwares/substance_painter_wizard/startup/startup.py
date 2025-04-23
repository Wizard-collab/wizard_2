# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
from substance_painter_wizard import wizard_plugin

# Substance painter modules
import substance_painter
import substance_painter.logging as logging

plugin_widgets = []

WIZARD_TOOLBAR = None


def start_plugin():
    global WIZARD_TOOLBAR
    WIZARD_TOOLBAR = wizard_plugin.tool_bar()
    substance_painter.event.DISPATCHER.connect(
        event_cls=substance_painter.event.ProjectSaved, callback=wizard_plugin.copy_save)


def close_plugin():
    global WIZARD_TOOLBAR
    del WIZARD_TOOLBAR


if __name__ == "__main__":
    start_plugin()
