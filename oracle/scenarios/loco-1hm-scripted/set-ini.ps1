# 006 M44 Part 1.5 (D396): bAlwaysActive=1 under [General] in the game's Skyrim.ini, so an unattended
# run does not pause when the window loses focus. The first time, the original file is copied to
# -Backup (never overwritten afterwards). Prints what it found and what it did.
param([string]$Ini, [string]$Backup)
if (-not (Test-Path -LiteralPath $Ini)) { "no $Ini"; exit 1 }
New-Item -ItemType Directory -Force -Path $Backup | Out-Null
$bak = Join-Path $Backup 'Skyrim.ini'
if (-not (Test-Path -LiteralPath $bak)) { Copy-Item -LiteralPath $Ini -Destination $bak; "backed up $Ini to $bak" } else { "backup already at $bak (kept)" }
$lines = [System.Collections.Generic.List[string]](Get-Content -LiteralPath $Ini)
$sect = ''; $gen = -1; $hit = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
  $l = $lines[$i].Trim()
  if ($l -match '^\[(.+)\]$') { $sect = $Matches[1]; if ($sect -ieq 'General') { $gen = $i } ; continue }
  if ($sect -ieq 'General' -and $l -match '^bAlwaysActive\s*=') { $hit = $i }
}
if ($hit -ge 0) {
  if ($lines[$hit].Trim() -eq 'bAlwaysActive=1') { "bAlwaysActive=1 already (line $($hit + 1))"; exit 0 }
  "line $($hit + 1) was '$($lines[$hit])'"; $lines[$hit] = 'bAlwaysActive=1'
} elseif ($gen -ge 0) { $lines.Insert($gen + 1, 'bAlwaysActive=1'); "inserted after [General] (line $($gen + 1))" }
else { $lines.Insert(0, 'bAlwaysActive=1'); $lines.Insert(0, '[General]'); 'added a [General] section' }
Set-Content -LiteralPath $Ini -Value $lines -Encoding ascii
'bAlwaysActive=1 set'
