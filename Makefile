deb:
	cp -r hilink hilink-tray-4.0/usr/lib/python2.7/dist-packages
	cp hilink-tray.py hilink-tray-4.0/usr/bin/hilink-tray
	dpkg --build hilink-tray-4.0 hilink-tray-4.0_all.deb

windows:
	wine C:/Python27/Scripts/pyinstaller -w hilink-tray
install:
	install hilink-tray /usr/bin/hilink-tray
uninstall:
	rm -rf /usr/bin/hilink-tray

clean:
	rm hilink-tray-4.0_all.deb
