# Maintainer: Samuel Roux <sam@gatewaycorporate.org>

pkgname=runixinstall
pkgver=0.0.1
pkgrel=1
pkgdesc="A modified archinstall built for Runix"
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
provides=(python-archinstall archinstall)
conflicts=(python-archinstall archinstall-git)
replaces=(python-archinstall archinstall-git)
source=(runixinstall::git://github.com/Gateway-Corporate-Solutions/runixinstall.git)
sha512sums=()
b2sums=()

check() {
  cd runixinstall
  ruff check
}

pkgver() {
  cd runixinstall

  awk '$1 ~ /^__version__/ {gsub("\"", ""); print $3}' archinstall/__init__.py
}

build() {
  cd runixinstall

  python -m build --wheel --no-isolation
  PYTHONDONTWRITEBYTECODE=1 make man -C docs
}

package() {
  cd runixinstall

  python -m installer --destdir="$pkgdir" dist/*.whl
  install -vDm 644 docs/_build/man/archinstall.1 -t "$pkgdir/usr/share/man/man1/"
}
