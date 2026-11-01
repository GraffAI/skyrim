# 006 M44 Part 1.5 (D395): wait for SkyrimSE.exe, hold a handle to it, and decide the run's `done`:
#   0   it exited by itself after oracle.status said `closed` (and not by the plugin's own
#       TerminateProcess, exit code 0xAC1E);
#   124 it was still running -Grace s after `closed` (or ended itself with 0xAC1E): killed;
#   3   oracle.status says `refused` (the input hook, D388), whatever happened next;
#   6   no `closed` within -Wait s: killed;  7 it exited with no oracle.status;  5 never started.
# Writes game-exit.txt in -Out: when it was seen, when the trace closed, when and how it ended.
param([string]$Out, [int]$Wait = 420, [int]$Grace = 30)
$status = Join-Path $Out 'oracle.status'
$log = Join-Path $Out 'game-exit.txt'
function Note([string]$m) { $m | Out-File -Append -Encoding ascii $log }
$p = $null
for ($i = 0; $i -lt 120 -and -not $p; $i++) { $p = Get-Process SkyrimSE -ErrorAction SilentlyContinue | Select-Object -First 1; if (-not $p) { Start-Sleep -Milliseconds 500 } }
if (-not $p) { Note 'never saw SkyrimSE.exe'; exit 5 }
$null = $p.Handle   # caches the handle, so ExitCode is readable after the exit
$t0 = Get-Date
Note "seen pid $($p.Id) at $($t0.ToUniversalTime().ToString('o'))"
$closedAt = $null
$refused = $false
while ($true) {
  if ($p.WaitForExit(500)) { break }
  $now = Get-Date
  if (-not $closedAt -and (Test-Path $status)) {
    $first = (Get-Content -TotalCount 1 $status)
    if ($first -match '^(closed|refused)') {
      $closedAt = $now
      $refused = $first -match '^refused'
      Note "oracle.status at $($now.ToUniversalTime().ToString('o')): $first"
    }
  }
  if ($closedAt -and ($now - $closedAt).TotalSeconds -ge $Grace) {
    Note "still running $Grace s after oracle.status at $($now.ToUniversalTime().ToString('o')): killed"
    Stop-Process -Id $p.Id -Force
    if ($refused) { exit 3 }
    exit 124
  }
  if (-not $closedAt -and ($now - $t0).TotalSeconds -ge $Wait) {
    Note "no closed trace after $Wait s at $($now.ToUniversalTime().ToString('o')): killed"
    Stop-Process -Id $p.Id -Force
    exit 6
  }
}
$code = $p.ExitCode
$after = if ($closedAt) { '{0:N1} s after oracle.status' -f ((Get-Date) - $closedAt).TotalSeconds } else { 'no oracle.status seen while running' }
Note ("exited at {0} code {1} (0x{1:X}), {2}" -f $p.ExitTime.ToUniversalTime().ToString('o'), $code, $after)
if (-not (Test-Path $status)) { exit 7 }
$first = (Get-Content -TotalCount 1 $status)
if ($first -match '^refused') { exit 3 }
if ($code -eq 0xAC1E) { exit 124 }
exit 0
