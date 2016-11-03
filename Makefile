all:
	wine C:/Python27/Scripts/pyinstaller hilink-tray.spec

dbg:
	wine C:/Python27/Scripts/pyinstaller hilink-tray-debug.spec

clean:
	rm -rf build dist
