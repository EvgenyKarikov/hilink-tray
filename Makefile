all:
	head -n \-3 hilink-tray.py | grep -v 'import res_rc' | grep -v 'import res3_rc' > hilink-tray
	pyside-rcc res.qrc >> hilink-tray
	tail -n 4 hilink-tray.py >> hilink-tray
windows:
	wine C:/Python27/Scripts/pyinstaller -w hilink-tray
install:
	install hilink-tray /usr/bin/hilink-tray
uninstall:
	rm -rf /usr/bin/hilink-tray
