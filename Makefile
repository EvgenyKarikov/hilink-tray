all:
	git clone https://github.com/ilya-fedin/hilink-tray.git
	wine C:/Python27/Scripts/pyinstaller hilink-tray.spec
	wine "C:/Program Files (x86)/Inno Setup 5/ISCC" hilink-tray.iss

prt:
	git clone https://github.com/ilya-fedin/hilink-tray.git
	wine C:/Python27/Scripts/pyinstaller hilink-tray-portable.spec

dbg:
	git clone https://github.com/ilya-fedin/hilink-tray.git
	wine C:/Python27/Scripts/pyinstaller hilink-tray-debug.spec

clean:
	rm -rf hilink-tray build dist
