![alt text](http://54.39.96.76/documentation/_images/wizard_icon_256.png)

# Wizard

Wizard is an autonomous software for managing CGI productions.

🌏 Official windows installer here : http://54.39.96.76/

⚠️ For now it only works on Windows OS.

* Use this repository:
	* Install PostgreSQL on your computer or any server
	* This repository :
		* Clone the repository
		* Install `python 3.12.#`
		* Download FFmpeg (https://ffmpeg.org/download.html) and move `ffmpeg.exe` inside the repository/binaries
		* Get mpv binaries here : https://sourceforge.net/projects/mpv-player-windows/files/libmpv/ and move `libmpv-2.dll` inside the repository/binaries
		* Launch `pip install -r requirement.txt`
		* Launch `app.bat` or `python app.py`

* Developed with _python 3.12.#_

* Modules dependencies:
	* PyQt6
	* PyYaml
	* pillow
	* pyautogui
	* psycopg2
	* psutil
	* QScintilla
	* requests
	* clipboard
	* opencv-python
	* pywin32
	* PyInstaller
	* winshell
	* rotate-screen
	* mpv

* Other dependecies
	* ffmpeg.exe
	* libmpv-2.dll

* Database dependency:
	* PostgreSQL
