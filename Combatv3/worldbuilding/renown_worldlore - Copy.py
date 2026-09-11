"""
renown_worldlore.py
====================
Structured world-lore data for Renown, derived from the four-domain simplex.

Governing rule: lore derives from mechanics, never invented alongside.
15 cultures = 4 heartlands + 6 pairs + 4 triples + 1 Generalist (center).

All strings are authored lore; import and reference as needed. This module is
data-only (no logic) so it can be consumed by generators, wikis, or docs.
"""

# ---------------------------------------------------------------------------
# DOMAINS — the master table. Each domain is one column of categorical choices.
# ---------------------------------------------------------------------------

DOMAINS = {
    "Prowess": {
        "core_value": "Glory",
        "org_form": "Warband",
        "government": "Kratocracy",
        "sacred": "War itself (deified) — combat is their god, glory-or-death is the sacrament",
        "belief_mode": "True believer (locked)",
        "source_of_authority": "Force / victory",
        "economy": "Plunder, tribute",
        "kinship_unit": "The band (allegiance)",
        "identity_theory": "You are who you serve",
        "succession": "Strongest takes",
        "attitude_to_change": "Present (glory-now)",
        "naming_grammar": "[name] of the [Warband]",
        "naming_example": "Dreg of the Clenched Fist",
        "affiliation_display": "Announced (loud, a banner); band nouns = weapons (Fist/Host/Blade)",
        "military_doctrine": "Open force / shock AND tactical (maneuver, discipline)",
        "settlement": "Fortified holds / warcamps OR nomadic",
        "land_scar": "Battlefields, barrows, ruins",
        "death_practice": "Glory-tombs, barrows",
        "taboo": "Retreat / cowardice",
        "defined_against": "The weak",
        "self_image": "The brave",
        "lore_voice": "Armies, fighting, captures, sacks, tribute",
        "lore_medium": "Written historical analysis (leadership, army mgmt, logistics, strategy, tactics, campaigns)",
        "consonants": ["g", "k", "b", "d", "r", "kh", "gh"],
        "phonology_signature": "Voiced stops + gutturals; blunt, hammered",
        "monuments": ["Royal Pavilion", "Ministry of Military Strategy"]
    },
    "Cunning": {
        "core_value": "Guile",
        "org_form": "Brotherhood (a.k.a. Syndicate)",
        "government": "Aristocracy",
        "sacred": "The game / process itself — addicted to the play; sabotage, theft, deception, blackmail are the sacraments. The False Prophet is a weaponized tool, not worshipped.",
        "belief_mode": "Doubter (can be atheist)",
        "source_of_authority": "Blood / leverage",
        "economy": "Extraction, racket, theft",
        "kinship_unit": "The brotherhood (hidden kin)",
        "identity_theory": "You are what you've done (concealed)",
        "succession": "Blood / intrigue",
        "attitude_to_change": "Opportunistic (cyclical)",
        "naming_grammar": "[name] [earned byname]",
        "naming_example": "Sliv Three-Knife",
        "affiliation_display": "Concealed (brotherhood never stated); byname is given by others (method/trait/deed)",
        "military_doctrine": "Ambush, asymmetric, sabotage",
        "settlement": "Warrens / hidden dens OR nomadic (roving)",
        "land_scar": "Smuggler-warrens, unmarked graves",
        "death_practice": "Erased, unmarked",
        "taboo": "Trust / being known",
        "defined_against": "The honest",
        "self_image": "The clever",
        "lore_voice": "Denial ('it never happened') OR victim mindset; never a straight confession — the telling is itself a con",
        "lore_medium": "Folklore & mystery (no records, only rumor/legend; deniable by nature)",
        "consonants": ["s", "sh", "z", "ts", "x"],
        "phonology_signature": "Sibilants + affricates; hissing; s->hard-stop sounds like a blade drawn",
        "monuments": ["Outlaw Rookery", "Thieves' Guild", "Outrider Intercept Post", "Aristocratic Court"]
    },
    "Industry": {
        "core_value": "Legacy",
        "org_form": "Craft",
        "government": "Democracy",
        "sacred": "The work / building / order (Peace) deified, or atheist",
        "belief_mode": "Doubter (can be atheist)",
        "source_of_authority": "Consent / competence",
        "economy": "Production, craft, trade",
        "kinship_unit": "The bloodline (inheritance)",
        "identity_theory": "You are your inheritance",
        "succession": "Vote / merit",
        "attitude_to_change": "Future (progress)",
        "naming_grammar": "[name] [craft-surname] [numeral]",
        "naming_example": "Frank Smith IV",
        "affiliation_display": "Lineage (surname) + generation numeral",
        "military_doctrine": "Tech, logistics, siege",
        "settlement": "Workshops, guildtowns",
        "land_scar": "Mines, workshops, scarred earth",
        "death_practice": "Interred by lineage, recorded",
        "taboo": "Waste / idleness",
        "defined_against": "The wasteful",
        "self_image": "The builders",
        "lore_voice": "Centuries refining the family's sacred inherited craft",
        "lore_medium": "Family oral tradition + statues, monuments, epitaphs (objects outlive the tellers)",
        "consonants": ["t", "p", "tr", "st", "kt", "pr", "ft"],
        "phonology_signature": "Voiceless stops + clusters; clipped, mechanical",
        "monuments": ["Manor House", "Office of Works"]
    },
    "Piety": {
        "core_value": "Devotion",
        "org_form": "Order",
        "government": "Ecclesiocracy (papacy)",
        "sacred": "The Tetramorph",
        "belief_mode": "True believer",
        "source_of_authority": "Divine mandate",
        "economy": "Tithe, alms",
        "kinship_unit": "The Order",
        "identity_theory": "You give the self up",
        "succession": "Chosen vessel",
        "attitude_to_change": "Past (tradition)",
        "naming_grammar": "St. [name] the [Order-adj]",
        "naming_example": "St. Paul the Brannochite",
        "affiliation_display": "Assumed — born name erased on joining; saint-name is a reused office, not a person",
        "military_doctrine": "Zealot, crusade",
        "settlement": "Monasteries / temple-towns OR nomadic (missionaries)",
        "land_scar": "Shrines, pilgrim-roads, relics",
        "death_practice": "Relics, sainted remains",
        "taboo": "Naming the self / pride",
        "defined_against": "The faithless",
        "self_image": "The saved",
        "lore_voice": "Unhinged, fervent zealotry ('insane shit')",
        "lore_medium": "Epistles & administrative documents (church bureaucracy; mania in dry official form is the horror)",
        "consonants": ["l", "m", "n", "th", "v", "soft-s"],
        "phonology_signature": "Liquids + nasals + soft fricatives; flowing, sung",
        "monuments": ["Papal Palace","Inquisitorial Palace"]
    },
}

# ---------------------------------------------------------------------------
# GODS / SACRED STRUCTURE — the four "gods" are not parallel deities.
# Each domain deifies its own activity; only Piety worships a literal god.
# ---------------------------------------------------------------------------

GODS = {
    "Esselantheum": {
        "title": "The God of Gods",
        "tier": "Blasphemously ABOVE the four greater deities",
        "nature": "Unreachable. To claim direct knowledge or access is blasphemy. Everywhere in the "
                  "world it is referred to only by the TITLE 'the God of Gods' — the true name is "
                  "unspeakable.",
        "the_name": "ESSELANTHEUM is spoken ONLY on Prophet's Landing. The false-religion cultures "
                    "say it aloud — saying it IS the sales pitch: 'we can name him, therefore we can "
                    "reach him.' This is why the name carries a Cunning sibilant inside Piety's "
                    "liquids: the only surviving pronunciation comes from con-men, shaped by their "
                    "tongue. THE ORTHODOX CANNOT CORRECT IT — to know the true name would itself be "
                    "blasphemy. The con-men's version is unchallengeable. That is the religion's "
                    "structural weakness in one word.",
        "tell": "A character who says 'Esselantheum' has been to Prophet's Landing or been converted "
                "by someone who has. The word is evidence.",
    },
    "Ollanenor": {
        "tier": "Greater deity — the GREATEST, of utmost power",
        "domain": "SAINTS",
        "nature": "Deliverer of saints' names. The most MYSTERIOUS of sects — an orthodoxy of power.",
        "seat": "The Inquisitorial Palace",
        "order": "The Inquisition",
    },
    "Anumaranth": {
        "tier": "Greater deity",
        "domain": "BALANCE",
        "nature": "Makes those who are empty WHOLE, and those who must be tithed, REDUCED. "
                  "The god of ADMINISTRATION.",
        "seat": "The Papal Palace",
        "order": "The Order of the True Word — the ultimate administrators, who attempt to record "
                 "EVERY POSSIBLE THING. People believe these documents will prove their truths. "
                 "(Recording everything inevitably records contradictions, lies told in good faith, "
                 "and errors — so the archive is simultaneously the most authoritative source in the "
                 "world and not actually reliable.)",
    },
    "Melvanar": {
        "tier": "Greater deity",
        "domain": "WRATH",
        "nature": "The most archaic and gothic. Self-flagellation. Spreads its message through the "
                  "REDUCTION OF FALSE GODS. Deliberately SOFT-SOUNDING name for a terrible god "
                  "(Galadriel principle) — the beauty is the disguise; it makes the fury worse.",
        "adherents": "The Drevghen — self-flagellating knightly crusaders defending the Lost Woods as "
                     "hallowed ground. TO SEE THEM IS TO KNOW UNMITIGATED ZEALOUS FURY. Taken by "
                     "Prowess cultures if they are pious.",
    },
    "Lorenthal": {
        "tier": "Greater deity",
        "domain": "PEACE",
        "nature": "The most ACCESSIBLE greater deity. Fixes the weather, brings good crops, keeps the "
                  "faithful safe from bandits and warbands. Spreads gospel through missionaries sent "
                  "throughout the world. Taken by Industry cultures if they are pious.",
    },
    "The False Prophet": {
        "tier": "Claimed GREATER DEMIGOD (not a god)",
        "nature": "Claims to be the MESSENGER of the God of Gods — not divinity, but ACCESS. You "
                  "cannot reach the God of Gods directly (blasphemy), but he can, and for a price he "
                  "will carry your message. A brokered-access racket. Cunning has no god of its own; "
                  "it arbitrages the belief market.",
        "seat": "Prophet's Landing",
    },
}

TETRAMORPH = {
    "faces": ["Ollanenor (Saints)", "Anumaranth (Balance)", "Melvanar (Wrath)", "Lorenthal (Peace)"],
    "function": "The four greater deities ARE the tetramorph (Revelation's four winged creatures) — "
                "four faces around the unreachable throne, standing between the faithful and the "
                "thing no one may approach. The pantheon has a SHAPE.",
    "inquisition_remit": "ONLY THE INQUISITION knows the name outside Prophet's Landing. Their central "
                         "motif is finding and eradicating those who know it — to PROTECT THE DIVINE "
                         "TETRAMORPH. Knowing the name means bypassing the four faces, which makes "
                         "them redundant: not sin, but STRUCTURAL COLLAPSE of the religion.",
    "inquisitors_burden": "They must know the name to recognize it. Every inquisitor holds the "
                          "blasphemy inside them and hunts others for exactly what they are.",
    "why_no_crusade": "A full crusade on Prophet's Landing would SPREAD the name — every soldier who "
                      "landed would hear it. Containment beats conquest. The tolerance of the false "
                      "church is STRATEGIC SILENCE, not weakness.",
}

