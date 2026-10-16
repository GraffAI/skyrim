#!/usr/bin/env bash
# Pinned build of serde-hkx's CLI `hkxc` (HKX <-> Havok packfile XML/JSON, hk_2010.2.0-r1)
# for macOS arm64, from source, in an ephemeral Nix shell. Nothing is installed globally.
#
#   build_serde_hkx.sh            clone + build -> $SRC/target/release/hkxc
#   build_serde_hkx.sh --release  instead download the upstream macOS arm64 release binary
#                                 (sha256-checked) -> $DEST/serde-hkx-release/hkxc
#
# Measured 2026-10-15 on aubron-roam (M1 Max): cold build 2m51s with nixpkgs rustc 1.98.1
# (crate needs rust-version >= 1.95, edition 2024).
set -euo pipefail
TAG=2.0.0
COMMIT=2b684a347375adc82be733e3d85077adbcec873a      # `git rev-parse 2.0.0^{commit}`
REL_ASSET=serde-hkx-cli-aarch64-apple-darwin-extra_fmt.tar.gz
REL_SHA256=a4a3bfde0ec2ae91bd93ee173f56cfc8ce04dcd2db211699730c08df777837c6
DEST=${DEST:-$HOME/skyrim-data-extracted/_toolsrc}
SRC=$DEST/serde-hkx
# the nixpkgs the measured build used (`nix flake metadata nixpkgs`); override to float
NIXPKGS=${NIXPKGS:-github:NixOS/nixpkgs/494ce7fd23ff6a5dff39e1fb11e9b6f2ac74bf25}
mkdir -p "$DEST"

if [[ ${1:-} == --release ]]; then
  d=$DEST/serde-hkx-release; mkdir -p "$d"
  curl -fsSL -o "$d/$REL_ASSET" "https://github.com/SARDONYX-sard/serde-hkx/releases/download/$TAG/$REL_ASSET"
  echo "$REL_SHA256  $d/$REL_ASSET" | shasum -a 256 -c -
  tar -xzf "$d/$REL_ASSET" -C "$d"
  "$d/hkxc" --version
  exit 0
fi

[[ -d $SRC/.git ]] || git clone https://github.com/SARDONYX-sard/serde-hkx "$SRC"
git -C "$SRC" fetch --tags --quiet
git -C "$SRC" checkout --quiet "$COMMIT"
[[ $(git -C "$SRC" rev-parse HEAD) == "$COMMIT" ]]
# extra_fmt adds json/yaml/toml output (the upstream release is built with it too)
(cd "$SRC" && nix shell "$NIXPKGS#cargo" "$NIXPKGS#rustc" -c cargo build --release --locked -p hkxc --features extra_fmt)
"$SRC/target/release/hkxc" --version
