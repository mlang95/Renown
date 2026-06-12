@echo off
REM ============================================================================
REM  build_all.bat - regenerate everything downstream of renown_data.py.
REM  Cards (player-scaled), the Word docs, and the GitHub Pages wiki.
REM  Does NOT run tournaments - that's run_tournament.bat, kept separate.
REM ============================================================================
cd /d "C:\Users\Matt\OneDrive\Desktop\Game\Combatv3"
REM ---------------------------------------------------------------- EDIT THESE
set PY="C:\Users\Matt\anaconda3\envs\kotr\python.exe"
set GIT="C:\Program Files\Git\cmd\git.exe"
REM VERSION : pulled from renown_data.py (single source of truth)
%PY% -c "import renown_data,sys; sys.stdout.write(renown_data.VERSION)" > "%TEMP%\renown_ver.txt"
set /p VERSION=<"%TEMP%\renown_ver.txt"
del "%TEMP%\renown_ver.txt"
REM PUSH_REPO : 1 = commit+tag+push the whole Game repo, 0 = don't
set PUSH_REPO=1
REM REPO_MSG : short description of what changed this version
set REPO_MSG=wiki + reference pages, Mill merge, Cipher Chamber
REM MODE : renown | escalation | both
set MODE=both
REM WHAT : cards | docs | wiki | both
set WHAT=both
REM PLAYERS : table size (2-7)
set PLAYERS=1
REM OUT_DIR : where card PDFs land
set OUT_DIR=cards
REM WIKI_REPO : local clone of the RenownWiki repo (GitHub Pages source)
set WIKI_REPO=C:\Users\Matt\OneDrive\Desktop\Game\RenownWiki
REM PUSH_WIKI : 1 = git commit+push after build, 0 = build only
set PUSH_WIKI=1
REM ---------------------------------------------------------------------------
echo.
echo === build_all : MODE=%MODE%  WHAT=%WHAT%  PLAYERS=%PLAYERS% ===
echo.
if /i "%WHAT%"=="cards" goto cards
if /i "%WHAT%"=="docs"  goto docs
if /i "%WHAT%"=="wiki"  goto wiki
if /i "%WHAT%"=="both"  goto cards
echo Invalid WHAT=%WHAT% & goto end

:cards
echo --- Cards ---
if /i "%MODE%"=="both" (
  %PY% generate_cards.py renown "%OUT_DIR%" %PLAYERS%
  %PY% generate_cards.py escalation "%OUT_DIR%" %PLAYERS%
) else (
  %PY% generate_cards.py %MODE% "%OUT_DIR%" %PLAYERS%
)
if /i "%WHAT%"=="cards" goto end

:docs
echo --- Docs ---
echo   Compendium...
%PY% gen_compendium.py compendium_data.json
%PY% build_compendium.py compendium_data.json Compendium.docx
echo   Rules...
%PY% build_docs.py Rules_authored.docx Rules.docx
echo   FAQ...
%PY% faq_export.py "ask-the-bot\renown_faq.txt"

:wiki
echo --- Wiki ---
rmdir /s /q wiki 2>nul
%PY% build_wiki.py RULES.md wiki
if errorlevel 1 (
  echo   Wiki build FAILED - skipping push.
  goto end
)
if "%PUSH_WIKI%"=="0" (
  echo   Built wiki - push skipped.
  goto end
)
if not exist "%WIKI_REPO%\.git" (
  echo   ERROR: %WIKI_REPO% is not a git repo.
  goto end
)
echo   Syncing into %WIKI_REPO% ...
for /d %%D in ("%WIKI_REPO%\*") do if /i not "%%~nxD"==".git" rmdir /s /q "%%D" 2>nul
for %%F in ("%WIKI_REPO%\*") do if /i not "%%~nxF"==".git" del /q "%%F" 2>nul
xcopy /e /i /y /h wiki "%WIKI_REPO%" >nul
echo   Pushing to GitHub Pages ...
pushd "%WIKI_REPO%"
%GIT% add -A
%GIT% commit -m "wiki rebuild" || echo   (nothing changed)
%GIT% push
popd
:pushrepo
REM ---- optional: commit + tag + push the WHOLE project repo ----
if "%PUSH_REPO%"=="1" (
  echo --- Pushing main repo as v%VERSION% ---
  pushd "C:\Users\Matt\OneDrive\Desktop\Game"
  %GIT% add -A
  %GIT% commit -m "v%VERSION%: %REPO_MSG%" || echo   (nothing to commit)
  %GIT% tag -a v%VERSION% -m "%REPO_MSG%"
  %GIT% push
  %GIT% push origin v%VERSION%
  popd
)


:end
echo.
echo Done. Press any key to close.
pause