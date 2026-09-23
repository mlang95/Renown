@echo off
REM ============================================================================
REM  build_all_CE.bat - regenerate everything downstream of the CE data file.
REM
REM  Layout:
REM     CE\combatv4   renown_data_d10.py (or _CE.py), combat + simulation code
REM     CE\sheets     every publishing script: cards, PDFs, docx, wiki
REM     CE\mapgen     map tools + the browser map generator
REM     CE\worldbuilding  renown_worldlore.py + the gen_* world documents
REM     CE\lab_out    ALL generated output
REM
REM  The sheets scripts all "import renown_data", so PYTHONPATH points at
REM  combatv4 rather than each folder keeping its own copy of the data. One
REM  data file, no drift.
REM
REM  Nothing here reaches into Combatv3. The D6 and CE builds stay separate.
REM  Does NOT run tournaments - that's run_tournament.bat. It CAN push the CE
REM  project to GitHub at the end (PUSH_REPO), with large-file handling so a
REM  fat tournament matchups.parquet in lab_out can't break the push.
REM ============================================================================
setlocal EnableExtensions EnableDelayedExpansion

REM ---------------------------------------------------------------- EDIT THESE
set PY="C:\Users\Matt\anaconda3\envs\kotr\python.exe"
set GIT="C:\Program Files\Git\cmd\git.exe"
set CE_ROOT=C:\Users\Matt\OneDrive\Desktop\Game\CE

REM ---- FOLDER NAMES (rename a folder on disk = change one word here) --------
set DIR_CODE=combatv4
set DIR_SHEET=references
set DIR_MAP=mapgen
set DIR_LORE=worldbuilding
set DIR_LAB=lab_out

set CODE_DIR=%CE_ROOT%\%DIR_CODE%
set SHEET_DIR=%CE_ROOT%\%DIR_SHEET%
set MAP_DIR=%CE_ROOT%\%DIR_MAP%
set LORE_DIR=%CE_ROOT%\%DIR_LORE%

REM ---- DATA VARIANT ----------------------------------------------------------
REM DIE : which data file gets copied to renown_data.py. Flip this one line to
REM       trial variants; each variant writes to its own lab_out\<DIE>\ folder
REM       so d8 and d10 output never clobber each other.
REM       Add / rename a row below if you add or rename a data file.
set DIE=d10
set DATA_d8=renown_data_d8.py
set DATA_d10=renown_data_d10.py
set DATA_CE=renown_data_CE.py
call set DATA_SRC=%%DATA_%DIE%%%
REM USE_LAST_RUN : 1 = dice knobs come from lab_out\last_run.json (the most
REM   recent tournament). 0 = dice_config file defaults. Set 0 before a print run.
set USE_LAST_RUN=0

REM LAB_DIR is tagged by variant so trials stay side-by-side.
set LAB_DIR=%CE_ROOT%\%DIR_LAB%\%DIE%

REM RULES : the CE rules markdown that feeds docs + wiki (lives in sheets\)
set RULES_MD=%CE_ROOT%\RULES_reorganized_6.md

REM ---- LORE (world documents from renown_worldlore.py) ----------------------
REM BUILD_LORE : 1 = regenerate the world documents before the wiki, 0 = skip.
set BUILD_LORE=1
REM LORE_OUT : NOT tagged by DIE. The lore is dice-agnostic, so a d8 and a d10
REM   run would otherwise write byte-identical files into two lab_out folders.
set LORE_OUT=%CE_ROOT%\%DIR_LAB%\lore
REM LORE_BOOK : 1 = also build renown_world.pdf (+ .docx if node docx present).
set LORE_BOOK=1
REM LORE_MAP : map image the book pages and the wiki Map page embed.
REM   Blank = no map image, both still build.
set LORE_MAP=%LORE_DIR%\map7.png

REM WHAT   : maps | cards | docs | wiki | lore | all
set WHAT=all
REM MODE   : renown | escalation | both
set MODE=both
REM PLAYERS: table size (2-7) for card scaling
set PLAYERS=2
set OUT_DIR=%LAB_DIR%\cards

REM WIKI_REPO : local clone GitHub Pages serves. Blank = build only.
REM   Do NOT point this at the D6 RenownWiki clone or CE will overwrite it.
set WIKI_REPO=C:\Users\Matt\OneDrive\Desktop\Game\RenownWiki
set PUSH_WIKI=1

