#!/usr/bin/env python
# patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block)
# in a renown_data variant with the CULTURES block below. Idempotent.
# Usage:  python patch_cultures.py [renown_data_d10.py renown_data_d8.py ...]
#         (default: every renown_data_*.py variant found in the current folder)
import ast, glob, sys

BLOCK = r'''# CULTURES: the 15 worldlore cultures as playstyles (replaces PLAYSTYLES).
# Names/domains match renown_worldlore.CULTURES. Read by references/playstyle_reference.py.
# type      : pure | pair | triple | centre
# domains   : culture's domains, lead first (drives banner colours)
# monuments : Monument nodes (NODES type == 'Monument') - standing path is derived from their unlocks
# wonders   : keys of WONDERS
# actions   : "Action" or "Action: mode" - Action must be a key of ACTIONS
# factions  : keys of FACTIONS; every faction maps to at least one culture (duplicates allowed)
# radar     : relative emphasis 1-5 on the seven reference axes
CULTURES = {
    # ---- pure ----
    'Trusteki': {
        'type': 'pure', 'domains': ['Industry'],
        'monuments': ['Office of Works', 'Manor House', 'Advanced Blast Furnace'],
        'wonders':   ['Colossus', 'The Grand Exchange', 'The Great Basilica', 'High Chancery'],
        'actions':   ['Pursue', 'Repair', 'Build'],
        'factions':  ['The Verdant Kingdom', 'The Elder Grove', 'The Illuminated Order', 'The Hermit Crown'],
        'radar': {'military_solutions': 3, 'economy_generators': 5, 'faith_management': 3, 'doubt_warfare': 1,
                  'political_control': 3, 'board_presence': 3, 'degenerate_punishment': 2},
    },
    'Kraghs': {
        'type': 'pure', 'domains': ['Prowess'],
        'monuments': ['Royal Pavilion', 'Artillery Park', 'Ministry of Military Strategy'],
        'wonders':   ['Colossus'],
        'actions':   ['Move: Battle', 'Declare War', 'Demand Tribute'],
        'factions':  ['The Boundless Steppe', 'The Final Word', 'The Wandering Crown', 'The Ancient Wilds', 'The Winter Wolves'],
        'radar': {'military_solutions': 5, 'economy_generators': 1, 'faith_management': 3, 'doubt_warfare': 2,
                  'political_control': 2, 'board_presence': 5, 'degenerate_punishment': 4},
    },
    'Ithiss': {
        'type': 'pure', 'domains': ['Cunning'],
        'monuments': ["Thieves' Guild", 'Aristocratic Court', 'Outlaw Rookery', 'Outrider Intercept Post'],
        'wonders':   ['High Chancery'],
        'actions':   ['Raze', 'Foster Rebellion', 'Intercept Caravan'],
        'factions':  ['The Bandit King', 'The Crimson Tide', 'The Smoldering Crown'],
        'radar': {'military_solutions': 2, 'economy_generators': 3, 'faith_management': 1, 'doubt_warfare': 5,
                  'political_control': 3, 'board_presence': 2, 'degenerate_punishment': 5},
    },
    'Lenavorites': {
        'type': 'pure', 'domains': ['Piety'],
        'monuments': ['Papal Palace', 'Inquisitorial Palace'],
        'wonders':   ['The Great Basilica'],
        'actions':   ['Tithe', 'Send Missionaries', 'Spread Truth'],
        'factions':  ['The Sacred Throne', 'The Undying Flame'],
        'radar': {'military_solutions': 2, 'economy_generators': 3, 'faith_management': 5, 'doubt_warfare': 3,
                  'political_control': 3, 'board_presence': 1, 'degenerate_punishment': 3},
    },
    # ---- pairs ----
    'Belvareth': {
        'type': 'pair', 'domains': ['Piety', 'Prowess'],
        'monuments': ["Preceptory of the Knight's Templar", 'Royal Pavilion'],
        'wonders':   ['The Great Basilica', 'Colossus'],
        'actions':   ['Sacred War', 'Move: Battle', 'Spread Truth'],
        'factions':  ['The Bloodied Cross', 'The Blazing Standard', 'The Undying Flame', 'The Iron Faith'],
        'radar': {'military_solutions': 5, 'economy_generators': 2, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 2, 'board_presence': 3, 'degenerate_punishment': 2},
    },
    'Vorghith': {
        'type': 'pair', 'domains': ['Prowess', 'Cunning'],
        'monuments': ['Ministry of Military Strategy', 'Outrider Intercept Post'],
        'wonders':   ['Colossus', 'High Chancery'],
        'actions':   ['Pillage', 'Intercept Caravan', 'Move: March'],
        'factions':  ["The Squatters' Crown", 'The Winter Wolves', 'The Bandit King'],
        'radar': {'military_solutions': 4, 'economy_generators': 2, 'faith_management': 1, 'doubt_warfare': 4,
                  'political_control': 3, 'board_presence': 4, 'degenerate_punishment': 5},
    },
    'Drakteni': {
        'type': 'pair', 'domains': ['Prowess', 'Industry'],
        'monuments': ['Advanced Blast Furnace', 'Ministry of Military Strategy', 'Artillery Park'],
        'wonders':   ['Colossus'],
        'actions':   ['Move: Lay Siege', 'Build', 'Demand Tribute'],
        'factions':  ['The Battering Ram', 'The Yew Heart', 'The Sublime Gate', 'The Final Word'],
        'radar': {'military_solutions': 5, 'economy_generators': 4, 'faith_management': 2, 'doubt_warfare': 2,
                  'political_control': 3, 'board_presence': 4, 'degenerate_punishment': 2},
    },
    'Prezish': {
        'type': 'pair', 'domains': ['Cunning', 'Industry'],
        'monuments': ['Aristocratic Court', "Thieves' Guild", 'Manor House'],
        'wonders':   ['The Grand Exchange'],
        'actions':   ['Intercept Caravan', 'Sign Treaty: Trade Agreement', 'Negotiate'],
        'factions':  ['The Merchant Republics', 'The Gilded Path', 'The Grand Compact'],
        'radar': {'military_solutions': 2, 'economy_generators': 5, 'faith_management': 2, 'doubt_warfare': 4,
                  'political_control': 4, 'board_presence': 1, 'degenerate_punishment': 3},
    },
    'Shassolin': {
        'type': 'pair', 'domains': ['Cunning', 'Piety'],
        'monuments': ['Senate Hall', 'Inquisitorial Palace', 'Aristocratic Court'],
        'wonders':   ['High Chancery'],
        'actions':   ['Send Missionaries', 'Tithe', 'Destabilize'],
        'factions':  ['The Ashen Vale', 'The Smoldering Crown', 'The Forked Tongue'],
        'radar': {'military_solutions': 2, 'economy_generators': 2, 'faith_management': 4, 'doubt_warfare': 5,
                  'political_control': 4, 'board_presence': 1, 'degenerate_punishment': 5},
    },
    'Madekites': {
        'type': 'pair', 'domains': ['Piety', 'Industry'],
        'monuments': ['Office of Works', 'Papal Palace'],
        'wonders':   ['The Great Basilica', 'The Grand Exchange'],
        'actions':   ['Build', 'Pursue', 'Spread Truth'],
        'factions':  ['The Iron Faith', 'The Gilded Crescent', 'The Tunnellers', 'The Verdant Kingdom'],
        'radar': {'military_solutions': 3, 'economy_generators': 4, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 2, 'board_presence': 1, 'degenerate_punishment': 3},
    },
    # ---- triples ----
    'Cailendroffs': {
        'type': 'triple', 'domains': ['Piety', 'Prowess', 'Cunning'],
        'monuments': ['Imperial Palace', 'Royal Pavilion', "Preceptory of the Knight's Templar", 'Aristocratic Court'],
        'wonders':   ['Colossus'],
        'actions':   ['Sacred War', 'Declare War', 'Negotiate'],
        'factions':  ['The Crowned Star', 'The Entwined Crown', 'The Hermit Crown', 'The Bloodied Cross'],
        'radar': {'military_solutions': 4, 'economy_generators': 1, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 3, 'board_presence': 4, 'degenerate_punishment': 3},
    },
    'Sarkopekt': {
        'type': 'triple', 'domains': ['Cunning', 'Industry', 'Prowess'],
        'monuments': ['Outrider Intercept Post', 'Ministry of Military Strategy', 'Advanced Blast Furnace'],
        'wonders':   ['Colossus', 'The Grand Exchange'],
        'actions':   ['Move: Battle', 'Demand Tribute', 'Negotiate'],
        'factions':  ['The Broken Banner', 'The Sublime Gate', 'The Iron Shore'],
        'radar': {'military_solutions': 4, 'economy_generators': 4, 'faith_management': 1, 'doubt_warfare': 3,
                  'political_control': 3, 'board_presence': 4, 'degenerate_punishment': 4},
    },
    'Ossensteins': {
        'type': 'triple', 'domains': ['Cunning', 'Piety', 'Industry'],
        'monuments': ['Office of Works', 'Inquisitorial Palace'],
        'wonders':   ['The Grand Exchange', 'High Chancery'],
        'actions':   ['Tithe', 'Destabilize', 'Intercept Caravan'],
        'factions':  ['The Hall of Masks', 'The Forked Tongue', 'The Velvet Hand'],
        'radar': {'military_solutions': 1, 'economy_generators': 5, 'faith_management': 3, 'doubt_warfare': 4,
                  'political_control': 4, 'board_presence': 1, 'degenerate_punishment': 4},
    },
    'Voldrastel': {
        'type': 'triple', 'domains': ['Piety', 'Industry', 'Prowess'],
        'monuments': ['Senate Hall', 'Ministry of Military Strategy', "Preceptory of the Knight's Templar"],
        'wonders':   ['The Grand Exchange', 'The Great Basilica'],
        'actions':   ['Sign Treaty', 'Muster', 'Repair'],
        'factions':  ['The Iron Throne', 'The Grand Compact', 'The Pale Throne'],
        'radar': {'military_solutions': 3, 'economy_generators': 4, 'faith_management': 3, 'doubt_warfare': 1,
                  'political_control': 4, 'board_presence': 3, 'degenerate_punishment': 2},
    },
    # ---- centre ----
    'Astravantheliad': {
        'type': 'centre', 'domains': ['Piety', 'Prowess', 'Cunning', 'Industry'],
        'monuments': ['Senate Hall', 'Studium Generale'],
        'wonders':   ['High Chancery'],
        'actions':   ['Negotiate', 'Sign Treaty', 'End Treaty'],
        'factions':  ['The Dukedom', 'The Eternal Court', 'The Illuminated Order', 'The Luminous Court',
                      'The Inner Circle'],
        'radar': {'military_solutions': 2, 'economy_generators': 3, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 5, 'board_presence': 2, 'degenerate_punishment': 3},
    },
}
# FACTION_SUMMARIES: one-line gist of each FACTIONS mechanic, for reference sheets.
# Shown under the mechanic name; FACTIONS[...]['mechanic'] stays the binding text.
FACTION_SUMMARIES = {
    'The Verdant Kingdom':   'Gold per Craft level; no war or Cunning actions',
    'The Tunnellers':        'Mountains move as grassland; starts with a Mine',
    'The Elder Grove':       'Doubt +1; faster, Steady Armies; no Alliances',
    'The Boundless Steppe':  'Starts with a Stable',
    'The Final Word':        'Ignores At War Doubt and Influence modifiers',
    'The Wandering Crown':   'Armies are Settlements; no Infrastructure, no upkeep',
    'The Ancient Wilds':     'Slows invaders, ignores terrain; must accept first NAPs',
    'The Bandit King':       "Starts with Smuggler's Nook; controls a Bandit Camp",
    'The Crimson Tide':      'Immune to Intercept Caravan; starts with a Shipyard',
    'The Sacred Throne':     'Declaring War on you costs Doubt',
    'The Undying Flame':     'Faith from wars and heavy losses; Immune War Weariness',
    'The Bloodied Cross':    'Sacred War at Rising Piety, uncapped; no Convert',
    'The Blazing Standard':  "Starts with a Preceptory; must field 25 Knight's Templar",
    "The Squatters' Crown":  'Armies Occupy Settlements instead of holding them',
    'The Winter Wolves':     'No upkeep in at-war Territory; ignores Winter Speed',
    'The Battering Ram':     'Starts with Siege Works; must Siege new Citadels',
    'The Yew Heart':         'Ranged +1 to Strike; no heavy plate or shields',
    'The Merchant Republics':'All trade needs a Trade Agreement with you',
    'The Gilded Path':       "Starts with Artisan Workshop; can't refuse trade",
    'The Ashen Vale':        'Neighbours gain Doubt; Retinues have Poison',
    'The Smoldering Crown':  'Strong Cunning Envoys; no Alliances or Diplomacy',
    'The Iron Faith':        'Sieges against you +2 while Public Order 3+',
    'The Gilded Crescent':   'Starts with an Inn',
    'The Crowned Star':      "Chooses every Council Envoy's Domain; your Envoys -1",
    'The Entwined Crown':    'Once, force an Alliance; members gain Faith and Influence',
    'The Hermit Crown':      'Always Abstains; your Envoys cost double to sway',
    'The Broken Banner':     "Can't war or be warred on; allied to the highest bidder",
    'The Sublime Gate':      "Musters from Trade Partners' Pursuits",
    'The Iron Shore':        'Spoils win or lose; recoups lost Retinues',
    'The Hall of Masks':     "Takes another player's Faction each turn",
    'The Forked Tongue':     'Unlimited, contradictory Treaties',
    'The Velvet Hand':       'Rewards players who support your Envoys',
    'The Iron Throne':       "Starts with a Citadel; your Alliance can't Declare War",
    'The Grand Compact':     'Trade partners must join your war or cut trade',
    'The Pale Throne':       'Unwieldy, Panic-immune Armies; Public Order capped at 1',
    'The Dukedom':           'Hosts the game; attacking the Duke unites the table',
    'The Eternal Court':     'Banks Influence; up to 5 per Envoy in Zenith',
    'The Illuminated Order': 'Influence +1 per 3 Pursuits',
    'The Luminous Court':    'Civic Pursuits upgraded; no Craft Pursuits',
    'The Inner Circle':      "Allies' Envoys +1; may spend allies' Influence",
}
'''


