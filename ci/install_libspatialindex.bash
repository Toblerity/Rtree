#!/bin/bash
set -xe

# A simple script to install libspatialindex from a Github Release
VERSION=1.9.3
SHA256=63a03bfb26aa65cf0159f925f6c3491b6ef79bc0e3db5a631d96772d6541187e


rm $VERSION.zip || true
curl -L -O https://github.com/libspatialindex/libspatialindex/archive/$VERSION.zip

# check the file hash
echo "${SHA256}  ${VERSION}.zip" | sha256sum --check

rm -rf "libspatialindex-${VERSION}" || true
unzip $VERSION
cd libspatialindex-${VERSION}

mkdir build
cd build

cmake ..
make -j 4

# copy built libraries
cp bin/* ../../../rtree/

cd ../..
rm -rf "libspatialindex-${VERSION}"