DIVINITY_RULE = ("Some level of Piety is required for there to be a god. Belief is the substrate of "
                 "divinity; a god's power scales with worship. Gods can DIE if Piety drops — the Tombs "
                 "of the Old Gods are gods whose worshippers vanished, and the Great Basilica marks a "
                 "civilization whose faith died, and its gods with it. The False Prophet becomes "
                 "real-ish through belief: the con becomes true by being believed.")

PANTHEON_ADJACENCY = {
    "Prowess":  {"if_not_pious": "No god — IDOLATRY of war itself (a warrior-cult, not a church)",
                 "if_pious": "Melvanar (Wrath)"},
    "Industry": {"if_not_pious": "Atheist / the work",
                 "if_pious": "Lorenthal (Peace)"},
    "Cunning":  {"if_not_pious": "The game itself",
                 "if_pious": "The False Prophet — as a TOOL, not worship"},
    "Piety":    {"if_not_pious": "n/a",
                 "if_pious": "All four greater deities, by order"},
}

GOD_OPPOSITIONS = [
    ("Melvanar (Wrath)", "Lorenthal (Peace)",
     "The two OUTWARD-FACING deities — the ones non-Piety cultures adopt. Wrath/Peace maps onto the "
     "secular poles of war/work (Prowess/Industry)."),
    ("Ollanenor + Anumaranth", "(internal)",
     "The INTERNAL deities: they run the institutions (Inquisitorial Palace, Papal Palace). You only "
     "care about these if you are inside the church."),
    ("Ollanenor's Inquisition", "The False Prophet",
     "The Inquisition polices who may approach the God of Gods; the False Prophet's entire claim IS "
     "that blasphemy. He is their natural target — but see TETRAMORPH: containment beats conquest."),
    ("The Order of the True Word (Anumaranth)", "The papacy's denial",
     "The Order records EVERYTHING — including the lost dioceses, unpaid tithes, and the frontier "
     "that no longer answers. They did not set out to expose anything; they just wrote it down. The "
     "papacy's official denial and its own official archive are in direct contradiction."),
]

PIETY_STRUCTURE = {
    "form": "A papacy with TWO SEATS, not one. The Papal Palace (Anumaranth, Balance) runs "
            "administration; the Inquisitorial Palace (Ollanenor, Saints) runs orthodoxy and "
            "the Inquisition. Vessels are CHOSEN, not born.",
    "the_four_orders": "One order per greater deity — Melvanar (Wrath, self-flagellation), "
                       "Lorenthal (Peace, missionary), Anumaranth (Balance, administration — the "
                       "Order of the True Word), Ollanenor (Saints, orthodoxy of power — the "
                       "Inquisition). Together they are the TETRAMORPH: four faces guarding the "
                       "unreachable throne.",
    "the_false_prophet": "Not an antipope and not a rival god — a claimed GREATER DEMIGOD who "
                         "brokers ACCESS to Esselantheum. A schism of DISTANCE, not doctrine: he "
                         "arose past where the papacy's reach ended, and by the time the center "
                         "noticed, it was an institution.",
    "militant_orders": "Warrior-orders (crusade/Templar) concentrate in Piety×Prowess (the "
                       "Drevghen, serving Melvanar), NOT pure Piety. Pure Piety stays devotional, "
                       "administrative, and penitential.",
    "the_denial": "The papacy KNOWS AND DENIES that its edges have broken off — like an empire "
                  "unable to acknowledge it no longer governs far distant shores. To admit the "
                  "edges are gone is to admit the God of Gods' reach has limits. The Inquisition "
                  "therefore polices the STORY: the heresy is not the False Prophet's claim, it is "
                  "ACKNOWLEDGING HE IS OUT OF REACH.",
    "aesthetic": "OPEN (Tier 3) — gothic/enthroned possible; don't overbuild on one inspiration.",
    "schism_discipline": "Each Piety split-off names the ONE axis it broke over (which deity leads "
                         "/ how you reach the god / quiet vs armed / fixed vs revisable record), "
                         "inheriting ~90% of pure Piety.",
}


# ---------------------------------------------------------------------------
# REPUTATION MATRIX — relational, asymmetric. reputation[viewer][subject].
# Diagonal = self-image. Each viewer judges by its own value.
# ---------------------------------------------------------------------------

REPUTATION = {
    "Prowess": {  # judges by strength
        "Prowess": "the brave (self)",
        "Cunning": "cowards / snakes",
        "Industry": "soft / merchants",
        "Piety": "zealots (worthy or heathen)",
    },
    "Cunning": {  # judges by leverage
        "Prowess": "blunt tools",
        "Cunning": "the clever (self)",
        "Industry": "cheats / parasites",
        "Piety": "fools to exploit",
    },
    "Industry": {  # judges by productivity
        "Prowess": "wasteful destroyers",
        "Cunning": "marks to fleece",
        "Industry": "the builders (self)",
        "Piety": "worldly / greedy",
    },
    "Piety": {  # judges by faith
        "Prowess": "godly warriors OR savage heathens",
        "Cunning": "deceivers / the false (HERETIC — special venom, shared-god schism)",
        "Industry": "fanatics / bad-for-business",
        "Piety": "the saved (self)",
    },
}

# ---------------------------------------------------------------------------
# CULTURES — all 15. keyed by demonym. domains = frozenset of parent domains.
# ---------------------------------------------------------------------------

