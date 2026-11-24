#!/usr/bin/env sh
# Downloads the open-licensed (OFL) fonts the README art is drawn with.
set -e
cd "$(dirname "$0")"
mkdir -p fonts
for family in ibm-plex-sans-arabic jetbrains-mono inter-tight; do
  rm -rf "fonts/$family"
  tarball=$(npm pack "@expo-google-fonts/$family" --silent --pack-destination fonts)
  mkdir -p "fonts/$family"
  tar xzf "fonts/$tarball" -C "fonts/$family" --strip-components=1
  rm "fonts/$tarball"
done
