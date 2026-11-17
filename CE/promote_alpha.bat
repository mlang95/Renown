@echo off
REM ============================================================================
REM  promote_alpha.bat - publish a committed dev state as the public alpha.
REM
REM  Two folders, one repo:
REM    dev    = this folder (Desktop\Game). Build, test, run tournaments freely;
REM             build_all_CE.bat here is CHANNEL=dev and never touches the wiki.
REM    alpha  = ALPHA_DIR, a git worktree on branch ALPHA_BRANCH. The public side
REM             runs from it: the board server, the Discord bot (!ask / !renown)
REM             and the wiki build. Live games live in ALPHA_DATA, outside git.
REM
REM  Usage (from this folder):
REM    promote_alpha.bat init       one time: create ALPHA_DIR at what is public
REM                                 now (origin/main) and move the live game
REM                                 databases into ALPHA_DATA. Publishes nothing.
REM    promote_alpha.bat            promote the branch you are on (its LAST COMMIT;
REM                                 uncommitted edits are not included)
REM    promote_alpha.bat <ref>      promote a branch / tag / commit instead
REM
REM  A promotion merges <ref> into ALPHA_BRANCH (where the two differ, <ref> wins:
REM  fix things in dev and promote again rather than editing the alpha folder),
REM  copies the last tournament run's summary + pool (the board's Escalation AI and
REM  !renown charts read them; they are git-ignored), then runs build_all_CE.bat
REM  there with CHANNEL=alpha: wiki pushed, branch ALPHA_BRANCH pushed, tag
REM  v<VERSION> created if new. The version is whatever renown_data_d10.py says,
REM  so promote 0.5.0.1, 0.5.0.2, ... as often as you like.
REM  Restart the board server and the bot afterwards (start_public.sh in WSL).
REM ============================================================================
setlocal EnableExtensions EnableDelayedExpansion

REM ---------------------------------------------------------------- EDIT THESE
set GIT="C:\Program Files\Git\cmd\git.exe"
set "ALPHA_DIR=C:\Users\Matt\Renown-alpha"
set "ALPHA_DATA=C:\Users\Matt\Renown-alpha-data"
set ALPHA_BRANCH=alpha
REM ----------------------------------------------------------------------------

set "CE_ROOT=%~dp0"
if "%CE_ROOT:~-1%"=="\" set "CE_ROOT=%CE_ROOT:~0,-1%"
for %%I in ("%CE_ROOT%\..") do set "DEV_DIR=%%~fI"

if /i "%~1"=="init" goto init

REM ---------------------------------------------------------------- promote
if not exist "%ALPHA_DIR%\.git" (
  echo No alpha folder at %ALPHA_DIR% - run "promote_alpha.bat init" first.
  pause & exit /b 1
)
set "REF=%~1"
if "%REF%"=="" for /f "delims=" %%B in ('"%GIT% -C "%DEV_DIR%" branch --show-current"') do set "REF=%%B"
if "%REF%"=="" ( echo Detached HEAD in %DEV_DIR% - name a branch, tag or commit. & pause & exit /b 1 )
set "SHA="
for /f "delims=" %%S in ('"%GIT% -C "%DEV_DIR%" rev-list -n 1 --abbrev-commit "%REF%" 2>nul"') do set "SHA=%%S"
if "%SHA%"=="" ( echo "%REF%" is not a branch, tag or commit here. & pause & exit /b 1 )

set "DIRTY="
for /f "delims=" %%L in ('"%GIT% -C "%DEV_DIR%" status --porcelain --untracked-files^=no"') do set "DIRTY=1"
if defined DIRTY (
  echo NOTE: %DEV_DIR% has uncommitted changes. They are NOT promoted - only the last commit of %REF%.
)
set "ADIRTY="
%GIT% -C "%ALPHA_DIR%" status --porcelain --untracked-files=no -- . ":^CE/lab_out" > "%TEMP%\renown_dirty.txt"
for %%A in ("%TEMP%\renown_dirty.txt") do if %%~zA GTR 0 set "ADIRTY=1"
if defined ADIRTY (
  echo ERROR: %ALPHA_DIR% has uncommitted changes. Commit or discard them there first.
  pause & exit /b 1
)

echo.
echo Promote %REF% ^(%SHA%^) to %ALPHA_BRANCH%. Commits it adds:
%GIT% -C "%DEV_DIR%" log --oneline --no-decorate %ALPHA_BRANCH%..%SHA% -n 15
echo.
echo This publishes: the wiki ^(GitHub Pages^), branch %ALPHA_BRANCH% and its tag on GitHub.
choice /m "Go ahead"
if errorlevel 2 ( echo Cancelled - nothing changed. & pause & exit /b 0 )

