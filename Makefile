all: install
install:
	pip install pyside
	mkdir /opt/hilink-tray/
	cp hilink-tray.py /opt/hilink-tray/
	cp res_rc.py /opt/hilink-tray/
	chmod 755 /opt/hilink-tray
	ln -s /opt/hilink-tray/hilink-tray.py /usr/bin/hilink-tray
uninstall:
	rm -R /opt/hilink-tray
