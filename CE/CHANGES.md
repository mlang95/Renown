# Changes in this bundle

## Rule numbering
- **New file:** `references/rule_numbers.py`.
- **Hooked into:**
  - `md_to_docx.py`: numbers printed; `--no-numbers` turns them off.
  - `build_wiki.py`, `wiki_markers.py` and `gen_settlement_board.py`: prose stays unnumbered; `{{SEE:}}` prints as "N (Section)".
- **Source md stays unnumbered.** The board reads its headings verbatim.

**Scheme:**

| Element | Number |
|---|---|
| Chapter | `2` |
| Section | `2.4` |
| Rule | `2.4.2` |
| Child section | shares its parent's counter |
| Lettered sub-rule (list after a "…:" line, or a nested item) | `2.4.1a` |
| Italic lines | unnumbered |
| Appendices (Holdings, Equipment, Heritages) | `A` / `B` / `C` |

**Markers:**
- `{{RULE:id}}` at the end of a line anchors that rule.
- Every heading auto-anchors by its slug.
- `{{SEE:id}}` is a cross-reference.

**Checks:**
- `python rule_numbers.py ../RULES_push_simple.md --check`
- The same check also runs inside `gen_settlement_board --check-rules`.

**Build plumbing:**
- `build_all_CE.bat`: `rule_numbers.py` added to the preflight list.
- `CLAUDE.md`: marker table updated.

## GLOSSARY_SEE
- **`renown_data_d10.py`:** 87 terms, SIMPLE only.
  - The glossary row prints the first sentence plus "See N (Section)".
  - `GLOSSARY` keeps the full text for cards, board and `{{TERM:}}`.
  - A `(short, anchor)` tuple overrides the first sentence.
- **`docx_tables.see_definition`:** renders the rows.
  - An unresolved anchor prints the full definition and a warning.
- **Anchors added to the md:** host, council-envoy, vote, renown-track, mastery-chain, root, speed, seize, form-line, initiative, strike, defend, panic, fatigue, end-skirmish.

## Sub-step rewrites — `RULES_push_simple.md` (no timing changes)

| Section | Before | After | What merged |
|---|---|---|---|
| Empire Phase | 10 steps + 11 sub-steps | 9 steps, 0 sub-steps | Sub-step chains go inline. Taxes folds into the front of Income & Upkeep; order is unchanged. "Taxes step" in Income Types is renamed to match. |
| Council Phase | lead line + 3 steps + 2 trailing paragraphs | 3 steps | The redundant lead line is dropped. The auto-Abstain rule and the floor-of-1 rule (formerly an italic note) fold into step 3. |
| Envoy Phase | 4 steps + 2 sub-steps | 4 steps | Vote order folds into step 3. |
| Rest Phase | 6 steps | 4 steps | Renown + Domain Point become one Score step. "Start the next Empire Phase" is dropped. |
| Skirmish | 11 steps | 8 steps | Roll to Strike / Strike and defend / Strike back → Strike + Defend. Lose Endurance / Break check / Fatigue token → Fatigue. |
| Ending a Battle | — | — | The Spoils of War definition moves from an italic note into step 2. |

**Italic notes that are rules, now plain text (so they get numbered):**
- the Edict timer
- the Envoy would-be-fail rule
- Vassal mutual exchange
- Suzerain vassalized

**Wording:**
- "the defender with may Parry" → "a defender with Parry may Parry".
- "a natural 10 is a Riposte" → "a natural 10 Ripostes if the defender has Riposte". This matches the glossary. It is the only line whose rule reading changes.

**Not touched:** the board's hard-coded Empire checklist (`board/js/10_table.js` `empireChecklistHTML`) still lists Winter tax as its own line. Its order still matches.

## Validation
- **Parse:** all edited `.py` files parse cleanly.
- **Anchors:** `rule_numbers --check` reports OK.
- **Rules.docx:** renders, and converts to PDF (preview included; fallback font).
- **Wiki:** `wiki_markers` self-test has no unresolved markers. The full wiki builds with no `{{RULE:}}`/`{{SEE:}}` left in its HTML.
- **Board:** builds with no markers in its HTML.
  - `--check-rules`: 0 mismatches.
  - `parity_efx.js`: 13,853 checks, 0 differences.
  - Phase-step labels parse.
- **SIMPLE=0:** `GLOSSARY_SEE` is empty, so the legacy build is unchanged.
