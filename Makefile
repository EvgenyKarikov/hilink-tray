all: install
install:
	cp hilink-tray.py /usr/bin/hilink-tray
	chmod 755 hilink-tray.py /usr/bin/hilink-tray
	mkdir /usr/share/pixmaps/hilink-tray
	cp -R icons /usr/share/pixmaps/hilink-tray
	mkdir /var/log/hilink-tray
	touch /var/log/hilink-tray/err.log
	chmod 666 /var/log/hilink-tray/err.log
uninstall:
	rm /usr/bin/hilink-tray
	rm -R /usr/share/pixmaps/hilink-tray
	rm -R /var/log/hilink-tray