#!/usr/bin/env bash
# Round-trip check: for every RAW/<rel>.hkx with a TEXT/<rel>.<ext>, convert the text back to
# 64-bit hkx and byte-compare with the original.
#
#   roundtrip_check.sh xml  [RAW] [TEXT] [WORK]   TEXT defaults to ~/skyrim-data-extracted/xml
#   roundtrip_check.sh json [RAW] [TEXT] [WORK]   (json: TEXT is generated first into WORK)
#
# Prints one line per file: IDENTICAL | DIFF <nbytes> | FAIL, then counts. WORK defaults to
# ~/skyrim-data-extracted/hkx-test/roundtrip-<fmt>. Never writes inside RAW or TEXT.
set -euo pipefail
fmt=${1:?xml|json}
RAW=${2:-$HOME/skyrim-data-extracted/raw}
TEXT=${3:-$HOME/skyrim-data-extracted/xml}
WORK=${4:-$HOME/skyrim-data-extracted/hkx-test/roundtrip-$fmt}
HKXC=${HKXC:-$HOME/skyrim-data-extracted/_toolsrc/serde-hkx/target/release/hkxc}
JOBS=${JOBS:-$(sysctl -n hw.ncpu 2>/dev/null || echo 8)}
mkdir -p "$WORK"
export RAW TEXT WORK HKXC fmt
rt() {
  rel=$1; src="$RAW/$rel"; key=$(printf '%s' "$rel" | tr '/ ' '__'); key=${key%.*}
  if [[ $fmt == json ]]; then txt="$WORK/$key.json"; "$HKXC" convert -i "$src" -o "$txt" -v json >/dev/null 2>&1 || true
  else txt="$TEXT/${rel%.*}.xml"; fi
  back="$WORK/$key.rt.hkx"
  "$HKXC" convert -i "$txt" -o "$back" -v amd64 >/dev/null 2>&1 || true
  if [[ ! -s $back ]]; then echo "FAIL	$rel"
  elif cmp -s "$src" "$back"; then echo "IDENTICAL	$rel"
  else echo "DIFF $(cmp -l "$src" "$back" 2>/dev/null | wc -l | tr -d ' ')	$rel"; fi
  rm -f "$back"
}
export -f rt
cd "$RAW"
if [[ $fmt == json ]]; then find . -type f -iname '*.hkx' | grep -vi '/animations/'
else (cd "$TEXT" && find . -type f -name '*.xml' ! -name '_*') | sed 's/\.xml$/.hkx/'; fi \
  | sed 's|^\./||' | while read -r r; do [[ -f $r ]] && echo "$r" || ls -d "${r%.hkx}".[hH][kK][xX] 2>/dev/null; done \
  | tr '\n' '\0' | xargs -0 -P "$JOBS" -I{} bash -c 'rt "$1"' _ {} | LC_ALL=C sort -t$'\t' -k2 > "$WORK/_roundtrip.tsv"
cut -f1 "$WORK/_roundtrip.tsv" | sed 's/ .*//' | sort | uniq -c
