all:
	mkdir -p hilink-tray-4.0/usr/lib/python2.7/dist-packages hilink-tray-4.0/usr/bin
	cp -rf hilink hilink-tray-4.0/usr/lib/python2.7/dist-packages
	cp -f hilink-tray.py hilink-tray-4.0/usr/bin/hilink-tray
	dpkg --build hilink-tray-4.0 hilink-tray-4.0_all.deb

clean:
	rm hilink-tray-4.0_all.deb
