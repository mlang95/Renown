#!/usr/bin/env python3
"""generate_cards.py — one entry point for ALL card generation, driven entirely
by renown_data.py (the single source of truth).

Usage (notebook or CLI):
    from generate_cards import generate_cards
    generate_cards()                              # full Renown set -> ./cards/
    generate_cards(mode="escalation")             # Escalation subset
    generate_cards(out_dir=r"C:\\path", only=["tactics", "pursuits"])

    python generate_cards.py                      # mode=renown
    python generate_cards.py escalation ./cards_esc

What each mode produces:
    renown      pursuit cards for ALL 105 nodes, faction cards, tactic cards,
                equipment cards (weapons/ranged/shields/armor/retinues),
                infrastructure & wonders reference (if reference_sheets exposes it)
    escalation  pursuit cards for the 24-node combat subset, tactic cards,
                equipment cards. Factions/infrastructure are skipped (the
                Escalation Campaign doesn't use them).

Every deck regenerates from renown_data on each call — there is no caching and
no CSV input, so cards can never drift from the rules.
"""
import os
import sys

DECKS_RENOWN = ["pursuits", "factions", "tactics"]  # equipment folded onto pursuit cards
DECKS_ESCALATION = ["pursuits", "tactics"]  # equipment folded onto pursuit cards


def generate_cards(mode="renown", out_dir="cards", only=None, verbose=True, players=1):
    """Generate every card deck for `mode` ('renown' | 'escalation') into out_dir.

    only: optional list to restrict decks, e.g. ["tactics"] or
          ["pursuits", "equipment"]. Valid names: pursuits, factions,
          tactics, equipment.
    Returns a dict {deck_name: pdf_path} of everything written.
    """
    if mode not in ("renown", "escalation"):
        raise ValueError(f"mode must be 'renown' or 'escalation', got {mode!r}")
    decks = list(only) if only else (DECKS_RENOWN if mode == "renown" else DECKS_ESCALATION)
    os.makedirs(out_dir, exist_ok=True)
    suffix = "" if mode == "renown" else "_escalation"
    written = {}

    def _p(name):
        return os.path.join(out_dir, f"{name}{suffix}.pdf")

    if "pursuits" in decks:
        import card_sheet
        path = _p("pursuit_cards")
        card_sheet.make_pdf(path, mode=mode, players=players)
        written["pursuits"] = path

    if "factions" in decks:
        if mode == "escalation":
            if verbose:
                print("  (factions skipped — not part of the Escalation Campaign)")
        else:
            import faction_sheet
            path = _p("faction_cards")
            faction_sheet.make_pdf(path)
            written["factions"] = path

    if "tactics" in decks:
        import tactic_sheet
        path = _p("tactic_cards")
        tactic_sheet.make_pdf(path)
        written["tactics"] = path

    if "equipment" in decks:
        import equipment_sheet
        path = _p("equipment_cards")
        equipment_sheet.make_all_pdf(path)
        written["equipment"] = path

    if verbose:
        print(f"\n{mode}: {len(written)} deck(s) -> {os.path.abspath(out_dir)}")
        for k, v in written.items():
            print(f"  {k:10} {v}")
    return written


if __name__ == "__main__":
    _mode = sys.argv[1] if len(sys.argv) > 1 else "renown"
    _out = sys.argv[2] if len(sys.argv) > 2 else "cards"
    _players = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    generate_cards(mode=_mode, out_dir=_out, players=_players)
