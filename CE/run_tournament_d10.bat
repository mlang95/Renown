@echo off
REM ============================================================================
REM Renown d10 tournament runner  —  CE build
REM
REM   C:\Users\Matt\OneDrive\Desktop\Game\CE\           <- this tree, self-contained
REM   C:\Users\Matt\OneDrive\Desktop\Game\Combatv3\     <- d6 build, NEVER touched
REM
REM CE imports nothing from Combatv3. Output goes to CE\lab_out\<TAG>\.
REM All paths derive from this file's location (%~dp0), so CE can be moved freely.
REM ============================================================================
setlocal
cd /d "%~dp0"

REM --- Interpreter (needs numpy, pandas, pyarrow, numba) ---
set PY="C:\Users\Matt\AppData\Local\Programs\Python\Python39\python.exe"
REM Conda alternative:
REM set PY="C:\Users\Matt\anaconda3\envs\kotr\python.exe"

REM ============================ DICE SETTINGS =================================
REM FACES   : die size. 10 for this build.
REM FOCUSED : natural result Focused fires on. 10 = nat-max only, 9 = top two faces.
REM FAT_S   : Fatigue token penalty to Strike (magnitude).
REM FAT_M   : Fatigue token penalty to Morale (magnitude).
REM PARRY   : base Parry target.
REM RECOVER : worst rung of the Recover ladder.
REM AUTOPASS: blank keeps the auto-pass rule; set to 1 to delete it.

set FACES=10
set FOCUSED=10
set FAT_S=0
set FAT_M=2
set PARRY=8
set RECOVER=8
set AUTOPASS=
set DEADLY_AP=10
set DEADLY_MODE=set
set UNSTOP=2
set IMP_PARRY=
REM NO_FALL_BACK: 1 = no army picks Fall Back (Arquebus always plays Fighting Formation); 0 = Fall Back allowed
set NO_FALL_BACK=1
set RENOWN_NO_FALL_BACK=%NO_FALL_BACK%

REM set FACES=8
REM set FOCUSED=8
REM set FAT_S=1
REM set FAT_M=1
REM set PARRY=7
REM set RECOVER=8
REM set AUTOPASS=
REM TAG: subfolder under lab_out. Blank = auto-named from the dice settings.
set TAG=

REM ============================ POOL SETTINGS =================================
REM Budget is TI = Holdings per build (each Holding brings its Mastery Chain line). Wards used (MPC) is reported only.
REM POOL: holding_first = Holdings first, gear from their text, balanced per (Retinue x TI)  [TI_MIN/TI_MAX, PER_CELL]
REM       balanced      = gear first, full legal gear cross, balanced per (Retinue x TI)     [TI_MIN/TI_MAX, PER_CELL]
REM       generator     = every Holding combination within TI (archetype_pool)              [TI_MIN/TI_MAX, STRATIFY per TI]
set POOL=holding_first
set TI_MIN=8
set TI_MAX=20
REM PER_CELL vs STRATIFY: both cap how many builds go into the pool; which one is read depends on POOL.
REM   PER_CELL  (holding_first, balanced): max builds per (Retinue x TI) cell, i.e. per Retinue at each TI value.
REM             Pool size <= 4 Retinues x PER_CELL x (TI_MAX - TI_MIN + 1). Low TI cells often hold fewer builds
REM             than the cap, so the real pool comes out a little smaller. "none" = every build.
REM             e.g. TI 5-12 (8 values) x 4 x 50 = up to 1,600 builds.
REM   STRATIFY  (generator only): max builds per TI value, split as evenly as it can across the Retinues.
REM             Pool size <= STRATIFY x (TI_MAX - TI_MIN + 1). "all" = every build.
REM             e.g. TI 5-12 x 500 = up to 4,000 builds.
REM   Run time and file size grow with the SQUARE of the pool (every build plays every other):
REM   1,600 builds = ~2.6M pairings per tournament; 4,000 builds = ~16M. Halve the cap to quarter the run.
set PER_CELL=50
REM BALANCE (holding_first only): weapon = each (Retinue x TI) cell's slots dealt evenly across the weapons
REM         it can field, so rare weapons (Estoc, Bastard Sword) get a full share; none = uniform sample.
REM         weapon_kit = dealt across weapon x kit (each shield, Dual Wield, none), so a weapon's
REM         shield builds are not crowded out by its cheaper Florentine builds (recommended).
set BALANCE=weapon_kit
set STRATIFY=500
REM POOL_CSV: reuse a saved pool instead of building one (same builds, so equipment changes compare cleanly).
REM           blank = build a new pool; last = the pool the last run used; or a path to a saved loadouts_*.csv
REM           Safe for equipment stats (weapon / armour / shield / Retinue numbers and keywords). Holding text,
REM           tree or unlock changes make a saved pool stale: the run lists the mismatches and stops.
set POOL_CSV=
REM ALLOW_STALE: 1 = run a reused pool even when it no longer matches the data
set ALLOW_STALE=
REM POOL_CACHE: 1 = when POOL_CSV is blank, reuse a cached pool if the tree, Holding text, gear rules and pool
REM             settings are unchanged since it was built (lab_out\_pool_cache); 0 = always build a new pool
set POOL_CACHE=1
set RUNS=25