CULTURES = {
    # ---- Pure corners (singles) — culmination of all a domain's choices ----
    "Lenavorites": {
        "type": "pure",
        "domains": ["Piety"],
        "region": "Lenaveron",
        "identity": "A COLLECTION OF DIFFERENT ORDERS of varying styles of worship and devotion — one per "
            "greater deity: Melvanar (Wrath, self-flagellation), Lorenthal (Peace, missionary work), "
            "Anumaranth (Balance, administration, the Papal Palace — the Order of the True Word), "
            "Ollanenor (Saints, orthodoxy of power, the Inquisitorial Palace — the Inquisition). "
            "The ultimate administrators, record keepers, with an unhealthy dose of self-flagellation.",

    },
    "Kraghs": {
        "type": "pure",
        "domains": ["Prowess"],
        "region": "Draggath Wastes / Bleak Highlands",
        "identity": "Glory-or-death warband culture of the fractured wastes. Once the Great Monarchy "
                    "that held the whole continent; the Great Fractioning shattered it into perpetually "
                    "warring city-states and warbands. Now nomadic warbands + some static city-states, "
                    "perpetually training for inevitable conflict.",
    },
    "Shassith": {
        "type": "pure",
        "domains": ["Cunning"],
        "region": "Dreadwood + Marrow Shoals",
        "identity": "An ANARCHIC ARISTOCRACY comprised of BROTHERHOODS AND GUILDS that form CRIMINAL "
            "EMPIRES. A pirate/bandit haven — far more anarchy than anywhere else; no central "
            "authority, but a rigid internal hierarchy of the feared and successful. The game with "
            "no rules imposed on it.",
        "trade_relation": "Primary supplier of illegally sourced FENCED GOODS to the Sixteni, who "
                          "take them to market. Unscrupulous and conniving, willing to step over "
                          "anyone, moving stolen and illicit goods from Heathport to the Wharf of "
                          "St. Brannoch.",
    },
    "Trusteki": {
        "type": "pure",
        "domains": ["Industry"],
        "region": "Blighthold",
        "identity":  "A DEMOCRATIC REPUBLIC where occupation is passed down as INTELLECTUAL PROPERTY each "
            "generation as tradecraft. Generally cooperative, but the virtue is PROGRESS. The "
            "senate is chosen by most-aligned short- and long-term interests. All forms of "
            "occupation, all focused on MASTERY. Forged by surviving the Blight: they learned to "
            "repair the land rather than fight it, and that patient accumulated technique became "
            "their culture. 'Blighthold' is named for what it endured — and doubles as "
            "reverse-marketing (Greenland/Iceland) to keep people from coming.",
    },

    # ---- Pairs ----
    "Drevghen": {
        "type": "pair",
        "domains": ["Piety", "Prowess"],
        "region": "Lost Woods",
        "identity": "The Lost Woods crusader order, serving MELVANAR (Wrath). Prowess-weighted — warriors "
            "first, faith second: the militant killing edge that sounds more soldier than saint "
            "(the horror). Both protector (against the northern barbarians) and slaughterer (of "
            "its own pilgrims). Overtly, suspiciously devout — devotion curdled.",
    },
    "Vorghith": {
        "type": "pair",
        "domains": ["Prowess", "Cunning"],
        "region": "Vogen's Gallows (enclave)",
        "identity": "Guerrilla & economic-warfare warbands. They don't win pitched battles; they bleed "
                    "enemies — ambush, supply-line raids, trade sabotage, economic strangulation. Will "
                    "spend an entire campaign evading a fight while raiding and pillaging, winning by "
                    "refusing to be pinned. VOGEN = famous general who conquered up to the Bleak Highlands; "
                    "signature = public executions (hence Vogen's Gallows).",
    },
    "Drakteni": {
        "type": "pair",
        "domains": ["Prowess", "Industry"],
        "region": "Heathport / Drakenheart",
        "identity": "The YOUNGEST of cultures. They combine craft to make FIREPOWER and use it to expand "
            "beyond their continent — constantly building and funding new campaigns to make their "
            "mark. THEIR CRAFT IS CONQUEST. Siegemasters and professionally-equipped fighters.",

    },
    "Sixteni": {
        "type": "pair",
        "domains": ["Cunning", "Industry"],
        "region": "Bay of Pigs / Marrow Shoals",
        "identity": "The PIRATES, SMUGGLERS, BROKERS, MONEY-LENDERS and PROFITEERS of the world. They "
            "profit from deception, threat of force, sabotage, and blackmail. Also the greatest "
            "trade organization to ever exist — an OPEC-like cartel/guild-syndicate that controls "
            "markets, sets prices, and corners supply.",
    },
    "Shassolin": {
        "type": "pair",
        "domains": ["Cunning", "Piety"],
        "region": "Shallow Mire / Quiet Hollow",
        "identity": "The puppets and paupers of the Ossensteins. They are their own puppetmasters — "
            "manipulating the desperate and destitute, seeking converts, bringing in tithe and "
            "labor to fund and maintain the collective's lifestyle. THEY BELIEVE THEY ARE THE "
            "PUPPETMASTERS OVER THE POOR AND ARE UNAWARE OF THE OSSENSTEINS' INFLUENCE OVER THEM. "
            "Settlements that refuse the missionary work of the ORDER OF THE LAST PROPHET find "
            "curses and bad luck: poisoned wells, rot on crops, livestock slaughtered, plagues.",
    },
    "Madekites": {
        "type": "pair",
        "domains": ["Piety", "Industry"],
        "region": "Fair Whitewood",
        "identity": "Believe in the pain & sacrifice of building — labor as devotion, suffering as worship. "
                    "Hard tundra rich with quarries. Strive to raise the grandest cathedrals to recreate the "
                    "lost technology of the Great Basilica (the vanished Piety high-civilization's wonder). "
                    "Sacred masons chasing a lost golden age.",
    },

    # ---- Triples (Polymaths) ----
    "Cailendroffs": {
        "type": "triple",
        "domains": ["Piety", "Prowess", "Cunning"],
        "region": "Cailendroff Isles / Wharf of St. Brannoch",
        "identity": "Believers that their warband is led by the LAST REMAINING BLOODLINE of the last "
            "monarch of the Draggath Empire, and that the Draggath Wastes must be united under one "
            "banner — his. Exiled during the Great Fracture, they have never had the means to "
            "return, the harder now with Sarkazekt free companies patrolling the Sea of Damnation, "
            "never knowing who they work for. They are unsure even of the Voldrastel, who are "
            "rumoured to hold the CAILENDROFF EDICT blasphemy to both gods and men. So they use "
            "piety and cunning to generate loyalists and recruits — growing the warband's size, "
            "skill base, and economic standing toward a FINAL CRUSADE to reunite the Kraghs under "
            "their true king, the Draggath dynasty.",
    },
    "Sarkazekt": {
        "type": "triple",
        "domains": ["Cunning", "Industry", "Prowess"],
        "region": "Free-company node network, no homeland: NE Vaelohk, Ivory Isle, Bleak Highlands, Dead "
            "Waters, Wharf of St. Brannoch, Bay of Lost Hope, Quiet Hollow, Cailendroff Isle.",
        "identity": "MERCENARY CITY-STATES and BORDER PRINCES. For-hire, for-profit arms dealers and "
                "mercenaries — MERCHANT KINGS AND WARLORDS. Well-armed, well-trained, will use any "
                "tactic that gives an edge. The military-industrial-complex triple: Industry makes "
                "the arms, Cunning deals/schemes, Prowess fields them. They hold no homeland — a "
                "NETWORK OF NODES threaded through others' territory, because a war-market culture "
                "must be wherever its customers are. They built or sold the shipyard behind the "
                "Pincer of Dead Waters — the warlord did not develop a capability, he BOUGHT one.",
    },
    "Ossensteins": {
        "type": "triple",
        "domains": ["Cunning", "Piety", "Industry"],
        "region": "Prophet's Landing",
        "identity": "A very old, UNKNOWN faction — the oldest and wealthiest families, who pull the purse "
            "strings of most macroeconomic events. No one knows where they occupy, who they are, "
            "how wealthy they are, or how many are associated. Believed to own MORE THAN HALF THE "
            "WEALTH OF VAELOHK, the Dukedom included. ORIGIN: the original and most successful "
            "Trusteki families, who turned to trade, met the Shassolin and the Sixteni, and formed "
            "a secret network dedicated to world power without ever being known.",

    },
    "Voldrastel": {
        "type": "triple",
        "domains": ["Piety", "Industry", "Prowess"],
        "region": "The Twelfth Reach (12 islands)",
        "role": "Neutral defenders of the trade routes and seas — safe passage and honest brokering as an "
            "intermediary, for a toll and a broker's fee. The stoic wardens of the world's roads and "
            "sea routes: powerful, and wielded for good.",
        "identity": "The MORAL AUTHORITY and the direct ANTAGONIST OF THE SIXTENI. Heroes to others for "
            "guaranteeing safe passage and access to trade. A faithful, defensive, neutral-good "
            "arbiter of the trade routes — sincere all the way down (no Cunning = no con; the "
            "honest counterpart to the Cailendroff pretenders). Piety=principle, Industry=the "
            "routes, Prowess=defensive might.",
    },

    # ---- Center / Generalist ----
    "Astravantheliad": {
        "type": "center",
        "domains": ["Piety", "Prowess", "Cunning", "Industry"],
        "region": "Vaelohk (the center island)",
        "identity": "A uniquely blended MELTING POT where all ideas can be explored and pursued fully, "
            "honestly, and TESTED RIGOROUSLY. Every citizen carries all four domains at a baseline: "
            "basic military training and athleticism (Prowess), familiarity with and recognition of "
            "the tetramorph (Piety), adept craftsmanship and trade (Industry), and the capability "
            "to get themselves out of jams (Cunning). But their true character is "
            "HYPER-INTELLECTUAL: perpetually studying, seeking the truth. Most are scribes, "
            "researchers, and academics aligned to an ACADEMIC HALL. SPECIALIZATION CONTRAST: the "
            "Trusteki master an industry; the Astravantheliad spend an entire lifetime solving A "
            "SINGLE SMALL ISSUE within the greater field of their niche Hall. Their sacred is "
            "influence/proximity to power — because their work is the most THEORETICAL, and "
            "influence is the only mechanism by which an idea leaves the Hall and becomes real.",
            
        "governance": "An academically led TECHNOCRACY focused on myopic, specific problems, each citizen "
              "dedicating a whole life to one pursuit. Those with the best outcomes and greatest "
              "products are VOTED INTO THE TECHNOCRATIC SENATE that takes court with the Duke, "
              "representing the most influential members of Vaelohk.",
        "diplomatic_role": "The PRIMARY DELEGATES other cultures interact with during envoys and "
                   "diplomatic negotiation. Even when not participating, they are at the center of "
                   "influence. Knowledge is indeed power.",
    },
}


ASTRAVANTHELIAD_PARADOX = {
    "internal_self_image": "A rigorous, honest, meritocratic research culture. Every citizen "
                           "competent across all four domains. Lifetimes devoted to genuine problems "
                           "at extraordinary resolution. Knowledge as devotion; truth-seeking as the "
                           "highest calling. FROM INSIDE: the Age of Influence is the age REASON "
                           "FINALLY GOVERNS.",
    "external_reputation": "Vain, hollow, produces nothing. Their work is the most THEORETICAL — "
                           "from outside, a lifetime spent on something that never touches the "
                           "ground. The output is real, but it is abstraction, and abstraction is "
                           "invisible to everyone outside the Hall. FROM OUTSIDE: the Age of "
                           "Influence is the age NOBODY DOES ANYTHING.",
    "why_illegible": "Every domain judges by its own value (strength, productivity, leverage, "
                     "faith). By ALL FOUR of those measures, a lifetime of theoretical work scores "
                     "near zero. Their genuine excellence is illegible to everyone not inside it.",
    "domain_objections": {
        "Kraghs (Prowess)": "Will not accept a refinement on their FIGHTING STANCE. Glory is earned "
                            "in the doing; a theorist correcting your form has never bled for it.",
        "Trusteki (Industry)": "Will not deviate from INHERITED TRADE SECRETS on the say-so of a "
                               "detached academic proving a refinement THE FAMILY HAS NOT FOUND ON "
                               "ITS OWN. If it was not earned through the lineage, it is not "
                               "legitimate.",
        "Shassith (Cunning)": "Do not believe the Astravantheliad know anything about business — and "
                              "DESPISE their use of cunning for more than amoral purpose. Guile in "
                              "service of TRUTH is a category error; cunning is for advantage, not "
                              "for knowing.",
        "Lenavorites (Piety)": "Great tension with these BARELY BELIEVERS who, in Lenavorite eyes, "
                               "hold themselves TOO CLOSE TO THE DEITIES — and whose record-keeping "
                               "is antithetical, because the Astravantheliad REVISE THEIR RECORDS "
                               "when new evidence is discovered. Not impiety but IMPERTINENCE: "
                               "treating the sacred as a subject rather than a superior. They study "
                               "the tetramorph rather than submit to it — an audit of God.",
    },
}

ARCHIVE_OPPOSITION = {
    "The Order of the True Word (Anumaranth)": "FIXED, sacred, complete. The record is holy BECAUSE "
                                               "it does not change — a permanent accounting, an act "
                                               "of devotion. To revise is to admit the word lied.",
    "The Academic Halls (Astravantheliad)": "REVISABLE, provisional, correct-for-now. The record is "
                                            "honest BECAUSE it changes with evidence.",
    "the_conflict": "To a Lenavorite, a revisable record is the MUTABLE WORD — a record that lies "
                    "today about what it said yesterday — and it implies TRUTH ITSELF CHANGES, which "
                    "touches the divine.",
}

# ---------------------------------------------------------------------------
# TIMELINE — the reckoning.
#
# UNIT: 1 year = one full Trusteki agricultural cycle. Industry defines the
# measure; Piety (the Order of the True Word) later keeps the tally. Different
# domains own the unit and the count.
#
# YEAR 0 = THE GREAT FRACTIONING. Everything prior is negative.
#
# AGES ARE GRADIENTS, not hard boundaries — same principle as the geography.
# The start years below are the dates the True Word RECORDS, not the moment
# anything actually changed. Ages are declared retroactively; nobody living
# through the Fractioning knew it ended one.
#
# PROVISIONAL — nothing is written in stone yet.
# ---------------------------------------------------------------------------

