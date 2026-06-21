@echo off
REM ============================================================================
REM  build_all.bat - regenerate everything downstream of renown_data.py.
REM  Cards (player-scaled), the Word docs, the GitHub Pages wiki, and the
REM  print-and-tape board(s). Does NOT run tournaments - that's run_tournament.bat.
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
REM ---- BOARD (print-and-tape start map) --------------------------------------
REM BUILD_BOARD : 1 = generate a start-board PDF, 0 = skip
set BUILD_BOARD=1
REM BOARD_DIR   : folder holding mapgen.py / hexmap.py / hexgen.py / build_board.py
set BOARD_DIR=C:\Users\Matt\OneDrive\Desktop\Game\Combatv3\mapgen
REM board dimensions, table size, seed, hex size (mm c->corner), paper
set BOARD_W=13
set BOARD_H=7
set BOARD_PLAYERS=2
set BOARD_SEED=96
set BOARD_HEX=20
set BOARD_PAPER=A4
REM BOARD_RES : 1 = stamp raw-material toppers, 0 = terrain only (loose tokens)
set BOARD_RES=0
REM BOARD_OUT : output PDF (lands in BOARD_DIR)
set BOARD_OUT=%BOARD_DIR%\board_%BOARD_W%x%BOARD_H%_%BOARD_PLAYERS%p.pdf
REM ---- TACTICAL BOARD (one-sheet skirmish map) -------------------------------
REM BUILD_TACTICAL : 1 = also emit the one-sheet skirmish board, 0 = skip
REM   terrain-only, landscape; ignores players/resources; auto-clamps to fit.
set BUILD_TACTICAL=1
set TAC_W=9
set TAC_H=6
set TAC_SEED=26
set TAC_HEX=20
set TAC_OUT=%BOARD_DIR%\tactical_%TAC_W%x%TAC_H%_s%TAC_SEED%.pdf
REM ---------------------------------------------------------------------------
echo.
echo === build_all : MODE=%MODE%  WHAT=%WHAT%  PLAYERS=%PLAYERS%  BOARD=%BUILD_BOARD%  TACTICAL=%BUILD_TACTICAL% ===
echo.
if /i "%BUILD_BOARD%"=="1" call :board
if /i "%BUILD_TACTICAL%"=="1" call :tactical
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
%PY% md_to_docx.py RULES_reorganized.md Rules.docx 
echo   FAQ...
%PY% faq_export.py "ask-the-bot\renown_faq.txt"
echo   Combat quick-reference sheet (front/back PDF)...
%PY% combat_sheet.py "%OUT_DIR%\combat_sheet.pdf"
echo   Specialization trees (landscape PDF)...
%PY% spec_tree_sheet.py "%OUT_DIR%\spec_trees.pdf"
:wiki
echo --- Wiki ---
rmdir /s /q wiki 2>nul
%PY% build_wiki.py RULES_reorganized.md wiki
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
goto :eof
REM ============================================================================
REM  :board  - generate the print-and-tape start map PDF into BOARD_DIR
REM ============================================================================
:board
echo --- Board ---
if not exist "%BOARD_DIR%\build_board.py" (
  echo   ERROR: build_board.py not found in %BOARD_DIR% - skipping board.
  exit /b
)
REM svglib is the only extra dep (reportlab already present); install if missing
%PY% -c "import svglib" 2>nul || %PY% -m pip install svglib
set BOARD_FLAGS=
if /i "%BOARD_RES%"=="0" set BOARD_FLAGS=--no-resources
pushd "%BOARD_DIR%"
%PY% build_board.py %BOARD_W% %BOARD_H% --seed %BOARD_SEED% --hex %BOARD_HEX% --paper %BOARD_PAPER% --param players=%BOARD_PLAYERS% %BOARD_FLAGS% --out "%BOARD_OUT%"
popd
echo   Board -^> %BOARD_OUT%
exit /b
REM ============================================================================
REM  :tactical  - one-sheet skirmish board (terrain only, landscape) into BOARD_DIR
REM ============================================================================
:tactical
echo --- Tactical board ---
if not exist "%BOARD_DIR%\build_board.py" (
  echo   ERROR: build_board.py not found in %BOARD_DIR% - skipping tactical.
  exit /b
)
%PY% -c "import svglib" 2>nul || %PY% -m pip install svglib
pushd "%BOARD_DIR%"
%PY% build_board.py %TAC_W% %TAC_H% --tactical --seed %TAC_SEED% --hex %TAC_HEX% --paper %BOARD_PAPER% --out "%TAC_OUT%"
popd
echo   Tactical board -^> %TAC_OUT%
exit /b