REM ============================ TOURNAMENTS ===================================
REM RANDOM=1  : Random tournament (summary.csv, matchups.parquet)
REM OPTIMAL=1 : Optimal tournament, both sides play the per-pairing equilibrium mix (summary_optimal.csv, ...)
REM PLAYSTYLE=1: heuristic-playstyle tournament (summary_playstyle.csv, ...)
REM EXPLORER=1: write build_explorer.html / build_explorer_optimal.html into the run folder
set RANDOM=0
set OPTIMAL=1
set PLAYSTYLE=0
set EXPLORER=1

REM ============================ MEMORY SETTINGS ===============================
REM WORKERS: each initializes numba and RESERVES several GB of Windows COMMIT.
REM Keep at 6-8. Lower on MemoryError; raise cautiously.
set WORKERS=12
set RENOWN_MEM_DEBUG=1
set SLOT_BUDGET=auto
REM auto
REM ============================================================================

REM Exported so spawned workers inherit the same dice settings.
set RENOWN_PARRY_BASE=%PARRY%
set RENOWN_RECOVER_BASE=%RECOVER%

set MODES=
if not "%RANDOM%"=="1"    set MODES=%MODES% --no-random
if "%OPTIMAL%"=="1"       set MODES=%MODES% --optimal
if not "%PLAYSTYLE%"=="1" set MODES=%MODES% --no-playstyle
if not "%EXPLORER%"=="1"  set MODES=%MODES% --no-explorer

set DICE=--faces %FACES% --focused %FOCUSED% --fatigue-strike %FAT_S% --fatigue-morale %FAT_M%
if not "%PARRY%"==""       set DICE=%DICE% --parry-base %PARRY%
if not "%RECOVER%"==""     set DICE=%DICE% --recover-base %RECOVER%
if not "%DEADLY_AP%"==""   set DICE=%DICE% --deadly-ap %DEADLY_AP%
if not "%DEADLY_MODE%"=="" set DICE=%DICE% --deadly-mode %DEADLY_MODE%
if not "%UNSTOP%"==""      set DICE=%DICE% --unstoppable %UNSTOP%
if not "%IMP_PARRY%"==""   set DICE=%DICE% --improved-parry %IMP_PARRY%

REM NOTE: the bat already exports RENOWN_PARRY_BASE / RENOWN_RECOVER_BASE. Those
REM still work as the env fallback; the --parry-base/--recover-base flags now
REM override them explicitly and put PARRY into the tag. Keep both — no conflict.
if not "%AUTOPASS%"=="" set DICE=%DICE% --no-auto-pass
if not "%TAG%"==""      set DICE=%DICE% --tag %TAG%

echo Verifying CE wiring...
%PY% verify_d10.py
if errorlevel 1 (
  echo.
  echo VERIFY FAILED - not starting the run. Fix the errors above.
  pause
  exit /b 1
)
echo.

set COMMON=--runs %RUNS% --slot-budget %SLOT_BUDGET% --workers %WORKERS% %MODES%
if not "%POOL_CSV%"=="" set COMMON=%COMMON% --csv "%POOL_CSV%"
if "%ALLOW_STALE%"=="1" (set RENOWN_ALLOW_STALE=1) else (set RENOWN_ALLOW_STALE=)
if "%POOL_CACHE%"=="0" (set RENOWN_POOL_CACHE=0) else (set RENOWN_POOL_CACHE=1)
if "%POOL%"=="holding_first" (
  %PY% run_tournament_d10.py %DICE% --holding-first --ti-min %TI_MIN% --ti-max %TI_MAX% --per-cell %PER_CELL% --balance %BALANCE% %COMMON%
) else if "%POOL%"=="balanced" (
  %PY% run_tournament_d10.py %DICE% --balanced --ti-min %TI_MIN% --ti-max %TI_MAX% --per-cell %PER_CELL% %COMMON%
) else (
  %PY% run_tournament_d10.py %DICE% --ti-min %TI_MIN% --ti-max %TI_MAX% --stratify %STRATIFY% %COMMON%
)

echo.
echo Done. Output in "%~dp0lab_out"
pause
endlocal
