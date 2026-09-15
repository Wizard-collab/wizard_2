# coding: utf-8
"""Silent launcher: runs Wizard.bat without popping a console window."""

import os
import subprocess

BAT_PATH = r"P:\WIZARD\Wizard.bat"

if __name__ == '__main__':
    subprocess.Popen(
        ['cmd.exe', '/c', BAT_PATH],
        cwd=os.path.dirname(BAT_PATH),
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
