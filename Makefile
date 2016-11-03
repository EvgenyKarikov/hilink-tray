res:
	pyside-rcc -o hilink/res_rc.py res.qrc
	pyside-rcc -o hilink/res3_rc.py res.qrc -py3

clean:
	rm -rf hilink/*.pyc

install:
	install -D hilink /usr/lib/python2.7/dist-packages/
	install -D hilink-tray.py /usr/bin/hilink-tray

uninstall:
	rm -rf /usr/bin/hilink-tray /usr/lib/python2.7/dist-packages/hilink
