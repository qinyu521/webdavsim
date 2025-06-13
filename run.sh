#!/bin/bash

prog="$0"
while [ -h "${prog}" ]; do
	newProg=`/bin/ls -ld "${prog}"`

	newProg=`expr "${newProg}" : ".* -> \(.*\)$"`
	if expr "x${newProg}" : 'x/' >/dev/null; then
		prog="${newProg}"
	else
		progdir=`dirname "${prog}"`
		prog="${progdir}/${newProg}"
	fi
done
progdir=`dirname "${prog}"`
cd "${progdir}"

rm -rf tmp
mkdir tmp
chmod 777 tmp
export TMPDIR=tmp
unset LD_PRELOAD
machine=$(uname -m)
if [[ "$machine" == *"arm"* || "$machine" == *"aarch"* ]]; then
    arch="arm64"
else
    arch="amd64"
fi
echo "arch:$arch"
./webdav_simulator.$arch --alist_config alistservers.txt "xy115-all.txt.xz#xy-dy.txt.xz#xy-dsj.txt.xz#xy115-music.txt.xz"
