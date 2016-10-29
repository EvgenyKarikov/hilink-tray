_pkgbase=hilink-tray
pkgname=hilink-tray-git
pkgver=4.0
pkgrel=0
pkgdesc="Displays signal level in a tray at Huawei modems on HiLink firmware"
arch=('any')
url="https://github.com/ilya-fedin/hilink-tray.git"
license=('MIT')
depends=('python2>=2.7' 'python2-pyside')
source=("git://github.com/ilya-fedin/hilink-tray.git")
md5sums=('SKIP')

package() {
  cd "$_pkgbase"
  
  mkdir -p "${pkgdir}"/usr/lib/python2.7/dist-packages "${pkgdir}"/usr/bin
  
  cp -rf hilink "${pkgdir}"/usr/lib/python2.7/dist-packages
  cp -rf hilink-tray.py "${pkgdir}"/usr/bin/hilink-tray
}
