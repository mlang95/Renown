@echo off
REM ============================================================================
REM Renown game simulator  —  CE build
REM
REM   Plays all-AI games with the settlement board's own rules and AI seats
REM   (references\settlement_board.html, run headless under Node), then writes
REM   tables, a cross-game report and RTS-style end screens.
REM
REM   Output: CE\lab_out\sim\<TAG>\
REM     games.jsonl      raw record of every game (per-turn snapshots, gold ledger, Envoys, Battles, treaties, wars, Edicts)
REM     games.csv / seats.csv / ledger.csv / turns.parquet
REM     report.html      cultures, archetypes, factions, seats, maps, player counts, Craft value, build paths, timelines, diagnostics
REM     endscreens\      one end screen per game (first END_SCREENS games)
REM ============================================================================
setlocal
cd /d "%~dp0"

REM --- Interpreters ---
REM PY needs pandas, numpy, matplotlib, pyarrow (the base Anaconda install has them).
set PY="C:\Users\Matt\anaconda3\python.exe"
set PY_BUILD="C:\Users\Matt\anaconda3\envs\kotr\python.exe"
set NODE="C:\Program Files\nodejs\node.exe"
if not exist %NODE% set NODE=node

REM ============================ GAME SETTINGS =================================
REM PLAYERS : player counts to run, comma-separated (2-7).
REM MAPS    : map presets, comma-separated, or all. Names as in the board's map generator
REM           (Default, Bleak Highlands, Blighthold, Coloured Mountains, Crag Pass, Draggath Wastes, Drakenheart,
REM            Dreadwood, Fair Whitewood, Glen of Pravak, Hermit's Row, Lenaveron, Lost Woods, Marrow Shoals,
REM            Scarlet Forest, Shallow Mire, The Twelfth Reach, Tombs of the Old Gods, Vaelohk, Wharf of St. Brannoch, Wheat Fields).
REM GAMES   : games per (player count, map) cell.
REM TURNS   : turn limit per game; never past GAME_TURN_LIMIT in the data (the rules' last turn, 50).
REM STOP_MAX_RENOWN : 0 = play on past Renown's maximum (the rules: the game ends at Last Alliance Standing or TURNS);
REM           1 = stop a game early once Renown reaches its maximum (faster test runs).
REM AGE     : random, or an Age name (Age of Fracture, Age of Plenty, Age of the Tetramorph, Age of Doubt, Age of Renown).
REM CULTURES: random (deal all 15 evenly), or a comma-separated list to deal from.
REM SEED    : master seed; the same settings and seed replay the same games.
REM WILD_OUTLAW : 1 = Setup places Wild Outlaw Country (the rules), 0 = leave it out (experiment).
set PLAYERS=3,4,5,6
set MAPS=Default,Bleak Highlands,Wheat Fields,Dreadwood
set GAMES=25
set TURNS=50
set STOP_MAX_RENOWN=0
set AGE=random
set CULTURES=random
set SEED=1
set WILD_OUTLAW=1

REM ============================ RUN SETTINGS ==================================
REM WORKERS : parallel games (one Node worker thread each, ~150 MB apiece).
REM TAG     : subfolder under lab_out\sim. Blank = auto-named from the date and time.
REM END_SCREENS : how many games get an end screen.
REM REBUILD : 1 = rebuild the settlement board from the data first (the simulator plays whatever the board holds).
set WORKERS=7
set TAG=
set END_SCREENS=20
set REBUILD=1
REM ============================================================================

if "%TAG%"=="" for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmm"') do set TAG=sim_%%i
set OUT=%~dp0..\lab_out\sim\%TAG%

if "%REBUILD%"=="1" (
  echo Rebuilding the settlement board from renown_data_d10.py ...
  pushd "%~dp0..\references"
  set PYTHONPATH=%~dp0..
  %PY_BUILD% gen_settlement_board.py --data ..\renown_data_d10.py --rules ..\RULES_push_simple.md --out settlement_board.html
  if errorlevel 1 ( popd & echo BOARD BUILD FAILED & pause & exit /b 1 )
  popd
  echo.
)

%NODE% sim_runner.js --players "%PLAYERS%" --maps "%MAPS%" --games %GAMES% --turns %TURNS% --workers %WORKERS% --seed %SEED% --age "%AGE%" --cultures "%CULTURES%" --stop-max-renown %STOP_MAX_RENOWN% --wild %WILD_OUTLAW% --tag "%TAG%" --out "%OUT%"
if errorlevel 1 ( echo SIMULATION FAILED & pause & exit /b 1 )

echo.
echo Analysing ...
%PY% analyse_sim.py "%OUT%" --end-screens %END_SCREENS%

echo.
echo Done. Report: "%OUT%\report.html"
pause
endlocal
