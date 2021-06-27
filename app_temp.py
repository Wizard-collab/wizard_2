import PyWizard
from wizard.gui import tree_widget
from wizard.gui import user_widget
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

app = QtWidgets.QApplication(sys.argv)
with open('wizard/gui/stylesheet.css', 'r') as f:
	app.setStyleSheet(f.read())
my_tree_widget = tree_widget.tree_widget()
my_user_widget = user_widget.user_widget()
my_tree_widget.show()
#my_user_widget.show()
sys.exit(app.exec_())