REM ---- REPO PUSH (commit + tag + push the CE project to GitHub) --------------
REM PUSH_REPO : 1 = commit+push REPO_DIR after the build, 0 = don't.
set PUSH_REPO=1
REM REPO_DIR  : the git working tree to push. Set to the parent Game root so the
REM   whole folder (CE + Combatv3 + older-state folders) is ONE repo that
REM   snapshots current state. Old states live as folders, not git history.
REM   NOTE: any subfolder with its own .git (Game\RenownWiki, a stray Game\CE\.git)
REM   would be recorded as a submodule pointer, not files - remove/ignore those
REM   (see the .gitignore block below and the one-time setup).
set REPO_DIR=C:\Users\Matt\OneDrive\Desktop\Game
REM REPO_REMOTE : used ONLY to create 'origin' on first run (when REPO_DIR has
REM   no .git yet). Ignored once a repo exists.
set REPO_REMOTE=https://github.com/mlang95/Renown.git
set REPO_BRANCH=main
set REPO_MSG=CE build v%DIE%
REM REPO_TAG : 1 = also create + push tag v<VERSION>, 0 = commit/push only.
set REPO_TAG=1

REM IGNORE_BULK : keep regenerable tournament/analysis output OUT of the repo so
REM   a big matchups.parquet can't get staged and blow past GitHub's 100 MB
REM   limit. These are re-derivable from a tournament run - they don't belong in
REM   git. 1 = on.
set IGNORE_BULK=1
REM   Patterns fed to 'git rm --cached' to untrack any that were committed
REM   before. cmd does NOT expand these globs - git does. (Source CSVs like
REM   equipment.csv / factions_table.csv are NOT matched and stay tracked.)
set BULK_PATTERNS=*.parquet matchups*.csv summary*.csv tactic_matrix*.csv loadouts_gen_*.csv gauntlet_power.csv gauntlet_panel.csv

REM LFS_PATTERNS : genuine large BINARIES (deliverables) you DO want versioned;
REM   these go to Git LFS so file size is not a problem. Only binary/output
REM   types here - never source CSVs.
set LFS_PATTERNS=*.pdf *.docx *.pptx *.png *.jpg *.zip *.7z *.mp4 *.pkl *.npz *.h5
REM AUTO_LFS_BIG : also LFS any single file over ~99 MB whose type is not listed.
set AUTO_LFS_BIG=1

REM ---- BOARD (print-and-tape start map) --------------------------------------
set BUILD_BOARD=1
set BOARD_W=13
set BOARD_H=16
set BOARD_PLAYERS=2
set BOARD_SEED=56
set BOARD_HEX=20
set BOARD_PAPER=A4
REM BOARD_RES : 1 = stamp raw-material toppers, 0 = terrain only
set BOARD_RES=0
set BOARD_OUT=%LAB_DIR%\board_%BOARD_W%x%BOARD_H%_%BOARD_PLAYERS%p.pdf

REM ---- TACTICAL BOARD (one-sheet skirmish map) -------------------------------
set BUILD_TACTICAL=1
set TAC_W=9
set TAC_H=6
set TAC_SEED=26
set TAC_HEX=20
set TAC_OUT=%LAB_DIR%\tactical_%TAC_W%x%TAC_H%_s%TAC_SEED%.pdf
REM ---------------------------------------------------------------------------

if not exist "%CODE_DIR%" ( echo ERROR: %CODE_DIR% not found & pause & exit /b 1 )
if not exist "%LAB_DIR%" mkdir "%LAB_DIR%"
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

REM The selected data file is copied to renown_data.py so every script can just
REM "import renown_data" without knowing which variant is running.
cd /d "%CE_ROOT%"
if not defined DATA_SRC (
  echo ERROR: DIE=%DIE% has no matching DATA_%DIE% row in EDIT THESE.
  pause & exit /b 1
)
if not exist "%DATA_SRC%" (
  echo ERROR: %DATA_SRC% not found in %CE_ROOT%  ^(DIE=%DIE%^)
  pause & exit /b 1
)
copy /y "%DATA_SRC%" "renown_data.py" >nul

