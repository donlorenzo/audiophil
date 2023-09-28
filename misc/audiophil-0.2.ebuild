# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI="2"
NEED_PYTHON=2.5

inherit distutils

DESCRIPTION="AudioPhil is a audio player written in python using PyQt4. It features tabbed playlists and a sql-based media library."
HOMEPAGE="http://sourceforge.net/projects/audiophil"
SRC_URI="http://downloads.sourceforge.net/audiophil/${P}.tar.gz"

LICENSE="BSD"
SLOT="0"
KEYWORDS="~x86 ~amd64"
IUSE=""

DEPEND="x11-libs/qt-core[glib]
	x11-libs/qt-gui[glib]
	x11-libs/qt-sql[sqlite]
	>=dev-python/PyQt4-4.4.2[phonon,sql,svg]
	media-libs/mutagen"

MY_P="AudioPhil-"${PV}
S="${WORKDIR}"/${MY_P}

