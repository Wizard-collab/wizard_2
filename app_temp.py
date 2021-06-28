import PyWizard
from wizard.gui import tree_widget
from wizard.gui import user_widget
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

app = QtWidgets.QApplication(sys.argv)

QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Black.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-BlackItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Bold.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-BoldItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Light.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-LightItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Medium.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-MediumItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Regular.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Thin.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-ThinItalic.ttf")

QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Black.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-BlackItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Bold.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-BoldItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ExtraBold.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ExtraBoldItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ExtraLight.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ExtraLightItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Medium.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-MediumItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Regular.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-SemiBold.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-SemiBoldItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Thin.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ThinItalic.ttf")

QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Rubik-Italic-VariableFont_wght.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Rubik-VariableFont_wght.ttf")

QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Cabin-Italic-VariableFont_wdth,wght.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Cabin-VariableFont_wdth,wght.ttf")

with open('wizard/gui/stylesheet.css', 'r') as f:
	app.setStyleSheet(f.read())
my_tree_widget = tree_widget.tree_widget()
my_user_widget = user_widget.user_widget()
my_tree_widget.show()
#my_user_widget.show()
sys.exit(app.exec_())