REM sheets\ scripts import renown_data from combatv4
set PYTHONPATH=%CE_ROOT%;%CODE_DIR%
set RENOWN_USE_LAST_RUN=%USE_LAST_RUN%
%PY% -c "import dice_config;print('    dice  ',dice_config.describe())"

%PY% -c "import renown_data,sys; sys.stdout.write(renown_data.VERSION)" > "%TEMP%\ce_ver.txt"
set /p VERSION=<"%TEMP%\ce_ver.txt"
del "%TEMP%\ce_ver.txt"

echo.
echo === build_all_CE : v%VERSION%  DIE=%DIE%  WHAT=%WHAT%  PLAYERS=%PLAYERS%  PUSH_REPO=%PUSH_REPO% ===
echo     data   %DATA_SRC%  -^> renown_data.py in %CE_ROOT%
echo     sheets %SHEET_DIR%
echo     maps   %MAP_DIR%
echo     out    %LAB_DIR%
echo.

REM ---- preflight -------------------------------------------------------------
REM Say what is missing ONCE, up front, rather than one traceback per script.
REM A half-ported folder is the normal state mid-migration; it should read as a
REM checklist, not a failure.
set MISSING=0
for %%F in (build_wiki.py wiki_markers.py worldtxt.py docx_tables.py gen_compendium.py patch_pursuit_domains.py build_compendium.py md_to_docx.py combat_sheet.py spec_tree_sheet.py playstyle_reference.py pursuit_tiles.py render_tree.py layout.json svg_to_pdf.py domain_board.py infra_board.py settlement_mats.py host_sheet.py generate_cards.py card_sheet.py card_copies.py reference_sheets.py equipment_sheet.py faction_sheet.py tactic_sheet.py) do (
  if not exist "%SHEET_DIR%\%%F" ( echo   MISSING  references\%%F & set MISSING=1 )
)
if not exist "%RULES_MD%" ( echo   MISSING  %RULES_MD% & set MISSING=1 )
if /i "%BUILD_LORE%"=="1" (
  for %%F in (renown_worldlore.py gen_cultures.py gen_intro.py gen_draft.py gen_pdf.py gen_book_json.py) do (
    if not exist "%LORE_DIR%\%%F" ( echo   MISSING  %DIR_LORE%\%%F & set MISSING=1 )
  )
)
for %%F in (hexmap.py mapgen.py hexgen.py build_board.py mapgen_regional.py region_presets.py gen.js app_shell.html build_mapapp.py) do (
  if not exist "%MAP_DIR%\%%F" ( echo   MISSING  mapgen\%%F & set MISSING=1 )
)
if "%MISSING%"=="1" (
  echo.
  echo   Port the above from Combatv3, then re-run. Steps whose files are
  echo   missing are skipped below rather than failing.
  echo.
)

if /i "%WHAT%"=="maps"  goto maps
if /i "%WHAT%"=="cards" goto cards
if /i "%WHAT%"=="docs"  goto docs
if /i "%WHAT%"=="wiki"  goto maps
if /i "%WHAT%"=="lore"  ( call :lore & goto end )
if /i "%WHAT%"=="all"   goto maps
echo Invalid WHAT=%WHAT% & goto end

REM ============================================================================
:maps
echo --- Map generator app ---
if not exist "%MAP_DIR%\build_mapapp.py" (
  echo   skipped - build_mapapp.py not ported
) else (
  pushd "%MAP_DIR%"
  REM --data pins the terrain table to CE's rules. Without it the app could
  REM ship D6 terrain effects with nothing on screen to say so.
  %PY% build_mapapp.py --data "%CODE_DIR%"
  popd
)
if /i "%WHAT%"=="maps" goto end

if /i "%BUILD_BOARD%"=="1"    call :board
if /i "%BUILD_TACTICAL%"=="1" call :tactical
if /i "%WHAT%"=="wiki" goto wiki

REM ============================================================================
:cards
echo --- Cards ---
pushd "%SHEET_DIR%"
if not exist "generate_cards.py" (
  echo   skipped - generate_cards.py not ported
) else if /i "%MODE%"=="both" (
  %PY% generate_cards.py renown "%OUT_DIR%" %PLAYERS%
  %PY% generate_cards.py escalation "%OUT_DIR%" %PLAYERS%
) else (
  %PY% generate_cards.py %MODE% "%OUT_DIR%" %PLAYERS%
)
popd
if /i "%WHAT%"=="cards" goto end

