import os, winshell
from win32com.client import Dispatch

desktop = winshell.desktop()
path = os.path.join(desktop, "Wizard.lnk")
target = r"C:\program files\Wizard\Wizard.exe"
wDir = r"C:\program files\Wizard"
icon = r"C:\program files\Wizard\Wizard.exe"
shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(path)
shortcut.Targetpath = target
shortcut.WorkingDirectory = wDir
shortcut.IconLocation = icon
shortcut.save()