TIMELINE = {
    "unit": "One year = one full Trusteki agricultural cycle.",
    "epoch": "Year 0 = The Great Fractioning.",
    "gradient_rule": "Age boundaries are ranges, not points. Recorded start years are the "
                     "True Word's reckoning, assigned in hindsight.",
    "present": "~4570s–4580s. Mid Age of Influence, a generation or two in.",

    "age_starts": {
        "Prowess":   0,
        "Industry":  1352,
        "Piety":     1942,
        "Cunning":   3066,
        "Influence": 4516,
    },
    "age_lengths": {
        "Prowess":   1352,
        "Industry":  590,      # SHORTEST — the Age of solving a problem. Once the
                               # Blight is endured, prosperity does not sustain an
                               # Age; it only enables the next one's excess.
        "Piety":     1124,
        "Cunning":   1450,     # LONGEST — ~50 generations under an internal
                               # inquisition. The Age that shaped the present most.
        "Influence": "ongoing",
    },

    # ===================== THE AGE OF THE OLD GODS (pre-0) =====================
    # Known only through pious ORAL tradition — the pre-administration age.
    # The old gods brought four peoples together into the four corners of the earth.
    "old_gods_era": {
        "dating": "~-3000s onward. No firm reckoning; the True Word records it as before "
                  "the count.",
        "premise": "The old gods brought four peoples into the four corners of the world.",
        "the_four_foundings": {
            "Trusteki": "Formed as FARMERS worshipping the old deity TRUSTI, in the old "
                        "continent of the ancient Coloured Mountains.",
            "Draggath": "Formed as WARRIORS under the Draggath Monarchy — eager expansionists "
                        "following the monarch's commands, believing the monarch to be the ear "
                        "and WARRIOR-PROPHET of the old god CAILEN.",
            "Shassith":  "Far south-west. Nomadic and sparse, incapable of trusting one another "
                         "and REJECTING the old god that brought them together, CLYPSO. Built "
                         "UNDERGROUND CITIES against an inhospitable land, and used the network "
                         "to travel in secret — finding and controlling natural chokepoints such "
                         "as the CRAG PASS (narrow paths, labyrinths, slot canyons).",
            "Lenavorites": "South-east. Worshipped the old gods fervently, forming a tradition of "
                           "BARE SUSTENANCE and the appeasement of the deities of old.",
        },
        "the_slow_expansion": {
            "Trusteki": "Grew beyond subsistence farming, passing knowledge down as ORAL "
                        "TRADITION through family lines. A peaceful people who traded fairly and "
                        "easily to raise everyone's quality of life — which let them learn "
                        "advanced technique quickly: animal husbandry, the SHIP, baggage carts "
                        "for long travel. This brought them to Crag Pass, and taught them the "
                        "dangers of the south.",
            "Draggath": "At its ZENITH. The land itself named for Draggath — a land of plenty, "
                        "easy to farm, much time spent training for war in coliseums, training "
                        "grounds, and grand tournaments. The largest empire in the known world, "
                        "barred only by natural obstacle: the southern Lost Woods and the SEA OF "
                        "DRAKES (named for the folklore of it destroying ships that tried to "
                        "cross).",
            "Shassith": "Some, seeing the bounty taken in ambushes on Trusteki caravans, believed "
                        "life could be improved — and ventured north through the Marrow Shoals "
                        "and Crag Pass to learn a new way of life.",
            "Lenavorites": "After hundreds of generations of pious worship in the great basilicas "
                           "of their time — and generations of poverty, starvation, and "
                           "self-mortification — SEEDS OF DOUBT formed. The old gods' names faded "
                           "into quietude. They migrated north and west from the frozen tundra "
                           "and named the land after themselves: LENAVERON — the FIRST WRITTEN "
                           "RECORD in the world. The old gods were forgotten in the desolate "
                           "tundra; graveyards and basilicas left to crumble.",
        },
        "consequence": "Those crumbling basilicas become the TOMBS OF THE OLD GODS. The old gods "
                       "died of ABANDONMENT — the divinity rule demonstrated in the world's own "
                       "prehistory, by the very people who would later invent the papacy.",
    },

    # ===================== YEAR 0 =====================
    "year_zero": {
        "event": "THE GREAT FRACTIONING",
        "content": "The Draggath Empire suddenly collapsed. A GREAT STORM came, changing the "
                   "geography of the entire world over the course of several generations. "
                   "North-west: disease and blight. South-west: a bountiful land — tall forests, "
                   "tropical islands teeming with plenty. South-east: mire, a faint reminder of "
                   "the land of the old gods. North-east: desolate wasteland, crumbling the "
                   "Empire's reach into civil war over the last dying flora and fertile soil.",
        "untouched": "The only land that remained untouched was the LOST WOODS, where a small "
                     "sect of Lenavorites migrated, never to return.",
        "note": "Year 0 is the storm's onset; the transformation took several generations.",
    },

    # ===================== THE FIVE AGES =====================
    "events": [
        # ---- AGE OF PROWESS (0–1352) ----
        {"year": 0, "age": "Prowess",
         "event": "The Great Fractioning. Draggath falls."},
        {"year": "0–~200", "age": "Prowess",
         "event": "Geography transforms over several generations. Lenavorites build simple rafts "
                  "and flee west — naming the STRAIT OF SORROW, as many and most fell ill on the "
                  "journey and died, only to find a worse swampy wetland to settle, inhabited by "
                  "bandits and conmen of the immoral kind."},
        {"year": "0–~400", "age": "Prowess",
         "event": "The Shassith leave their underground cities as the climate changes."},
        {"year": "0–1352", "age": "Prowess",
         "event": "THE CIVIL WAR  — the primary motif of the timeline, but "
                  "not the only thing happening. RECURSIVE SCARCITY: the more they fought over "
                  "the lessening fertile land, the less fertile land there was to fight over, and "
                  "the more they had to fight to claim it. Trusteki and Lenavorites migrate "
                  "throughout."},
        {"year": "0–1352", "age": "Prowess",
         "event": "The Trusteki endure the BLIGHT, using ancient trade secrets to grow crops in "
                  "the heath of what was soon dubbed BLIGHTHOLD, working together to survive the "
                  "diseased land."},
        {"year": 1136, "age": "Prowess", "provisional": True,
         "event": "VOGEN leads a warband to control everything up to the Bleak Highlands. His "
                  "signature: assassinating opponents by PUBLIC EXECUTION — the method that names "
                  "VOGEN'S GALLOWS. (A civil-war general, not a Cunning-age warlord: the site "
                  "carries his name for ~3,400 years to the present.)"},

        # ---- AGE OF INDUSTRY (1352–1942) ----
        {"year": 1352, "age": "Industry",
         "event": "AGE BEGINS — from the proliferation of the SCARLET FOREST, the migration to "
                  "Blighthold from the Coloured Mountains, and the general capacity to move at "
                  "sea."},
        {"year": "~1352", "age": "Industry",
         "event": "The soil south of Blighthold turns blood red; SCARLET TREES grow from it. A "
                  "verdant swelling — trees reaching the size of the old wood of Fair Whitewood "
                  "within a single generation. The Trusteki's skill lets them survive and REPEL "
                  "the blight."},
        {"year": "1352–1942", "age": "Industry",
         "event": "THE MIGRATIONS. Some Trusteki, not stalwart, move north seeking religion in "
                  "the wintery forested mountain pass of FAIR WHITEWOOD. Others build ships and "
                  "flee east, finding a natural port dubbed HEATHPORT with plentiful mines. "
                  "Others venture south to the archipelago of the MARROW SHOALS, meeting the "
                  "fleeing Shassith coming from the south, seeking another way of life."},
        {"year": "1352–1942", "age": "Industry",
         "event": "THE UTOPIA. Survival and cooperative spirit propel the Trusteki into a great "
                  "utopia — far from perfect. Wealth eventually outpaces meaning; criminality and "
                  "indulgence follow."},

        # ---- AGE OF PIETY (1942–3066) ----
        {"year": 1942, "age": "Piety",
         "event": "AGE BEGINS. Lenavorites are scattered in tiny ABBEYS, PRIORIES and "
                  "MONASTERIES, forming many small orders. These begin combining into larger and "
                  "larger administrative bodies IN THE SEARCH OF TRUTH. Rises as a response to "
                  "the excess and over-indulgence of the Industrial utopia."},
        {"year": "~1942–2100", "age": "Piety",
         "event": "THE UNIFYING FORCE. The FOUR GODS are recorded — Ollanenor, Anumaranth, "
                  "Melvanar, Lorenthal. THE PAPACY BEGINS at this moment. Mission work starts as "
                  "a COLLECTIVE movement."},
        {"year": "~2100", "age": "Piety",
         "event": "THE INQUISITION appears — mostly IDLE AND SYMBOLIC. As proof of the absence of "
                  "any other false gods, they do nothing."},
        {"year": "2100–3066", "age": "Piety",
         "event": "Peak reach. The Drevghen take the Lost Woods as hallowed ground; the WHEAT "
                  "FIELDS become a permanent battlefield. The bureaucracy doubles, and doubles "
                  "again."},
        {"year": 2910, "age": "Piety (toward Cunning)", "provisional": True,
         "event": "THE PINCER OF DEAD WATERS. A Prowess warlord raises a single disposable "
                  "shipyard (bought from the Sarkazekt) on the then-unnamed northern bay; the "
                  "main host drives south from the north while the flotilla lands on the "
                  "defenders' flank and rear. The most successful assault on the Lost Woods to "
                  "date — 156 years before the papacy's edges break. A visible crack in the "
                  "church's invulnerability. (The Drevghen call that day a massacre.)"},

        # ---- AGE OF CUNNING (3066–4516) ----
        {"year": 3066, "age": "Cunning",
         "event": "AGE BEGINS. Consolidating the small orders into one papacy required declaring "
                  "who stood OUTSIDE it. EXCOMMUNICATIONS for failing to recognize the "
                  "tetramorph — and the excommunicated go somewhere."},
        {"year": "~3066+", "age": "Cunning",
         "event": "THE FALSE GOD MANIFESTS ON PROPHET'S LANDING, among the excommunicated. A "
                  "schism of DISTANCE as much as doctrine — out past where the papacy's reach "
                  "ended. By the time the center noticed, it was an institution."},
        {"year": "~3100+", "age": "Cunning",
         "event": "THE INQUISITION SEIZES GOVERNMENT. It began as a response to stifle the False "
                  "Prophet. The papacy is reduced to COLLECTION AND ADMINISTRATION — Anumaranth's "
                  "Order of the True Word still records everything and rules nothing. The "
                  "Inquisition rules. The religion turns GOTHIC HORROR: a timeline of hysteria "
                  "and control."},
        {"year": "3100–4516", "age": "Cunning",
         "event": "THE PARANOIA ENGINE. The Inquisition keeps growing and preys on its own "
                  "people, ever more suspicious that the LENAVORITES THEMSELVES are converting to "
                  "the False Prophet. The threat is unfalsifiable (conversion is internal), so "
                  "the work can never conclude. Suspicion → confession → proof → more suspicion. "
                  "Worse: every purge EXILES converts to Prophet's Landing, manufacturing the "
                  "thing it fears. Free recruitment for the false church, funded by the "
                  "orthodoxy's own fear."},
        {"year": "3100–4516", "age": "Cunning",
         "event": "THE OSSENSTEINS — little-known until now — FUND AND PROPEL the False Prophet's "
                  "word, as a matter of PROFIT and of CONTROL OVER THEIR OWN PEOPLE. A cartel "
                  "that invented a church to keep its workforce obedient."},
        {"year": "~3300+", "age": "Cunning",
         "event": "THE EDGES BREAK OFF. The papacy's administration crumbles under its own size — "
                  "not completely, but the frontier shears away. Distant dioceses stop answering. "
                  "The Shassolin were not infiltrators: they WERE church administrators and "
                  "missionaries on the frontier when the connection to the center failed — "
                  "abandoned and repurposed. Criminals and Machiavellians climb the cracks into "
                  "ARISTOCRATIC power. THE PAPACY KNOWS AND DENIES."},
        {"year": "3300–4516", "age": "Cunning",
         "event": "THE REIGN OF THE PUPPETMASTERS. Raiders and piracy flourish in ungoverned "
                  "water. Chaos as DECENTRALIZATION, not apocalypse."},

        # ---- AGE OF INFLUENCE (4516–present) ----
        {"year": 4516, "age": "Influence",
         "event": "THE RETURN TO POWER. Stable tension after the dramatic ages — a perfect balance "
                  "of power and everyone's motivations within it. (The start date is CONTESTED: "
                  "the Astravantheliad argue it began earlier; the True Word insists on the "
                  "recorded year, and revising it would be blasphemy.)"},
        {"year": "~4570s–4580s", "age": "Influence",
         "event": "NOW. A generation or two in. History has stopped; the board is set."},
    ],

    # ===================== CONSEQUENCES OF THE RECKONING =====================
    "implications": {
        "cailendroff_arithmetic": "Draggath fell at Year 0. The pretender claims descent across "
                                  "~4,570 years. Not merely unprovable — ABSURD on its face, and "
                                  "believed anyway. No bloodline is traceable across that gap, "
                                  "which is exactly why the claim survives: it cannot be "
                                  "disproven any more than it can be proven.",
        "cailen_and_cailendroff": "The Draggath monarch was the ear and warrior-prophet of the "
                                  "old god CAILEN. The pretender's people are the CAILENDROFFS. "
                                  "The claim may not be descent from a king but from the "
                                  "PROPHET-LINE OF A DEAD GOD.",
        "draggath_the_word": "Draggath is land, empire, monarchy, dynasty, and the last monarch — "
                             "fully synonymous. The oldest and most enduring single word in the "
                             "world's history and future. To claim Draggath's line is to claim "
                             "THE WORD ITSELF.",
        "shassith_founding_refusal": "The Shassith's founding act was REJECTING Clypso, the god "
                                     "who brought them together. That is why Cunning is "
                                     "permanently a doubter domain.",
        "who_keeps_the_calendar": "The Order of the True Word maintains the reckoning — so the "
                                  "papacy DATES the world even where it no longer GOVERNS it. "
                                  "Prophet's Landing presumably keeps its own count.",
        "ages_declared_retroactively": "Nobody knew the Fractioning ended an Age; they thought it "
                                       "was a bad decade.",
        "lenavorite_temperament": "Self-flagellation and weaponized guilt are not ancient "
                                  "tradition — they are what ~50 generations under a permanent "
                                  "internal inquisition does to a people. The penance is "
                                  "pre-emptive: punish yourself first and you have less to fear "
                                  "from the men who come asking.",
    },
}




