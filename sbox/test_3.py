import os
print(os.path.abspath(""))
import PyWizard
from wizard.core import assets
from wizard.gui import gui_server
assets.create_asset("Lola", 1, 100, 220)
gui_server.refresh_ui()

