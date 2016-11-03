all:
	git clone https://github.com/ilya-fedin/hilink-tray.git
	wine C:/Python27/Scripts/pyinstaller hilink-tray.spec

dbg:
	git clone https://github.com/ilya-fedin/hilink-tray.git
	wine C:/Python27/Scripts/pyinstaller hilink-tray-debug.spec

clean:
	rm -rf hilink-tray build dist
