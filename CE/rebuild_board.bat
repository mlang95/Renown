@echo off
REM rebuild_board.bat - regenerate only the settlement board (no full build).
REM The server re-reads settlement_board.html on every page load: just refresh the browser afterwards.
setlocal
set PY="C:\Users\Matt\anaconda3\envs\kotr\python.exe"
set CE_ROOT=C:\Users\Matt\OneDrive\Desktop\Game\CE
cd /d "%CE_ROOT%\references" || exit /b 1
REM dice_config.py lives in Combatv4: put it on the path so the data reads the real dice (not its fallback copy)
set PYTHONPATH=%CE_ROOT%\Combatv4;%CE_ROOT%;%PYTHONPATH%
%PY% gen_settlement_board.py --data "%CE_ROOT%\renown_data_d10.py" --rules "%CE_ROOT%\RULES_push.md" --out "settlement_board.html"
if errorlevel 1 (echo Board build FAILED & exit /b 1)
echo Board rebuilt - refresh the browser.
endlocal