REM ============================================================================
:docs
echo --- Docs ---
pushd "%SHEET_DIR%"
echo   Compendium...
if exist "gen_compendium.py"        %PY% gen_compendium.py "%LAB_DIR%\compendium_data.json"
if exist "patch_pursuit_domains.py" %PY% patch_pursuit_domains.py "%LAB_DIR%\compendium_data.json"
if exist "build_compendium.py"      %PY% build_compendium.py "%LAB_DIR%\compendium_data.json" "%LAB_DIR%\Compendium.docx"
echo   Rules...
if exist "md_to_docx.py"            %PY% md_to_docx.py "%RULES_MD%" "%LAB_DIR%\Rules.docx"
echo   Combat quick-reference sheet...
if exist "combat_sheet.py"          %PY% combat_sheet.py "%OUT_DIR%\combat_sheet.pdf"
echo   Specialization trees...
if exist "spec_tree_sheet.py"       %PY% spec_tree_sheet.py "%OUT_DIR%\spec_trees.pdf"
echo   Playstyle reference...
if exist "playstyle_reference.py"   %PY% playstyle_reference.py "%OUT_DIR%\playstyle_reference.pdf"
echo   Pursuit ward-tiles...
if exist "pursuit_tiles.py"         %PY% pursuit_tiles.py "%OUT_DIR%\pursuit_tiles.pdf"
echo   Pursuit tech tree...
if exist "render_tree.py"           %PY% render_tree.py layout.json "%OUT_DIR%\pursuit_tree.svg"
if exist "svg_to_pdf.py"            %PY% svg_to_pdf.py "%OUT_DIR%\pursuit_tree.pdf" "%OUT_DIR%\pursuit_tree_p1.svg" "%OUT_DIR%\pursuit_tree_p2.svg"
echo   Domain standing board...
if exist "domain_board.py"          %PY% domain_board.py "%OUT_DIR%\domain_board.pdf"
echo   Infrastructure board...
if exist "infra_board.py"           %PY% infra_board.py "%OUT_DIR%\infra_board.pdf"
echo   Settlement board...
if exist "settlement_mats.py"       %PY% -c "import settlement_mats as s; s.build_board(r'%OUT_DIR%\settlement_board.pdf')"
if exist "settlement_mats.py"       %PY% settlement_mats.py "%OUT_DIR%\settlement_mats.pdf"
echo   Settlement board emulator (HTML)...
if exist "gen_settlement_board.py" %PY% gen_settlement_board.py --data %DATA_D10% --out "settlement_board.html"
echo   Host sheet...
if exist "host_sheet.py"            %PY% host_sheet.py "%OUT_DIR%\host_sheet.pdf"
popd

REM ============================================================================
:wiki
REM Lore first: build_wiki.py renders its Lore pages from world.txt, so the
REM text has to be regenerated before the wiki reads it.
if /i "%BUILD_LORE%"=="1" call :lore
echo --- Wiki ---
pushd "%SHEET_DIR%"
if not exist "build_wiki.py" (
  echo   skipped - build_wiki.py not ported
  popd
  goto pushrepo
)
if not exist "wiki_markers.py" (
  echo   skipped - wiki_markers.py not ported, build_wiki imports it
  popd
  goto pushrepo
)
if not exist "%RULES_MD%" (
  echo   skipped - %RULES_MD% not found
  popd
  goto pushrepo
)
rmdir /s /q "%LAB_DIR%\wiki" 2>nul
REM build_wiki searches ..\mapgen for renown-maps.html and copies it in as
REM maps.html; it notes and skips if the app was never built.
%PY% build_wiki.py %RULES_MD% "%LAB_DIR%\wiki"
if errorlevel 1 (
  echo   Wiki build FAILED - skipping repo push.
  popd
  goto end
)
popd
if "%PUSH_WIKI%"=="0" ( echo   Built wiki - wiki push skipped. & goto pushrepo )
if "%WIKI_REPO%"=="" ( echo   WIKI_REPO not set - wiki push skipped. & goto pushrepo )
if not exist "%WIKI_REPO%\.git" ( echo   WIKI_REPO is not a git repo - wiki push skipped. & goto pushrepo )
echo   Syncing into %WIKI_REPO% ...
for /d %%D in ("%WIKI_REPO%\*") do if /i not "%%~nxD"==".git" rmdir /s /q "%%D" 2>nul
for %%F in ("%WIKI_REPO%\*") do if /i not "%%~nxF"==".git" del /q "%%F" 2>nul
xcopy /e /i /y /h "%LAB_DIR%\wiki" "%WIKI_REPO%" >nul
pushd "%WIKI_REPO%"
%GIT% add -A
%GIT% commit -m "CE wiki rebuild v%VERSION% (%DIE%)" || echo   (nothing changed)
%GIT% push
popd

