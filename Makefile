all:
	head -n \-3 hilink-tray.py > hilink-tray
	pyside-rcc res.qrc >> hilink-tray
	tail -n 4 hilink-tray.py >> hilink-tray
install:
	install hilink-tray /usr/bin/hilink-tray
uninstall:
	rm -R /usr/bin/hilink-tray
