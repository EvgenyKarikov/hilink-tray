deb:
	mkdir -p hilink-tray-4.0/usr/lib/python2.7/dist-packages hilink-tray-4.0/usr/bin
	cp -rf hilink hilink-tray-4.0/usr/lib/python2.7/dist-packages
	cp -rf hilink-tray.py hilink-tray-4.0/usr/bin/hilink-tray
	dpkg --build hilink-tray-4.0 Release/hilink-tray-4.0_all.deb

windows:
	wine C:/Python27/Scripts/pyinstaller -w hilink-tray.py

windows-dbg:
	wine C:/Python27/Scripts/pyinstaller hilink-tray.py

install:
	install -D hilink /usr/lib/python2.7/dist-packages/
	install -D hilink-tray.py /usr/bin/hilink-tray

uninstall:
	rm -rf /usr/bin/hilink-tray /usr/lib/python2.7/dist-packages/hilink

deb-clean:
	rm -rf hilink-tray-4.0/usr

pacman-clean:
	rm -rf hilink-tray pkg src

windows-clean:
	rm -rf build *.spec