REM ============================================================================
REM  :pushrepo  - commit + (optional) tag + push the CE project to GitHub.
REM    Large-file handling so a fat tournament matchups.parquet in lab_out can't
REM    reject the push:
REM      IGNORE_BULK   -> gitignore + untrack the regenerable analysis output.
REM      LFS_PATTERNS  -> genuine large binaries (PDF/DOCX/PNG) go to Git LFS.
REM      AUTO_LFS_BIG  -> any stray file > ~99 MB is LFS'd as a backstop.
REM    This push is NON-destructive (no history rewrite). If a normal push is
REM    rejected for a large file that is ALREADY in history, that needs a
REM    history rewrite - use push_github.bat with FIX_HISTORY=1.
REM ============================================================================
:pushrepo
if not "%PUSH_REPO%"=="1" goto end
echo.
echo --- Push repo (v%VERSION%, DIE=%DIE%) -^> %REPO_DIR% ---
if not exist "%REPO_DIR%" ( echo   REPO_DIR %REPO_DIR% not found - skipping push. & goto end )

%GIT% lfs version >nul 2>&1
if errorlevel 1 (
  echo   Git LFS not installed ^(https://git-lfs.com^) - skipping repo push so a
  echo   large file can't be committed without LFS. Install once, then re-run.
  goto end
)

pushd "%REPO_DIR%"

REM init repo + origin on first run
if not exist ".git" (
  if "%REPO_REMOTE%"=="" ( echo   No repo here and REPO_REMOTE blank - skipping. & popd & goto end )
  echo   No repo in %REPO_DIR% - initialising -^> %REPO_REMOTE%
  %GIT% init
  %GIT% branch -M %REPO_BRANCH%
  %GIT% remote add origin %REPO_REMOTE%
)

REM --- keep bulk tournament output out of the repo -----------------------------
if "%IGNORE_BULK%"=="1" (
  if not exist ".gitignore" type nul > ".gitignore"
  REM sentinel line keeps this block from being appended twice on re-runs
  findstr /x /c:"# renown build - bulk output" ".gitignore" >nul 2>&1 || (
    echo.>> ".gitignore"
    echo # renown build - bulk output ^(regenerable tournament/analysis data^)>> ".gitignore"
    echo *.parquet>> ".gitignore"
    echo matchups*.csv>> ".gitignore"
    echo summary*.csv>> ".gitignore"
    echo tactic_matrix*.csv>> ".gitignore"
    echo loadouts_gen_*.csv>> ".gitignore"
    echo gauntlet_power.csv>> ".gitignore"
    echo gauntlet_panel.csv>> ".gitignore"
    echo # separate repo ^(GitHub Pages clone^) - keep out of the monorepo>> ".gitignore"
    echo RenownWiki/>> ".gitignore"
  )
  REM drop any bulk files committed before now from tracking (leaves them on
  REM disk). git expands the globs; --ignore-unmatch = no error if none match.
  %GIT% rm -r --cached --ignore-unmatch %BULK_PATTERNS% >nul 2>&1
)

REM --- route genuine large binaries (deliverables) to LFS ----------------------
%GIT% lfs install --local >nul
%GIT% lfs track %LFS_PATTERNS% >nul
if "%AUTO_LFS_BIG%"=="1" (
  for /f "delims=" %%F in ('%GIT% ls-files --others --modified --exclude-standard') do (
    set FSIZE=0
    if exist "%%F" set FSIZE=%%~zF
    if !FSIZE! GTR 99000000 (
      echo   large: %%F  ^(!FSIZE! bytes^) -^> LFS
      %GIT% lfs track "%%F" >nul
    )
  )
)

%GIT% add -A
%GIT% commit -m "v%VERSION% (%DIE%): %REPO_MSG%" || echo   (nothing to commit)

if "%REPO_TAG%"=="1" %GIT% tag -a v%VERSION% -m "%REPO_MSG%" 2>nul || echo   (tag v%VERSION% already exists - keeping it)

%GIT% rev-parse --abbrev-ref --symbolic-full-name @{u} >nul 2>&1
if errorlevel 1 ( %GIT% push -u origin HEAD:%REPO_BRANCH% ) else ( %GIT% push )
if "%REPO_TAG%"=="1" %GIT% push origin v%VERSION% 2>nul
popd

:end
echo.
echo Done. Press any key to close.
pause
endlocal
goto :eof

REM ============================================================================
REM  :board  - print-and-tape start map PDF into lab_out
REM ============================================================================
:board
echo --- Board ---
if not exist "%MAP_DIR%\build_board.py" (
  echo   skipped - build_board.py not ported
  exit /b
)
%PY% -c "import svglib" 2>nul || %PY% -m pip install svglib
set BOARD_FLAGS=
if /i "%BOARD_RES%"=="0" set BOARD_FLAGS=--no-resources
pushd "%MAP_DIR%"
%PY% build_board.py %BOARD_W% %BOARD_H% --seed %BOARD_SEED% --hex %BOARD_HEX% --paper %BOARD_PAPER% --param players=%BOARD_PLAYERS% %BOARD_FLAGS% --out "%BOARD_OUT%"
popd
echo   Board -^> %BOARD_OUT%
exit /b

REM ============================================================================
REM  :tactical  - one-sheet skirmish board into lab_out
REM ============================================================================
:tactical
echo --- Tactical board ---
if not exist "%MAP_DIR%\build_board.py" (
  echo   skipped - build_board.py not ported
  exit /b
)
%PY% -c "import svglib" 2>nul || %PY% -m pip install svglib
pushd "%MAP_DIR%"
%PY% build_board.py %TAC_W% %TAC_H% --tactical --seed %TAC_SEED% --hex %TAC_HEX% --paper %BOARD_PAPER% --out "%TAC_OUT%"
popd
echo   Tactical board -^> %TAC_OUT%
exit /b

REM ============================================================================
REM  :lore  - regenerate the world documents from renown_worldlore.py, and hand
REM    build_wiki.py the world.txt + map image it renders the Lore pages from.
REM    The gen_* scripts write bare filenames into the CWD, so this pushd's into
REM    LORE_DIR and copies the results out to LORE_OUT afterwards.
REM    Nothing here imports renown_data - the lore is dice-agnostic, which is why
REM    LORE_OUT is not tagged by DIE. CE keeps its OWN copy of renown_worldlore.py;
REM    drift from the Combatv3 copy is intentional and timestamped by the commit.
REM ============================================================================
:lore
echo --- Lore (world documents from renown_worldlore.py) ---
if not exist "%LORE_DIR%\gen_cultures.py" (
  echo   skipped - %DIR_LORE%\gen_cultures.py not ported
  exit /b
)
if not exist "%LORE_OUT%" mkdir "%LORE_OUT%"
REM Read by gen_pdf.py / build_docx.js (RENOWN_MAP) and by build_wiki.py
REM (WORLD_TXT / WORLD_MAP). Set explicitly so the wiki never falls back to its
REM parent-directory search and renders Combatv3's world.txt instead of CE's.
set RENOWN_MAP=%LORE_MAP%
set WORLD_MAP=%LORE_MAP%
set WORLD_TXT=%LORE_DIR%\world.txt
pushd "%LORE_DIR%"
%PY% gen_cultures.py
if errorlevel 1 echo   WARNING: gen_cultures.py failed - the wiki will render the previous world.txt.
if exist gen_intro.py %PY% gen_intro.py
if exist gen_draft.py %PY% gen_draft.py
if /i "%LORE_BOOK%"=="1" (
  if exist gen_pdf.py %PY% gen_pdf.py
  if exist gen_book_json.py (
    %PY% gen_book_json.py
    if exist build_docx.js node build_docx.js || echo   ^(node docx not installed - DOCX skipped^)
  )
)
for %%F in (world.txt world_design.txt intro.txt draft.txt book.json renown_world.pdf renown_world.docx) do (
  if exist "%%F" copy /y "%%F" "%LORE_OUT%\" >nul
)
popd
echo   Lore -^> %LORE_OUT%
exit /b