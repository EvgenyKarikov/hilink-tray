all:
	wget https://raw.githubusercontent.com/AppImage/AppImages/master/pkg2appimage
	chmod a+x pkg2appimage
	./pkg2appimage --no-di hilink-tray.yml

clean:
	rm -rf hilink-tray out pkg2appimage