def patch(path):
    raw = open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    src = raw.replace("\r\n", "\n")
    lines = src.split("\n")
    tree = ast.parse(src)
    tgt = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) in ("PLAYSTYLES", "CULTURES") for t in node.targets):
            tgt = node
            break
    if tgt is None:
        print(f"  {path}: no PLAYSTYLES/CULTURES block - skipped")
        return
    start, end = tgt.lineno - 1, tgt.end_lineno          # 0-based start, exclusive end
    i = tree.body.index(tgt)                               # extend over FACTION_SUMMARIES if it is the next statement
    nxt = tree.body[i + 1] if i + 1 < len(tree.body) else None
    if isinstance(nxt, ast.Assign) and any(getattr(t, "id", None) == "FACTION_SUMMARIES" for t in nxt.targets):
        end = nxt.end_lineno
    # absorb the block's own comment header (# PLAYSTYLE... / # CULTURES...) above the assignment
    j = start
    while j > 0 and not lines[j - 1].strip():
        j -= 1
    top = j
    while top > 0 and lines[top - 1].lstrip().startswith("#"):
        top -= 1
    if top < j and lines[top].lstrip().startswith(("# PLAYSTYLE", "# CULTURES")):
        start = top
    new = lines[:start] + BLOCK.rstrip("\n").split("\n") + lines[end:]
    out = "\n".join(new)
    ast.parse(out)
    open(path, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))
    print(f"  {path}: lines {start+1}-{end} replaced with CULTURES")


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob("renown_data_*.py"))
    for f in files:
        patch(f)