# ---------------------------------------------------------------------------
# AGES — linear total-story (NOT cyclical). 5 Ages; the 5th (Influence) is the
# final end-state. An Age = a domain's dominance over its timeframe (that domain
# sets the terms everyone navigates), NOT that domain's own story. Ages are
# OVERTURES: they surface undercurrents as lived experience, never explaining
# the machinery. (ERAS are unrelated — a per-empire lifecycle, a mechanics axis.)
# ---------------------------------------------------------------------------

AGES = {
    "structure": "Linear total story of the world, one arc, beginning to end. Not a cycle. "
                 "Each Age is the ANSWER TO THE FAILURE of the one before — dominance shifts because "
                 "the previous Age's method proved insufficient.",
    "an_age_is": "Tied to a domain's DOMINANCE over that timeframe (sets the conditions everyone "
                 "lives under) — but NOT that domain's story; everyone's story is told in every Age.",
    "delivery": "Overtures — short tonal pieces surfacing one undercurrent as lived experience, "
                "without explaining the framework. All framework logic stays undercurrent: felt, "
                "not read.",

    "sequence": [
        {
            "n": 1,
            "age": "The Age of Fracture",
            "event": "The Great Fractioning",
            "content": "Fall of Draggath. Draggath becomes the Wastes — a desolate land of dead and "
                       "decaying civilization. Battles fought over the ruins of the last great "
                       "empire. Decentralized governments: city-states, small kingdoms, wandering "
                       "nomadic warbands. War's answer to catastrophe was more violence, which made "
                       "it worse.",
        },
        {
            "n": 2,
            "age": "The Age of Plenty",
            "event": "The Blight — and the Trusteki's origin of excellence",
            "content": "The Blight brought great disease and death to arable land, permanently "
                       "changing some regions — including the SCARLET FOREST, which ended up "
                       "generating the best wood in the world. Enormous hardship, endured only "
                       "through engineering and overcoming adversity (patient, generation-spanning, "
                       "and SOLVED in the end). Came after Draggath's climate collapse — but where "
                       "the Kraghs fought the land and lost, the Trusteki learned to REPAIR the land "
                       "and live with the changes instead of fighting back into the earth. Their "
                       "survival and cooperative spirit propelled them into a great UTOPIA — which "
                       "was far from perfect. Blighthold is named for what it endured.",
        },
        {
            "n": 3,
            "age": "The Age of the Tetramorph",
            "event": "The rise of the False Prophet; the Inquisition of Ollanenor",
            "content": "Arose as a RESPONSE TO THE EXCESS AND OVER-INDULGENCE of the Industrial "
                       "utopia — born from the criminality and immorality that endless generated "
                       "wealth produced. Many turned to the gods of Ollanenor, Lorenthal, "
                       "Anumaranth, and Melvanar.",
        },
        {
            "n": 4,
            "age": "The Age of Doubt",
            "event": "The Reign of the Puppetmasters",
            "content": "THE ADMINISTRATION OF THE PAPACY CRUMBLED UNDER ITS OWN SIZE — not "
                       "completely, but THE EDGES BROKE OFF. Distant dioceses, frontier missions, "
                       "and the far reaches of the bureaucracy sheared away. Cracks opened, and "
                       "criminals and Machiavellian politicians climbed through them into "
                       "ARISTOCRATIC power — they did not overthrow the nobility, they BECAME it "
                       "(which is why Cunning's government is Aristocracy). The Ossensteins financed "
                       "what the church abandoned and owned it. The Shassolin were not infiltrators "
                       "— they WERE church administrators and missionaries on the frontier when the "
                       "connection to the center failed: abandoned and repurposed. The False Prophet "
                       "is a schism of DISTANCE, not doctrine — out past where the papacy's reach "
                       "ended, someone began claiming to be the messenger, and by the time the "
                       "center noticed it was an institution. THE PAPACY KNOWS AND DENIES — like an "
                       "empire unable to acknowledge it no longer governs far distant shores. To "
                       "admit the edges are gone is to admit the God of Gods' reach has limits, "
                       "which is unthinkable. So the Inquisition polices the STORY: the heresy is "
                       "not the False Prophet's claim, it is ACKNOWLEDGING HE IS OUT OF REACH. "
                       "Raiders and piracy flourish in the ungoverned space. Chaos as "
                       "DECENTRALIZATION, not apocalypse.",
        },
        {
            "n": 5,
            "age": "The Age of Renown",
            "event": "The Return to Power",
            "content": "A stable tension after the dramatic ages — a perfect balance of power, and "
                       "everyone's motivations within it. The FIFTH AND FINAL Age, deliberately the "
                       "thinnest: it is the present tense, the point where the world stops being "
                       "history and becomes a game state. Every other Age is backstory explaining "
                       "how the board got set; this one IS the board. Not triumph but MANAGED "
                       "TENSION — nobody wins; everyone positions.",
        },
    ],

    "note": "Whether the 5th Age exists in the mechanics or is a lore/end-state layer is TBD.",
}

AGES["names"] = {
    "Prowess":   "The Age of Fracture",
    "Industry":  "The Age of Plenty",
    "Piety":     "The Age of the Tetramorph",
    "Cunning":   "The Age of Doubt",
    "Influence": "The Age of Renown",
}
AGES["naming_logic"] = (
    "Tetramorph -> Doubt is the pivot: the most certain Age produces the least certain one. "
    "Doubt names the MECHANISM, not the events — the frontier stops answering and nobody knows "
    "what is still theirs; the Inquisition hunts an invisible conversion that can never be "
    "disproven; the Kraghs cannot tell who is Vorghith; the Shassolin believe they are the "
    "puppetmasters and are wrong. Renown resolves it: after 1,450 years of not knowing who anyone "
    "is, reputation becomes the only verifiable currency. DOUBT MAKES RENOWN NECESSARY."
)


# ---------------------------------------------------------------------------
# NAMED EVENTS
# ---------------------------------------------------------------------------

EVENTS = {
    "The Pincer of Dead Waters": {
        "type": "Prowess tactical feat (names Dead Waters Bay)",
        "summary": "Every northern assault on the Wheat Fields had broken on the Lost Woods treeline. A "
                   "Prowess warlord took the minimum slice of Industry to raise a single disposable "
                   "shipyard on the then-unnamed northern bay. Double-move: the main host drove south from "
                   "the north (the expected assault, drawing defenders to the treeline) WHILE the "
                   "shipyard-born flotilla landed on their flank/rear from the water. The most successful "
                   "assault on the Lost Woods to date. The bay was named Dead Waters for what came out of it.",
        "teaches": "Hybrid domain-point spending — a sliver of a 2nd domain for one unlock, not becoming "
                   "an Industry power. Proves Prowess is TACTICAL, not just brute.",
        "perspective": "'Most successful assault' is the attacker's framing; the Lost Woods crusaders name "
                       "the day a massacre / a drowning.",
        "hero": "placeholder (not yet named)",
    },
}

EVENTS["Mason-King Karalius II"] = {
    "who": "Sarkazekt. Famous shipwright and builder of MASONRY CITADELS, seated at Ivory Isle. "
           "His wealth is RECOGNIZED — not self-styled, not contested; the title is acknowledged "
           "because the money is undeniable.",
    "reputation": "THE EXPENSIVE SOLUTION THAT ALWAYS WORKS. You do not hire Karalius because he is "
                  "clever; you hire him because you have run out of cheaper options and you need "
                  "the thing to actually happen. The price is the price, and the wall stands, and "
                  "the ship floats.",
    "the_numeral": "II implies a Karalius I — an anomaly in a culture whose succession is merit, "
                   "intrigue, and strength. Likely the Industry craft-lineage numeral worn as a "
                   "crown: a workshop convention repurposed as royal succession.",
    "weightlessness": "He is not complicit; he is INFRASTRUCTURE. Whatever you use him for is on "
                      "you. The Voldrastel refuse to deal with him on principle; the Sixteni keep "
                      "his terms on file.",
}
# Explicit event->culture ownership. The generator attaches an event to a culture
# ONLY via this list (falling back to a text scan if the field is absent), so that
# cultures merely MENTIONED in commentary are not linked as participants.
EVENTS["The Pincer of Dead Waters"]["cultures"] = ["Drevghen", "Sarkazekt", "Kraghs"]
EVENTS["Mason-King Karalius II"]["cultures"] = ["Sarkazekt"]


# ---------------------------------------------------------------------------
# MAP / GEOGRAPHY
# ---------------------------------------------------------------------------

