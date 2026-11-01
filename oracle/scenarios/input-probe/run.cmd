@echo off
rem 006 M44 Part 1.5: the interim host runner of a scripted oracle scenario, until run.ps1 has its
rem branch for it (Part 4). `devx oracle run <this dir>` copies the directory to C:\oracle\in\<name>
rem and runs this file with ORACLE_IN (the copy) and ORACLE_OUT set. It waits for Steam's logon,
rem sets bAlwaysActive=1 in Skyrim.ini (D396; the first original is kept in C:\oracle\in\ini-backup),
rem starts the game through the script extender's loader with ORACLE_SCENARIO = this directory, waits
rem for the game to end (wait-game.ps1), and copies the logs. The save directory is only read; the
rem save's sha256 is taken before and after.
rem Exit (the run's `done`, D395): 0 the game exited by itself after a closed trace; 124 it was
rem killed 30 s after a closed trace; 3 the input hook was refused; 6 killed with no closed trace
rem after WAIT s; 7 exited with no oracle.status; 5 the game never started; 8 no Steam logon.
setlocal
set "WAIT=420"
set "STEAMWAIT=180"
set "GAME=C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition"
set "DOCS=%USERPROFILE%\Documents\My Games\Skyrim Special Edition"
set /a N=0
:steamwait
set "ACTIVE=0"
for /f "tokens=3" %%A in ('reg query "HKCU\Software\Valve\Steam\ActiveProcess" /v ActiveUser 2^>nul ^| find "ActiveUser"') do set "ACTIVE=%%A"
if not "%ACTIVE%"=="0x0" if not "%ACTIVE%"=="0" goto steamok
if %N% geq %STEAMWAIT% ( echo steam not logged on after %STEAMWAIT% s > "%ORACLE_OUT%\steam.txt" & exit /b 8 )
ping -n 6 127.0.0.1 > nul
set /a N+=5
goto steamwait
:steamok
echo steam logged on after %N% s (ActiveUser %ACTIVE%) > "%ORACLE_OUT%\steam.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File "%ORACLE_IN%\set-ini.ps1" -Ini "%DOCS%\Skyrim.ini" -Backup "C:\oracle\in\ini-backup" > "%ORACLE_OUT%\ini.txt" 2>&1
certutil -hashfile "%DOCS%\Saves\loco1hm.ess" SHA256 > "%ORACLE_OUT%\save-before.txt" 2>&1
if exist "%DOCS%\SKSE\oracle.log" del /q "%DOCS%\SKSE\oracle.log"
if exist "%DOCS%\SKSE\skse64.log" del /q "%DOCS%\SKSE\skse64.log"
set "ORACLE_SCENARIO=%ORACLE_IN%"
set "SteamAppId=489830"
set "SteamGameId=489830"
cd /d "%GAME%"
echo start %date% %time% > "%ORACLE_OUT%\times.txt"
start "" "%GAME%\skse64_loader.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File "%ORACLE_IN%\wait-game.ps1" -Out "%ORACLE_OUT%" -Wait %WAIT% -Grace 30
set "RC=%errorlevel%"
echo end %date% %time% >> "%ORACLE_OUT%\times.txt"
certutil -hashfile "%DOCS%\Saves\loco1hm.ess" SHA256 > "%ORACLE_OUT%\save-after.txt" 2>&1
dir "%DOCS%\Saves" > "%ORACLE_OUT%\saves.txt" 2>&1
if exist "%DOCS%\SKSE\oracle.log" copy /y "%DOCS%\SKSE\oracle.log" "%ORACLE_OUT%\oracle.log" > nul
if exist "%DOCS%\SKSE\skse64.log" copy /y "%DOCS%\SKSE\skse64.log" "%ORACLE_OUT%\skse64.log" > nul
exit /b %RC%
