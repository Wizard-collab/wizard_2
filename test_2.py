from wizard.core import assets
from wizard.gui import gui_server
import random

for a in range(0,10):
	assets.create_asset(str(a)+str(random.randint(0,1000))+'zekfja', 1)
gui_server.refresh_ui()