REM lab_out output copied by the last promotion is re-copied below; reset the tracked part so the merge is clean
%GIT% -C "%ALPHA_DIR%" checkout -- CE/lab_out 2>nul
%GIT% -C "%ALPHA_DIR%" merge --no-edit -X theirs %SHA% -m "Promote %REF% (%SHA%) to %ALPHA_BRANCH%"
if errorlevel 1 (
  %GIT% -C "%ALPHA_DIR%" merge --abort 2>nul
  echo ERROR: the merge into %ALPHA_BRANCH% stopped ^(nothing published^). Resolve it in %ALPHA_DIR% or ask Claude.
  pause & exit /b 1
)

call :copy_lab
call :launcher
set CHANNEL=alpha
call "%ALPHA_DIR%\CE\build_all_CE.bat"
echo.
echo Promoted %REF% ^(%SHA%^). Restart the public side in WSL:  bash /mnt/c/Users/Matt/Renown-alpha-data/start_public.sh
pause
exit /b 0

REM ---------------------------------------------------------------- init
:init
%GIT% -C "%DEV_DIR%" fetch origin
if exist "%ALPHA_DIR%\.git" (
  echo %ALPHA_DIR% already exists - skipping the checkout.
) else (
  %GIT% -C "%DEV_DIR%" rev-parse --verify --quiet refs/remotes/origin/%ALPHA_BRANCH% >nul
  if errorlevel 1 (
    echo Creating %ALPHA_DIR% on new branch %ALPHA_BRANCH% at origin/main ^(what is public now^)...
    %GIT% -C "%DEV_DIR%" worktree add --no-track -b %ALPHA_BRANCH% "%ALPHA_DIR%" origin/main
  ) else (
    echo Creating %ALPHA_DIR% on branch %ALPHA_BRANCH% from origin/%ALPHA_BRANCH%...
    %GIT% -C "%DEV_DIR%" worktree add "%ALPHA_DIR%" %ALPHA_BRANCH%
  )
  if errorlevel 1 ( echo ERROR: could not create the alpha folder. & pause & exit /b 1 )
)
if exist "%ALPHA_DATA%" (
  echo %ALPHA_DATA% already exists - live games left as they are.
) else (
  echo Copying the live game databases to %ALPHA_DATA% ^(stop the board server first^)...
  mkdir "%ALPHA_DATA%\games"
  if exist "%CE_ROOT%\references\renown.db" copy /y "%CE_ROOT%\references\renown.db*" "%ALPHA_DATA%\" >nul
  if exist "%CE_ROOT%\references\games" robocopy "%CE_ROOT%\references\games" "%ALPHA_DATA%\games" /E /NFL /NDL /NJH /NJS >nul
)
call :copy_lab
call :launcher
echo.
echo Alpha folder ready: %ALPHA_DIR%   live games: %ALPHA_DATA%
echo Nothing was published. Start the public side in WSL:  bash /mnt/c/Users/Matt/Renown-alpha-data/start_public.sh
pause
exit /b 0

REM ---------------------------------------------------------------- copy_lab
REM The last tournament run (git-ignored): summary + pool for the board's Escalation AI,
REM charts for !renown. The big matchups files stay behind.
:copy_lab
set "DEV_LAB=%CE_ROOT%\lab_out"
set "ALPHA_LAB=%ALPHA_DIR%\CE\lab_out"
if not exist "%DEV_LAB%\last_run.json" ( echo   no tournament run in %DEV_LAB% - skipped. & exit /b 0 )
set "RUN_TAG="
if exist "%TEMP%\renown_runtag.txt" del "%TEMP%\renown_runtag.txt"
powershell -NoProfile -Command "$j = Get-Content -Raw '%DEV_LAB%\last_run.json' | ConvertFrom-Json; [IO.File]::WriteAllText('%TEMP%\renown_runtag.txt', [string]$j.tag)"
if exist "%TEMP%\renown_runtag.txt" set /p RUN_TAG=<"%TEMP%\renown_runtag.txt"
if "%RUN_TAG%"=="" ( echo   last_run.json has no tag - skipped. & exit /b 0 )
if not exist "%ALPHA_LAB%" mkdir "%ALPHA_LAB%"
robocopy "%DEV_LAB%\%RUN_TAG%" "%ALPHA_LAB%\%RUN_TAG%" /E /XF *.parquet matchups*.csv /NFL /NDL /NJH /NJS >nul
powershell -NoProfile -Command "$j = Get-Content -Raw '%DEV_LAB%\last_run.json' | ConvertFrom-Json; $j.out_dir = '%ALPHA_LAB%\%RUN_TAG%'; [IO.File]::WriteAllText('%ALPHA_LAB%\last_run.json', ($j | ConvertTo-Json -Depth 5))"
echo   tournament run %RUN_TAG% copied to the alpha folder.
exit /b 0

REM ---------------------------------------------------------------- launcher
REM start_public.sh lives with the live data (outside git), refreshed from this folder's copy.
:launcher
if not exist "%ALPHA_DATA%" mkdir "%ALPHA_DATA%"
if exist "%CE_ROOT%\start_public.sh" copy /y "%CE_ROOT%\start_public.sh" "%ALPHA_DATA%\start_public.sh" >nul
exit /b 0