MAP = {
    "world_name": "Vaelohk (= the center island; the world is named for its center)",
    "sea": "Named perspectivally (Gulf-of-Mexico logic): Lonely Sea / Sea of Faith / Sea of Damnation are "
           "the same water from different shores. No master sea name.",
    "corners": {
        "Industry": "NW — Blighthold (castle in mountains), Scarlet Forest",
        "Prowess": "NE — Draggath Wastes (tundra), Bleak Highlands, Glen of Pravak, Drakenheart, Sea of Drakes",
        "Cunning": "SW — Dreadwood, Marrow Shoals",
        "Piety": "S/SE — Lenaveron core + Lost Woods",
    },
    "diagonals": "Prowess×Cunning and Piety×Industry are the non-adjacent pairs (no shared border) -> "
                 "enclaves/islands.",
    "twelfth_reach": "12 islands; a diaspora zone receiving displaced Prowess×Industry peoples, governed "
                     "by the Voldrastel.",
    "naming_registers": [
        "Phonological/constructed (Vaelohk, Cailendroff, Lenaveron, Vorghast)",
        "Overt-grim (Dreadwood, Sea of Damnation)",
        "Understated-grim (Bay of Pigs, Wheat Fields, Quiet Hollow, Flat Pass — mild names hiding violence)",
        "Center — plain common-tongue (The Duchy's Mouth, Bay of Renown)",
    ],
    "regional_lore": {
        "Lost Woods": "Sacred to the crusader order; pilgrims go to 'meet the God of Gods' — the crusaders "
                      "cut them down; the 'meeting' is death. Suspiciously, overtly devout.",
        "Wheat Fields": "The perpetual battlefield defending the Lost Woods from the northern barbarians; "
                        "never paved (hallowed ground). Men reaped like wheat.",
        "Tombs of the Old Gods": "Site of the Great Basilica, an old-wonder of a vanished Piety high-civilization.",
        "Draggath Wastes": "Once the Great Monarchy that held the whole continent; the Great Fractioning "
                            "shattered it into warring city-states. Named for the final monarch. Fertile "
                            "once — endless war (salted earth, deforestation) made it badlands; the ruins "
                            "ARE the former bounty.",
        "Prophet's Landing": "Caribbean-esque tropical archipelago; the false-religion racket's seat.",
        "Vaelohk": "Grounded, educated; home to the generalists and the Duke.",
    },
}

# ---------------------------------------------------------------------------
# PHONOLOGY — governs constructed names (plain-English descriptor names bypass).
# ---------------------------------------------------------------------------

PHONOLOGY = {
    "consonants_by_domain": {d: DOMAINS[d]["consonants"] for d in DOMAINS},
    "vowel_harmony": "Purity = harmony. Pure corner = one vowel class; pair = two; triple = three "
                     "(harmony breaks); center = neutral (a, schwa) / open, or deliberately all-classes "
                     "for the Generalist.",
    "endings": "Open (vowel-final / soft -n) = center/loose; closed (hard stop) = corner/sealed.",
    "collision_fix": "Keep Prowess on VOICED stops (g,b,d) and Industry on VOICELESS clusters (tr,st,pr) "
                     "so their velars don't sound identical.",
    "cunning_signature": "s -> hard-stop (Vraskil, Skorgath) sounds like a blade drawn.",
    "root_families": {
        "Prowess war-corner": "Dra-/Drag- (Drakenheart, Sea of Drakes, Draggath, Bluffs of Vorghast)",
    },
}

# ---------------------------------------------------------------------------
# CORE SPINE — the setting's first principles.
# ---------------------------------------------------------------------------

CORE_SPINE = [
    "Terrain identity is FIXED (the simplex); every NAME is a narrator's claim (perspectival).",
    "Population is a DEMOGRAPHIC OVERLAY on fixed terrain — people migrate; a region's terrain-domain "
    "!= who currently lives there. Lets anyone start anywhere / go anywhere.",
    "Map domain-points are TENDENCIES, not hard demarcations — gradient, not discrete.",
    "Names carry register-tone signalling the speaker's relationship to a place "
    "(endonym/exonym, pride/contempt, translation).",
    "Blends don't average — pick which parent leads each axis; the god often decides the fork. "
    "Two same-domain-set cultures differ by rolling different leads.",
]

# Open design threads still to resolve:
OPEN_THREADS = [
    "RESOLVED: the old diagonal-vs-god-opposition tension is obsolete — the pantheon replaced the "
    "War/Peace opposition entirely.",
    "Whether the 5th Age (Renown) exists mechanically or is a lore/end-state layer.",
    "Name the hero/warlord of The Pincer of Dead Waters (the Highlander who paid Karalius).",
    "Name the Duke. The center of the world is still unnamed.",
    "Name the False Prophet.",
    "Does the Preceptory hold other orders besides the Drevghen? Does a Drevghen pair share one "
    "saint-name or two? Does the pairing have an in-world name?",
    "Pre-0 dates are all unfixed — the Age of the Old Gods has no reckoning.",
    "Confirm the Sarkazekt already exist as arms dealers by 2910 for the Pincer to work.",
    "The 'true ledger' is a COLLECTION OF DOCUMENTS (MacGuffin, not a culture). If it ever becomes "
    "a culture, it is NOT the Cailendroffs.",
]



# For pure corners, axes = the domain column verbatim (see DOMAINS in
# renown_worldlore.py). Listed here only for completeness / the lean note.

