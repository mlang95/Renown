# Wiki rules — restructure draft (proposal, not applied)

Goal: the wiki's Rules section should read front to back like a rulebook. You learn what you own, then
play one turn in order, and each subsystem is explained at the step where it first comes up.

## What's wrong now

- `build_wiki.py` turns every `#` / `##` heading of `RULES_push_simple.md` into one page and lists them all in
  one flat **Rules** nav group (~40 links). The file order is a reference order, not a play order.
- The turn is explained twice: briefly in **The Turn** (phase steps), then again in standalone chapters far
  away (Economy, Bandits, Public Order, Battles…). The step list never links to where each step is explained.
- Some rules sit far from what they govern:
  - Core Principle 13 (Mastery Chain) and 14 (Scope) are Holding rules but live in Core Principles.
  - *Rule: Commanding Presence* (Army movement) lives under Prowess Actions, not Armies.
  - Seasons and Timers come before Setup, but you need them only once the turn starts.
  - Domains & Standings comes after all the actions, although every Envoy and Council action reads Standing.
- The wiki has no prev/next order, so nothing tells you what to read next.

## Proposed reading order

Four parts. **Bold** = an existing section that moves; *(new)* = a short new linking page, no new rules.

### Part I — Before You Play
1. Introduction — Game Synopsis, How to Win (Edicts), Game Structure (Eras)
2. Reading These Rules
3. Core Principles — 1–12 and 14+; **13 Mastery Chain moves to Part II §8**
4. Setup — Table Setup, Setup Order, Ages, Player Setup

### Part II — Your Empire (what's on your board)
5. Resources
6. **Domains & Standings** — Domain Standings, Standing & Influence, Domain Identities & Traits
7. Settlements — Wards, Chartering, Reach, Hamlets
8. Holdings — **Mastery Chain (old Principle 13, incl. new 13.4 Build Timer rule)**, Scope (old 14), catalog link
9. Infrastructure
10. Territory & Terrain
11. **Armies** — Overview, Mustering, Blocked Armies, **Commanding Presence (moved from Prowess Actions)**

### Part III — Playing a Turn (in order)
12. The Turn — five-phase overview, the Host, **Seasons**, **Timers**
13. Empire Phase — the 9 steps; each step links to its detail page:
    - step 4 → **Bandits** (Outlaw Country, Spawning, Growing, Bandit Rules, Army Behavior)
    - step 5 → Influence (gain)
    - step 6 → **Economy**: Treasury & Upkeep, Trade & Income, Insolvency & Bankruptcy
    - step 7 → **Public Order**
    - step 8 → Endurance (stays inline)
14. Council Phase
15. Envoy Phase — Sending, Resolving, Envoy Resolution Table, Influence (spending)
16. Actions — one page per Domain **in resolve order**: Diplomacy → Prowess → Cunning → Piety → Industry
    - Diplomacy also carries **Diplomacy & Treaties** and **Vassalization**
17. Battle Phase — **Battles** (Beginning, Skirmish Steps, Ending, Tactic Matrix), **Siege Warfare**,
    Attacking a Bandit Camp
18. Rest Phase — Renown, Domain Points, Host change, and *(new)* "Winning": Edicts and Era advance (links back
    to How to Win)

### Part IV — Reference (unchanged content)
Holdings catalog · Equipment · Factions · Glossary · Index · the existing reference pages

## Wiki presentation changes (`build_wiki.py`)
- Nav: replace the flat Rules list with the four parts above, collapsible, opening on the current page's part.
- Prev / Next buttons on every rules page, following the reading order above.
- Breadcrumb on each page, e.g. *Playing a Turn › Empire Phase › Step 6 Income & Upkeep*.
- The existing ★ Turn Sequence page becomes Part III §12's landing page and links into each step.

## How it would be built (choose one)
- **A. Reorder `RULES_push_simple.md` itself (recommended).** Rules.docx and the wiki then share one order.
  Rule numbers are recomputed at render (`rule_numbers.py`), and `{{SEE:}}` / `GLOSSARY_SEE` use slug anchors,
  so cross-references survive. Old wiki URLs (`rules-<slug>.html`) keep their slugs.
- **B. Keep the file and add a `WIKI_ORDER` list in `build_wiki.py`.** Only the wiki changes and the docx keeps
  today's order, but the two documents drift apart.

## Open questions
1. A or B?
2. Should Core Principles stay up front (MTG style), or move to Part IV as reference?
3. Should Domains & Standings come before Settlements (as above) or after Armies?

## Found while drafting (not changed)
- `--check-rules` reports 1 mismatch: `GLOSSARY_SEE 'Presence' -> 'rule-presence'` doesn't resolve, because
  the heading is *Rule: Commanding Presence*. This was already failing before this change.
