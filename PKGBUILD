# Maintainer: Samuel Roux <sam@gatewaycorporate.org>

pkgname=runixinstall-git
pkgver=0.0.3
pkgrel=1
pkgdesc="A modified runixinstall built for Runix"
arch=(any)
url="https://github.com/Gateway-Corporate-Solutions/runixinstall"
license=(GPL-3.0-only)
depends=(
  'arch-install-scripts'
  'btrfs-progs'
  'coreutils'
  'cryptsetup'
  'dosfstools'
  'e2fsprogs'
  'glibc'
  'kbd'
  'libcrypt.so'
  'libxcrypt'
  'pciutils'
  'procps-ng'
  'python'
  'python-cryptography'
  'python-pydantic'
  'python-pyparted'
  'python-textual'
  'systemd'
  'util-linux'
  'xfsprogs'
  'lvm2'
  'f2fs-tools'
  'ntfs-3g'
)
makedepends=(
  'python-build'
  'python-installer'
  'python-setuptools'
  'python-sphinx'
  'python-wheel'
  'python-sphinx_rtd_theme'
  'python-pylint'
  'ruff'
)
optdepends=(
  'python-systemd: Adds journald logging'
)
provides=(runixinstall-git)
source=(runixinstall-git::git+https://github.com/Gateway-Corporate-Solutions/runixinstall.git)
md5sums=('SKIP')

build() {
  cd runixinstall-git

  python -m build --wheel --no-isolation
  PYTHONDONTWRITEBYTECODE=1 make man -C docs
}

package() {
  cd runixinstall-git
  
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -vDm 644 docs/_build/man/runixinstall.1 -t "$pkgdir/usr/share/man/man1/"
}
