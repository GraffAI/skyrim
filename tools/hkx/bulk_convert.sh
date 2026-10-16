#!/usr/bin/env bash
# Bulk HKX (SE, hk_2010.2.0-r1, 64-bit) -> hkpackfile XML with serde-hkx's hkxc.
#
#   bulk_convert.sh graph  [RAW] [OUT]       every .hkx NOT under an `animations/` dir
#                                            (behaviors, characters, character assets,
#                                            project files, plus misc graphs/skeletons)
#   bulk_convert.sh anim N [RAW] [OUT]       a deterministic sample of N animations/*.hkx
#   bulk_convert.sh anim-all [RAW] [OUT]     every .hkx under an `animations/` dir
#
# Defaults: RAW=~/skyrim-data-extracted/raw, OUT=~/skyrim-data-extracted/xml (graph) or
# ~/skyrim-data-extracted/xml-anim-sample (anim) or ~/skyrim-data-extracted/xml-anim
# (anim-all). Output mirrors RAW's paths, .hkx -> .xml.
# Writes OUT/_manifest.tsv (status, dir_category, root_classes, bytes_in, bytes_out, relpath) and
# OUT/_errors.log. hkxc exits 0 even when a conversion fails (measured with 2.0.0), so
# success here means "hkxc wrote a non-empty file that starts with <?xml".
# HKXC overrides the binary (default: the pinned build from build_serde_hkx.sh).
set -euo pipefail

mode=${1:?usage: bulk_convert.sh graph|anim N|anim-all [RAW] [OUT]}; shift
n=0
if [[ $mode == anim ]]; then n=${1:?anim needs N}; shift; fi
RAW=${1:-$HOME/skyrim-data-extracted/raw}
case $mode in graph|anim|anim-all) ;; *) echo "unknown mode $mode" >&2; exit 2 ;; esac
if [[ $mode == anim ]]; then OUT=${2:-$HOME/skyrim-data-extracted/xml-anim-sample}
elif [[ $mode == anim-all ]]; then OUT=${2:-$HOME/skyrim-data-extracted/xml-anim}
else OUT=${2:-$HOME/skyrim-data-extracted/xml}; fi
HKXC=${HKXC:-$HOME/skyrim-data-extracted/_toolsrc/serde-hkx/target/release/hkxc}
[[ -x $HKXC ]] || { echo "no hkxc at $HKXC (run build_serde_hkx.sh)" >&2; exit 1; }
JOBS=${JOBS:-$(sysctl -n hw.ncpu 2>/dev/null || echo 8)}

mkdir -p "$OUT"
list=$(mktemp); trap 'rm -f "$list"' EXIT
cd "$RAW"
if [[ $mode == graph ]]; then
  find . -type f -iname '*.hkx' | grep -vi '/animations/' | sed 's|^\./||' | LC_ALL=C sort > "$list"
elif [[ $mode == anim-all ]]; then
  find . -type f -iname '*.hkx' | grep -i '/animations/' | sed 's|^\./||' | LC_ALL=C sort > "$list"
else
  # every k-th animation in sorted order: deterministic, spread across actors
  find . -type f -iname '*.hkx' | grep -i '/animations/' | sed 's|^\./||' | LC_ALL=C sort > "$list.all"
  total=$(wc -l < "$list.all"); step=$(( total / n )); (( step < 1 )) && step=1
  awk -v s="$step" -v n="$n" 'NR % s == 1 && c < n {print; c++}' "$list.all" > "$list"; rm -f "$list.all"
fi
echo "converting $(wc -l < "$list" | tr -d ' ') files from $RAW to $OUT with $JOBS jobs" >&2

export RAW OUT HKXC
one() {
  rel=$1
  out="$OUT/${rel%.*}.xml"
  mkdir -p "$(dirname "$out")"
  d=$(dirname "$rel" | tr 'A-Z' 'a-z'); base=$(basename "$d")
  case "$d" in
    */animations|*/animations/*) cat=animation ;;
    *) case "$base" in
         behaviors*) cat=behavior_dir ;; characters*) cat=characters_dir ;;
         "character assets"*|characterassets*) cat=character_assets_dir ;;
         *) cat=other_dir ;;
       esac ;;
  esac
  err=$("$HKXC" convert -i "$RAW/$rel" -o "$out" -v xml 2>&1 >/dev/null || true)
  if [[ -s $out ]] && head -c 5 "$out" | grep -q '<?xml'; then st=ok; else st=FAIL; rm -f "$out"
    printf '%s\n%s\n\n' "$rel" "$err" | sed 's/\x1b\[[0-9;]*m//g' >> "$OUT/_errors.log"; fi
  # root classes: the className of each hkRootLevelContainer namedVariant (hkbProjectData,
  # hkbBehaviorGraph, hkbCharacterData, hkaAnimationContainer, ...), joined with '+'
  roots=-
  [[ $st == ok ]] && roots=$(grep -m8 '<hkparam name="className">' "$out" | sed 's/.*">\(.*\)<.*/\1/' | paste -sd+ - || true)
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$st" "$cat" "${roots:--}" "$(stat -f %z "$RAW/$rel")" "$( [[ -f $out ]] && stat -f %z "$out" || echo 0)" "$rel"
}
export -f one
: > "$OUT/_errors.log"
tr '\n' '\0' < "$list" | xargs -0 -P "$JOBS" -I{} bash -c 'one "$1"' _ {} | LC_ALL=C sort -t$'\t' -k6 > "$OUT/_manifest.tsv"
echo "status counts:" >&2; cut -f1 "$OUT/_manifest.tsv" | sort | uniq -c >&2
echo "by dir category:" >&2; cut -f1,2 "$OUT/_manifest.tsv" | sort | uniq -c >&2
echo "by root class:" >&2; cut -f1,3 "$OUT/_manifest.tsv" | sort | uniq -c | sort -rn >&2