CULTURE_AXES = {

    # ======================= PURE CORNERS =======================
    "Lenavorites": {  # Piety
        "lead": "Pure Piety (single-minded culmination)",
        "note": "Axes = the Piety column. Flavor: ultimate administrator + weaponized "
                "Catholic guilt; bureaucratic religious machine + extreme penance.",
    },
    "Kraghs": {  # Prowess
        "lead": "Pure Prowess",
        "note": "Axes = the Prowess column. Fractured warband wastes; glory-or-death.",
    },
    "Shassith": {  # Cunning
        "lead": "Pure Cunning",
        "note": "Axes = the Cunning column. Pirate/bandit haven; anarchy; the game with no rules.",
    },
    "Trusteki": {  # Industry
        "lead": "Pure Industry",
        "note": "Axes = the Industry column. Bloodline knowledge = highest status; insular.",
    },

    # ======================= PAIRS =======================
    "Drevghen": {  # Piety × Prowess — Lost Woods crusader order
        "lead": "Defenders of the Lost Woods; Prowess-weighted in practice",
        "government": "Militant ecclesiocracy — a warrior-church / theocratic military order [FUSE]",
        "sacred": "The God of Gods, served through the sword — faith as holy violence [FUSE]",
        "org_form": "Militant Order / warrior-monks [FUSE: Order + Warband]",
        "authority": "Divine mandate proven by force [Prowess-lead]",
        "economy": "Tithe + plunder (spoils of the crusade) [FUSE]",
        "kinship_unit": "The Militant Order of the Knight's Templar",
        "identity_theory": "You give the self up to the war for God [FUSE]",
        "succession": "Chosen by output in battle [Piety-lead]",
        "attitude_to_change": "Past/tradition — the sacred woods must never change [Piety-lead]",
        "military_doctrine": "Zealot-crusade + tactical defense of the treeline [FUSE]",
        "taboo": "Retreat AND doubt (cowardice = faithlessness) [FUSE — both taboos merge]",
        "defined_against": "The faithless-and-the-barbarian (the northern Kraghs are both) [FUSE]",
        "naming": "St. [name] the [Order] — martial saint-names [Piety grammar]",
        "monuments": ["Preceptory of the Knight's Templar"]
    },

    "Vorghith": {  # Prowess × Cunning — guerrilla / economic warfare
        "lead": "True fusion — force-via-indirection; neither parent dominates",
        "government": "Warlord dictatorship by fear & reputation [FUSE]",
        "sacred": "Chaos and Disruption, not glory [Prowess-base, Cunning-inflected]",
        "org_form": "Warband run like a Syndicate [FUSE]",
        "authority": "Force applied through terror — rule by strangulation [FUSE]",
        "economy": "Plunder + extraction/racket — economic warfare IS the economy [FUSE]",
        "kinship_unit": "The band + hidden cells [FUSE]",
        "identity_theory": "You are what you've done — your raids, your kills [Cunning-lead, violent]",
        "succession": "Strongest takes OR out-schemes [FUSE]",
        "attitude_to_change": "Opportunistic [Cunning-lead]",
        "military_doctrine": "Guerrilla, ambush, attrition, economic strangulation; evade decisive battle [FUSE]",
        "taboo": "Fighting head-on (evasion is doctrine, not cowardice — inverts Prowess retreat-taboo) [FUSE]",
        "defined_against": "The weak AND the honest [FUSE]",
        "naming": "[name] of the [Warband] OR earned byname — Vogen's people carry grim bynames [FUSE]",
        "monuments": ["Outrider Intercept Post", "Royal Pavilion"]
    },

    "Drakteni": {  # Prowess × Industry — siegemasters, professional army
        "lead": "Balanced; Industry gives the method, Prowess the purpose",
        "government": "Martial republic / a professional officer-state [FUSE]",
        "sacred": "War + the work — the engineered victory [FUSE]",
        "org_form": "Craft-warband (a professional standing army with an engineering corps) [FUSE]",
        "authority": "Competence + force — command earned by skill and rank [FUSE]",
        "economy": "Production + tribute — they build the war machine and take by it [FUSE]",
        "kinship_unit": "Regiments served through bloodline [Prowess-lead, institutionalized]",
        "identity_theory": "You are your training and your record [FUSE]",
        "succession": "Merit/rank — promotion through the professional hierarchy [Industry-lead]",
        "attitude_to_change": "Future/progress in the art of war — better siege, better arms [Industry-lead]",
        "military_doctrine": "Tech, logistics, siege — the best-equipped, disciplined siege specialists [FUSE]",
        "taboo": "Unpreparedness + cowardice — an ill-supplied or broken line is shameful [FUSE]",
        "defined_against": "The wasteful AND the the amateurish, the unequipped [FUSE]",
        "naming": "[name] [craft-surname] [numeral] — surnames of war-trades (Gunner, Sapper) [Industry grammar]",
        "monuments": ["Advanced Blast Furnace", "Ministry of Military Strategy"]
    },

    "Sixteni": {  # Cunning × Industry — the great trade cartel
        "lead": "Balanced; Industry on FORM (guild/lineage), Cunning on METHOD (manipulation)",
        "government": "Oligarchic cartel — a guild-syndicate board [FUSE]",
        "sacred": "The work + the game — the deal itself [FUSE]",
        "org_form": "Syndicate-Guild (a trade cartel) [FUSE: Brotherhood + Craft]",
        "authority": "Leverage + competence — you rule by controlling supply [FUSE]",
        "economy": "Production + racket — market manipulation, cornering supply, price-setting [FUSE]",
        "kinship_unit": "Merchant bloodlines bound into a syndicate [FUSE]",
        "identity_theory": "You are your inheritance AND your leverage from it [FUSE]",
        "succession": "Inherit a seat but must earn it — how much do you enrich the syndicate [FUSE]",
        "attitude_to_change": "Future/opportunistic — whatever moves markets [FUSE]",
        "military_doctrine": "Sabotage + logistics — economic weapons, embargo, bought force [FUSE]",
        "taboo": "Waste + being cut out of the deal [FUSE]",
        "defined_against": "The wasteful AND the honest [FUSE]",
        "naming": "[name] [craft-surname] [numeral] — the 'craft' is trade; merchant dynasties [Industry grammar]",
        "monuments": ["Aristocratic Court","Thieves' Guild"]
    },

    "Shassolin": {  # Cunning × Piety — false-religion field operators
        "lead": "Cunning-led (it's a con) wearing Piety's robes",
        "government": "A missionary hierarchy fronting as a church [FUSE: aristocracy + ecclesiocracy]",
        "sacred": "The False Prophet — publicly the God of Gods, privately the wealth generated from it [Cunning-lead]",
        "org_form": "Missionary order that is really a syndicate cell [FUSE]",
        "authority": "Divine mandate (claimed) + leverage (real) [Cunning-lead]",
        "economy": "Tithe + extraction — fleece the faithful [FUSE]",
        "kinship_unit": "The order over hidden brotherhood (CxPxI) [FUSE]",
        "identity_theory": "You give the self up to convince others to join.",
        "succession": "Chosen vessel (claimed) / intrigue (real) [Cunning-lead]",
        "attitude_to_change": "Tradition as cover — the con relies on looking ancient [Piety-veneer]",
        "military_doctrine": "Martyrdom + sabotage — poorly armed converts + quiet coercion [FUSE]",
        "taboo": "Being exposed as false (fusion of 'being known' + 'pride/self') [FUSE]",
        "defined_against": "The honest AND (privately) the truly faithful they prey on [FUSE]",
        "naming": "St. [name] the [Order] as the public face",
        "monuments": ["Senate Hall","Inquisitorial Palace"]
    },

    "Madekites": {  # Piety × Industry — sacred cathedral-builders
        "lead": "Balanced fusion — faith through craft",
        "government": "A builders' ecclesiocracy — a guild of sacred masons under the church [FUSE]",
        "sacred": "The God of Gods + the work — building as worship, suffering as devotion [FUSE]",
        "org_form": "Sacred Craft-Order (mason-monks) [FUSE: Order + Craft]",
        "authority": "Divine mandate + competence — the master-builder is holy [FUSE]",
        "economy": "Tithe + production — cathedral-building funded by faith and labor [FUSE]",
        "kinship_unit": "The order + the bloodline of craft (technique passed down within the faith) [FUSE]",
        "identity_theory": "You give the self up to the Work AND you use your inheritance to further it [FUSE]",
        "succession": "Chosen vessel via merit — the anointed master mason [FUSE]",
        "attitude_to_change": "Past — recover the LOST technology of the Great Basilica [Piety-lead, Industry-flavored]",
        "military_doctrine": "Defensive/siege engineering — fortress-cathedrals [Industry-lead]",
        "taboo": "Waste + pride (a flawed or vain structure is sin) [FUSE]",
        "defined_against": "The wasteful AND the faithless [FUSE]",
        "naming": "St. [name] the [Craft-Order] [numeral] [FUSE]",
        "monuments": ["Office of Works","Papal Palace"]
    },

    # ======================= TRIPLES =======================
    "Cailendroffs": {  # Piety × Prowess × Cunning — holy pretender
        "lead": "Prince = sincere (Prowess+Piety); Cunning is STRUCTURAL (the fabricated claim + handlers)",
        "government": "Court-in-exile of a claimed monarch — sacred kingship [FUSE: dictatorship + ecclesiocracy + intrigue]",
        "sacred": "The God of Gods — the pretender as divinely anointed; the war as crusade [Piety-lead, Cunning-fabricated]",
        "org_form": "A royalist warband-order around the prince [FUSE of all three]",
        "authority": "Bloodright (Prowess) + divine mandate (Piety) — both possibly fabricated (Cunning) [FUSE]",
        "economy": "Tribute + tithe + covert financing by handlers [FUSE]",
        "kinship_unit": "The claimed royal bloodline + loyal band + the order [FUSE]",
        "identity_theory": "You serve the true king / you give the self up to the cause [FUSE]",
        "succession": "Bloodright — the sacred royal line (the whole legitimacy question) [Prowess+Piety]",
        "attitude_to_change": "Past — RESTORATION; reverse the Great Fractioning of Draggath [FUSE]",
        "military_doctrine": "Crusade-reconquest + the schemers' plots [FUSE]",
        "taboo": "Doubting the prince's legitimacy (retreat + heresy + exposure all in one) [FUSE]",
        "defined_against": "The usurpers / all who deny the true anointed king [FUSE]",
        "naming": "Royal names + war-bynames that have demonstrated your allegiance to the true crown; the prince is the only St. name. 'the True King of Draggath over the water' [FUSE]",
        "monuments": ["Imperial Palace","Royal Pavilion"]
    },

    "Sarkazekt": {  # Cunning × Industry × Prowess — arms dealers / war-machine
        "lead": "Balanced ruthless fusion — make, deal, and field force",
        "government": "Militarized corporate-oligarchy — an amoral war-industrial board [FUSE]",
        "sacred": "War + the work + the game — victory-at-any-cost, sold and waged [FUSE]",
        "org_form": "Arms-syndicate with a professional army [FUSE of all three]",
        "authority": "Force + leverage + competence — the best-armed and best-connected rule [FUSE]",
        "economy": "Arms production + racket + plunder — make weapons, sell them, use them [FUSE]",
        "kinship_unit": "Weaponsmith dynasties + syndicate [FUSE]",
        "identity_theory": "You are what you've built and how you've used it [FUSE]",
        "succession": "Merit + intrigue + strength — the sharpest operator [FUSE]",
        "attitude_to_change": "Future — every edge, every new weapon and tactic [FUSE]",
        "military_doctrine": "Hyper-strategy, win-at-all-costs, any tactic for an edge; well-equipped [FUSE]",
        "taboo": "Losing an edge / being outbid / being outgunned [FUSE]",
        "defined_against": "The weak, the honest, AND the wasteful (everyone soft or naive) [FUSE]",
        "naming": "[earned combat byname] [arms-surname] [numeral] [FUSE]",
        "monuments": ["Outrider Intercept Post","Ministry of Military Strategy"]
    },

    "Ossensteins": {  # Cunning × Piety × Industry — false-religion kingpins
        "lead": "Cunning-led financiers; Industry = the scale engine; Piety = the product",
        "government": "A financier-cartel running a false church — puppet-master oligarchy [FUSE]",
        "sacred": "The False Prophet — the industrialized con of the God of Gods [Cunning-lead]",
        "org_form": "Syndicate that owns a manufactured religion [FUSE of all three]",
        "authority": "Money + leverage + claimed divine mandate [Cunning+Industry lead]",
        "economy": "Industrialized extraction — the racket as a vertically-integrated enterprise [FUSE]",
        "kinship_unit": "Financier bloodlines + hidden syndicate + the front-order [FUSE]",
        "identity_theory": "You are invisible.",
        "succession": "Machiavellian intrigue — inherit control and retain power at all costs [FUSE]",
        "attitude_to_change": "Opportunistic + progress — scale and optimize the con [FUSE]",
        "military_doctrine": "sabotage — hire and undermine, rarely fight openly [FUSE]",
        "taboo": "Waste + exposure — an unprofitable or discovered scheme is failure [FUSE]",
        "defined_against": "The honest, the wasteful, AND the truly faithful [FUSE]",
        "naming": "hidden and mysterious faction, unknown [Cunning+Industry]",
        "monuments": ["Inquisitorial Palace", "Office of Works", "Aristocratic Court"]
    },

    "Voldrastel": {  # Piety × Industry × Prowess — trade-route arbiters (no Cunning)
        "lead": "Balanced, sincere fusion — the HONEST counterpart to the Cailendroffs/Ossensteins",
        "government": "A council-republic of guardians under a code of moral faith [FUSE: democracy + ecclesiocracy + martial]",
        "sacred": "The God of Gods + the work — faith and honest trade as duty [FUSE]",
        "org_form": "A defensive order-guild (faithful merchant-wardens) [FUSE, no Cunning]",
        "authority": "Divine mandate + competence + defensive force — trusted because principled [FUSE]",
        "economy": "Production + tithe + tolls — they keep the routes open and take a fair share [FUSE]",
        "kinship_unit": "The order + trade-bloodlines + the defensive regiment [FUSE]",
        "identity_theory": "You give the self up to the duty of keeping the routes fair [FUSE]",
        "succession": "Merit + chosen vessel — the trusted, tested guardian [FUSE]",
        "attitude_to_change": "Tradition + progress — steady stewardship, improving safety [FUSE]",
        "military_doctrine": "DEFENSIVE — convoy escort, fortified waystations, siege-resistant [Prowess+Industry, defensive]",
        "taboo": "Waste + betrayal of trust + cowardice (abandoning a convoy) [FUSE]",
        "defined_against": "Raiders and cheats — those who prey on trade (esp. the Vorghith) [FUSE]",
        "naming": "[name] [numeral] of the [order-fleet] — no saint's name as their humility doesn't allow themselves to be compared to saints [FUSE]",
        "monuments": ["Ministry of Military Strategy", "Advanced Blast Furnace", "Preceptory of the Knight's Templar"]
    },

    # ======================= CENTER =======================
    "Astravantheliad": {  # Generalist — all four
        "lead": "Commands all four, embodies none forcefully; power via POSITION, not domain-force",
        "government": "Technocracy — expertise is the currency of proximity; courtiers contest each other through information and expertise to climb toward the Duke [CENTER]",
        "sacred": "Influence / proximity to power through competitive proofs & application of expertise that result positively on the Astravantheliad [CENTER]",
        "org_form": "The court / courtiers, a hierarchy ",
        "authority": "Access — whoever is nearest the throne; positional [CENTER]",
        "economy": "Rents, patronage, brokerage — they produce nothing; they broker [CENTER]",
        "kinship_unit": "Alliance networks / who owes whom [CENTER]",
        "identity_theory": "You are your proximity to power [CENTER]",
        "succession": "Positioning — outlast and outmaneuver at court [CENTER]",
        "attitude_to_change": "Whatever preserves access — the ultimate pragmatists [CENTER]",
        "military_doctrine": "None of their own — they DEPLOY others using their logistical and strategic knowledge (incl. populism as a tool) [CENTER]",
        "taboo": "Irrelevance / distance from power / to be indebtted to another [CENTER]",
        "defined_against": "The provincial (those with convictions but no access) [CENTER]",
        "naming": "[Court-standing] [name] of [Academic Hall]; the hyper-intellectual demonym performs their vanity [CENTER]",
        "monuments": ["Studium Generale", "Senate Hall", "Aristocratic Court"]
    },
}

