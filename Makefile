all:
	git clone --depth 1 https://github.com/ilya-fedin/hilink-tray.git
	mkdir -p hilink-tray-4.1.1/usr/lib/python2.7/dist-packages hilink-tray-4.1.1/usr/bin
	cp -rf hilink-tray/hilink hilink-tray-4.1.1/usr/lib/python2.7/dist-packages
	cp -f hilink-tray/hilink-tray.py hilink-tray-4.1.1/usr/bin/hilink-tray
	dpkg --build hilink-tray-4.1.1 hilink-tray-4.1.1_all.deb

clean:
	rm -rf hilink-tray hilink-tray-4.1.1_all.deb
