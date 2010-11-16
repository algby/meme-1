#!/bin/bash

# Meme: a fast mind-mapping tool
# (c) 2010 Jamie Webb - MIT license

shopt -s nullglob

PREFIX=${PREFIX:-/usr/local}

function run() {
	echo "$@"
	"$@" || exit 1
}

function usage() {
	echo "Usage: ./make.sh <action>"
	echo
	echo "  compile     Compiles python bytecode (optional)"
	echo "  install     Installs to \$PREFIX, default /usr/local"
	echo "  clean       Cleans the source tree"
	echo "  package     Builds a distribution tarball"
	exit 1
}

function do_compile() {
	cd src
	run python -m compileall meme
	run python -O -m compileall meme
}

function do_install() {
	cd src
	run install -D -m 755 meme.py "$PREFIX/share/meme/meme.py"
	for x in meme/*.py{,c,o}; do
		run install -D -m 644 "$x" "$PREFIX/share/meme/$x"
	done
	run ln -sf "$PREFIX/share/meme/meme.py" "$PREFIX/bin/meme"
	cd ..
	run install -D -m 644 ui/meme.xml "$PREFIX/share/meme/ui/meme.xml"
}

function do_clean() {
	for x in src/meme/*.py[co] meme-*.tar.gz; do
		run rm -f "$x"
	done
}

function do_package() {
	if [ -z "$1" ]; then
		echo "Usage: ./make.sh package <version>"
		echo 1
	fi
	run git archive -o "meme-$1.tar" --prefix="meme-$1/" HEAD
	gzip -f "meme-$1.tar"
}

case "$1" in
	compile)
		do_compile
		;;
	install)
		do_install
		;;
	clean)
		do_clean
		;;
	package)
		do_package "$2"
		;;
	*)
		usage
		;;
esac

# vim:sw=4 ts=4