FORMATION = {
    "rule": "INDUSTRY IS THE VECTOR. It owns the ship and the baggage cart (invented pre-0), so it "
            "is the only domain that MOVES without conquering. Prowess conquers, Cunning preys, "
            "Piety converts — Industry JOINS. Trusteki crafters left, fared well among those they "
            "met, and combined; the encounter formed a new culture. 8 of 15 carry Industry.",

    "industry_diaspora": {
        "Madekites":   "Trusteki north to Fair Whitewood 'seeking religion' -> met Piety.",
        "Drakteni":    "Trusteki east by ship to Heathport, plentiful mines -> met Prowess.",
        "Sixteni":     "Trusteki south to Marrow Shoals, meeting fleeing Shassith -> met Cunning.",
        "second_order": "The triples form from SECOND-GENERATION contact — diaspora cultures meeting "
                        "each other. The Ossensteins are the type case: the original and most "
                        "successful Trusteki families turned to trade, met the Shassolin and the "
                        "Sixteni, and formed a secret network.",
    },

    "non_industry": {
        "Drevghen":    "REFUGEE PACT. Draggaths fleeing the Fractioning met zealous Lenavorites "
                       "fleeing the Tombs of the Old Gods. The Draggaths agreed to teach martial "
                       "prowess if the Lenavorites taught them their god — the god of wrath.",
        "Shassolin":   "STRANDED CLERGY. Frontier church administrators and missionaries, abandoned "
                       "when the alministralum's edges broke off. Not infiltrators — repurposed.",
        "Cailendroffs":"EXILE. Driven out during the Great Fracture, never possessing the means to "
                       "return. No Industry = no way home.",
        "Vorghith":    "SHIPWRECK AND IMPRISONMENT. Shipwrecked and imprisoned pirates and bandits "
                       "(Shassith stock) stranded in Kragh territory. With no fleet and no numbers "
                       "they cut supply lines instead — crippling the Kraghs so profusely they were "
                       "never given an opportunity to fight back. After Vogen's Gallows the Kraghs "
                       "recoiled inland, surrendering the best prison-turned-fortress and island bay "
                       "on the continent. THE PRISONERS INHERITED THE PRISON.",
    },

    "the_kragh_wound": "The Kraghs did not lose the bay to force — they lost it to SUSPICION. Kragh "
                       "social technology assumes allegiance is VISIBLE (a warband is a banner, worn "
                       "loudly). Cunning conceals by definition. Against an enemy that does not "
                       "announce itself they had no instrument and no test. Was the citizen a "
                       "traitor? The warden? Some of the jailers must have been — but how could a "
                       "Kragh tell? Withdrawing inland was the only move: retreat to where you know "
                       "everyone, because that is the only place your way of life still functions. "
                       "SAME ENGINE AS THE INQUISITION — an invisible internal enemy that can never "
                       "be cleared. Prowess solved it by leaving; Piety could not leave, so it ate "
                       "itself for fifty generations. And some who walked out may not have been "
                       "theirs. There is no way to know.",
}

TERMS = {
    "alministralum": "The papal administrative apparatus — the machine of the church. The Age of "
                     "Doubt begins with the fall of the alministralum AT THE EDGES OF ITS REACH: "
                     "not a collapse, a shearing. The core held; the frontier stopped answering.",
    "Order of the Last Prophet": "The ENDONYM — what the followers call themselves. 'The False "
                                 "Prophet' is the orthodox EXONYM. Both names are in use; which one "
                                 "a speaker chooses places them.",
    "The Cailendroff Edict": "The document or declaration asserting the pretender's bloodright. The "
                             "Voldrastel are rumoured to hold it BLASPHEMY TO BOTH GODS AND MEN — "
                             "which the Cailendroffs know, and which is why they cannot be certain "
                             "of the one culture in the world that guarantees safe passage.",
}

PLACES_ADDENDA = {
    "Hermit's Row": "A narrow pair of mountain ranges. The DRAKTENI have invaded and hold a "
                    "position and settlement here; the KRAGHS attempt to stave off the invasion "
                    "through the narrows — the Persian-at-Thermopylae register.",
    "Bay of Lost Hope": "A Sarkazekt free-company node.",
    "The Wheat Fields": "Not a border — a PROVING GROUND. The strongest warbands and warlords come "
                        "here on purpose, to test themselves against the Drevghen, known as the "
                        "best warriors and defenders of the Lost Woods. Some believe they truly are "
                        "their god's WRATH MADE MANIFEST. This is why the stalemate has held for "
                        "millennia: a frontier under real conquest-pressure would fall or expand, "
                        "but a proving ground stays exactly where it is forever — the warbands need "
                        "somewhere to earn glory, the Drevghen need the trial to keep their balance "
                        "sharp, and neither has any interest in resolution. Never paved: hallowed "
                        "ground, where the world comes to be measured.",
}

EVENTS["Mason-King Karalius II"] = {
    "who": "Sarkazekt. Famous shipwright and builder of MASONRY CITADELS, seated at Ivory Isle. "
           "His wealth is RECOGNIZED — not self-styled, not contested; the title is acknowledged "
           "because the money is undeniable.",
    "reputation": "THE EXPENSIVE SOLUTION THAT ALWAYS WORKS. You do not hire Karalius because he is "
                  "clever; you hire him because you have run out of cheaper options and you need "
                  "the thing to actually happen. The price is the price, and the wall stands, and "
                  "the ship floats.",
    "the_numeral": "II implies a Karalius I — an anomaly in a culture whose succession is merit, "
                   "intrigue, and strength. Likely the Industry craft-lineage numeral worn as a "
                   "crown: a workshop convention repurposed as royal succession.",
    "weightlessness": "He is not complicit; he is INFRASTRUCTURE. Whatever you use him for is on "
                      "you. The Voldrastel refuse to deal with him on principle; the Sixteni keep "
                      "his terms on file.",
}

EVENTS["The Pincer of Dead Waters"]["organised_by"] = (
    "THE HIGHLANDERS, who agreed to JOIN THE MASON-KING'S MERCENARY COMPANY in exchange for his "
    "services. Payment in men, not coin — Karalius came out of the deal with a fleet and an army. "
    "The warlord did not have a stroke of genius; he had a BUDGET. Every prior assault on the Wheat "
    "Fields broke on the treeline because nobody was willing to pay Karalius' number. The one who "
    "finally was, won."
)
EVENTS["The Pincer of Dead Waters"]["significance"] = (
    "THE ONLY DEFEAT EVER RECORDED OF THE DREVGHEN. They gave ground in the Wheat Fields for the "
    "first time that day — on ground that is never paved because it is hallowed. For an order whose "
    "taboo is retreat AND doubt, this is not a battle loss but a THEOLOGICAL EVENT: the standard "
    "failed the test, and every warlord ever turned back there learned it could be done. Worse, the "
    "tactic MIRRORED them — a two-pronged attack against an order whose entire discipline is holding "
    "two halves in balance. 156 years later the alministralum's edges began to break."
)
PRECEPTORY = {
    "what": "The holy order. The DREVGHEN are a SUBSET of it — one militant order under the "
            "Preceptory umbrella, not the whole institution.",
    "the_pairing": "Every Drevghen is PAIRED WITH THEIR OPPOSITE ORIGIN — one Draggath-descended, "
                   "one Lenavorite-descended — bound as mutual lifelong mentors. Each teaches what "
                   "their line brought. They train together and FIGHT TOGETHER: the pair is the "
                   "combat unit. The founding trade never ended; it is a thing every member does "
                   "every day, for life.",
    "why_it_holds": "DOCTRINE, not logistics. PURE BALANCE is the sacred thing. A monoculture would "
                    "drift — the martial wing secularizing, the devotional wing softening. Forced "
                    "pairing prevents both and structurally guarantees the order stays exactly "
                    "half-and-half. Their real fear is not defeat but DRIFT: a brother who becomes "
                    "more warrior than devotee, or more devotee than warrior, is the failure state.",
    "the_taboo_explained": "'Retreat AND doubt' is not two prohibitions bolted together — it is ONE: "
                           "IMBALANCE. Retreat is the Draggath half failing; doubt is the Lenavorite "
                           "half failing. Either is the same sin.",
    "the_oldest_monument": "Not a building — the ORDER ITSELF. Everything else in the world "
                           "fractured, migrated, converted, collapsed, or reinvented itself; the "
                           "Drevghen have done the same thing in the same woods since the Fracture. "
                           "They PREDATE THE PAPACY by ~1,900 years, and predate the recording of "
                           "the four gods — they worshipped wrath before Melvanar had a written "
                           "name. The Inquisition has no purchase on them: a regime built on "
                           "suspecting internal conversion runs into an order structurally incapable "
                           "of drifting, which alone would make them suspect. They are not a faction "
                           "with ambitions but a FEATURE OF THE LANDSCAPE, like the mountains.",
    "the_horror": "A pilgrim in the Lost Woods is cut down not by one zealot but by TWO MEN WHO "
                  "HAVE BEEN EACH OTHER'S WHOLE LIFE — one who inherited the sword, one who "
                  "inherited the wrath, each of whom taught the other. Sincere, mutual, and "
                  "completely closed.",
    "open": "Does the Preceptory hold other orders besides the Drevghen? Does a pair share one "
            "saint-name or hold two? Does the pairing have an in-world name?",
}

RIVALRIES = {
    "Drakteni vs Madekites": {
        "over": "What building is FOR — conquest vs devotion.",
        "shared_domain": "Industry",
        "detail": "The expansionist Drakteni ('their craft is conquest') constantly attack the "
                  "Madekites, which is WHY the Madekites build fortress-citadels. Their "
                  "siege-engineering doctrine has a cause, and their Great Basilica obsession has a "
                  "war-zone context: the most beautiful thing in the world, built under assault, by "
                  "people who think the suffering is the point. One builds siege engines to break "
                  "walls; the other builds walls to survive them.",
    },
    "Sixteni vs Voldrastel": {
        "over": "The trade routes — predator vs protector.",
        "shared_domain": "Industry",
    },
    "Vorghith vs Kraghs": {
        "over": "Supply lines, and the impossibility of telling friend from enemy.",
        "detail": "See FORMATION['the_kragh_wound'].",
    },
    "Drakteni vs Kraghs": {
        "over": "Hermit's Row — the Drakteni hold a settlement in the narrows; the Kraghs try to "
                "stave off the invasion.",
    },
    "pattern": "TWO OF THE FIRST THREE RIVALRIES ARE INDUSTRY-INTERNAL. Industry is the most "
               "CONTESTED domain — its cultures define themselves against each other. Prowess "
               "cultures fight everyone; Industry cultures fight their own kind over the meaning of "
               "the work. They agree on the WHAT and split on the WHY.",
}

EXPANSION_HOOKS = {
    "new_ages_new_domains": "Future expansions sit in DIFFERENT AGES and introduce a new mechanic — "
                            "e.g. an AGE OF MYSTICISM creating a FIFTH DOMAIN. Either swap a domain "
                            "out for it, or play with five. Ships with another colour or two of "
                            "tokens, mystic actions, buildings, factions. Repeatable per expansion.",
}

LORE_SEQUENCE = {
    "order": ["4 pure corners", "6 pairs", "4 triples", "Astravantheliad"],
    "why": "Pures establish the vocabulary — four clean archetypes, no blending to track. Pairs let "
           "the reader DO THE MATH THEMSELVES and teach the blend rule by reward ('of course a "
           "Prowess x Cunning people would refuse open battle'). Triples are harder and now earned, "
           "and hold the best material. The Astravantheliad last, because their paradox only works "
           "on a reader who has already met the four domains that find them illegible — you cannot "
           "understand why a Kragh rejects a refinement on his stance until you have met a Kragh.",
    "effect": "Teaches the simplex WITHOUT EVER EXPLAINING IT. By the time a reader reaches the "
              "center they have learned domain-blending by induction — framework stays undercurrent, "
              "felt not read.",
}


if __name__ == "__main__":
    print(f"Renown world-lore: {len(CULTURES)} cultures, {len(DOMAINS)} domains, {len(GODS)} gods.")
    for name, c in CULTURES.items():
        print(f"  [{c['type']:<6}] {name:<16} {'×'.join(c['domains'])}")
    print(f"Culture axes: {len(CULTURE_AXES)} cultures resolved.")
    for name, ax in CULTURE_AXES.items():
        print(f"  {name:<16} lead: {ax['lead']}")