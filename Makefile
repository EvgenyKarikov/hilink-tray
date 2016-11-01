res:
	pyside-rcc -o hilink/res_rc.py res.qrc
	pyside-rcc -o hilink/res3_rc.py res.qrc -py3

clean:
	rm -rf hilink/*.pyc

windows:
	wine C:/Python27/Scripts/pyinstaller -w hilink-tray.py
	mkdir -p dist/hilink-tray/phonon_backend
	cp -rf ~/.wine/drive_c/Python27/Lib/site-packages/PySide/plugins/phonon_backend/phonon_ds94.dll dist/hilink-tray/phonon_backend

windows-dbg:
	wine C:/Python27/Scripts/pyinstaller hilink-tray.py
	mkdir -p dist/hilink-tray/phonon_backend
	cp -rf ~/.wine/drive_c/Python27/Lib/site-packages/PySide/plugins/phonon_backend/phonon_ds94.dll dist/hilink-tray/phonon_backend

install:
	install -D hilink /usr/lib/python2.7/dist-packages/
	install -D hilink-tray.py /usr/bin/hilink-tray

uninstall:
	rm -rf /usr/bin/hilink-tray /usr/lib/python2.7/dist-packages/hilink

windows-clean:
	rm -rf build *.spec
