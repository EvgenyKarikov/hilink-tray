# Maintainer: Ilya Fedin <fedin-ilja2010@ya.ru>
pkgname=hilink-tray
pkgver=4.1
pkgrel=1
pkgdesc="Displays signal level in a tray at Huawei modems on HiLink firmware"
arch=('any')
url="https://github.com/ilya-fedin/hilink-tray.git"
license=('MIT')
depends=('python2>=2.7' 'python2-pyside')
source=("git://github.com/ilya-fedin/hilink-tray.git")
md5sums=('SKIP')

package() {
  cd "$pkgname"
  mkdir -p "${pkgdir}"/usr/lib/python2.7 "${pkgdir}"/usr/bin "${pkgdir}"/usr/share/licenses/hilink-tray
  cp -R hilink "${pkgdir}"/usr/lib/python2.7
  cp hilink-tray.py "${pkgdir}"/usr/bin/hilink-tray
  cp LICENSE "${pkgdir}"/usr/share/licenses/hilink-tray
}
