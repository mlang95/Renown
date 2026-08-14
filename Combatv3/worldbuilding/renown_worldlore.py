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
        "identity_theory": "You are who you fight for",
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
        "the_name": "Esselantheum is spoken only on Prophet's Landing. The false-religion cultures "
                    "say it aloud — saying it is the sales pitch: we can name him, therefore we can "
                    "reach him. The orthodox cannot correct the pronunciation, because to know the "
                    "true name would itself be blasphemy.",
        "tell": "A character who says 'Esselantheum' has been to Prophet's Landing or been converted "
                "by someone who has. The word is evidence.",
    },
    "Ollanenor": {
        "tier": "Greater deity — the GREATEST, of utmost power",
        "domain": "SAINTS",
        "nature": "The deliverer of saints' names. When a person gives themselves up to an order "
                  "their born name is erased and Ollanenor returns one in its place — an office "
                  "rather than a person, worn by whoever holds it now and passed on when they "
                  "do not. The most mysterious of the sects, and an orthodoxy of power.",
        "seat": "The Inquisitorial Palace",
        "order": "The Inquisition",
        "the_schooling": "The Inquisition runs the EDUCATIONAL ARM of the papacy — the "
                         "administration is Anumaranth's, but the teaching is Ollanenor's. They "
                         "prepare a person to give themselves up: what it will cost, what will be "
                         "asked, and WHICH ORDER SUITS THEM, weighed against their temperament and "
                         "their preferences. A novice does not choose blind. They are counselled "
                         "toward wrath or peace or balance or the saints by the people who will "
                         "later hand them the name.",
    },
    "Anumaranth": {
        "tier": "Greater deity",
        "domain": "BALANCE",
        "nature": "Makes those who are empty WHOLE, and those who must be tithed, REDUCED. "
                  "The god of ADMINISTRATION.",
        "seat": "The Papal Palace",
        "order": "The Order of the True Word — the ultimate administrators, who attempt to record "
                 "every possible thing. People believe these documents will prove their truths.",
    },
    "Melvanar": {
        "tier": "Greater deity",
        "domain": "WRATH",
        "nature": "The most archaic and gothic. Self-flagellation. Spreads its message through the "
                  "REDUCTION OF FALSE GODS.",
        "adherents": "The Belvareth — self-flagellating knightly crusaders defending the Lost Woods as "
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

DIVINITY_RULE = ("Some level of Piety is required for there to be a god — but THE GODS NEVER "
                 "INTERACT with the world or the narrative. They are a MEDIUM PEOPLE USE; whether "
                 "they exist is beside the point, and it is never adjudicated. No miracle occurs on "
                 "the page, no wrath is delivered, no prayer is answered. What scales with worship "
                 "is INSTITUTIONAL reach, not power: a god with no worshippers is a god with no "
                 "orders, no palaces, and no tithe. The Tombs of the Old Gods are ABANDONED "
                 "INSTITUTIONS, not dead beings — the old gods died the way a language dies. "
                 "Consequence: the False Prophet's con is undetectable IN PRINCIPLE. He brokers "
                 "access to something that would never respond anyway, so no test distinguishes him "
                 "from an orthodox priest — which is why the Inquisition polices SPEECH rather than "
                 "evidence. There is no evidence to find.")
                 
# Piety governs GODS, not MONSTERS. The divinity rule does not reduce mythos —
# folklore stays folklore: unverified, persistent, and never adjudicated by the
# narrative. The explanation is wrong and the warning is usually correct.
MYTHOS = {
    "rule": "Belief creates gods; it does not create monsters. Mythos is EXEMPT from the divinity "
            "rule and is never confirmed or denied.",
    "The Drakes": "The Sea of Drakes is named for the mythology that flying drakes destroy ships to "
                  "protect the water. There are no drakes. The stretch is tumultuous; ships still "
                  "sink there.",
    "The Giants of Cravencroft": "The Kraghs hold that giants in Cravencroft destroy the weak and "
                                 "the outcast. A threat aimed at their own — the story a "
                                 "glory-or-death culture tells to keep weakness from taking root. "
                                 "Nobody volunteers to test it.",
}

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
    "who_teaches": "The INQUISITION holds the schooling. Administration belongs to Anumaranth "
                   "and the Papal Palace, but the preparation of novices belongs to Ollanenor — "
                   "the god who delivers the name is the god whose order decides you are ready "
                   "for one. Every person in every order was placed there on Inquisitorial "
                   "counsel. The Inquisition was inside the formation of the whole church long "
                   "before it took the government of it, and when the suspicion began, the "
                   "people it suspected were the people it had taught.",
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
                       "Belvareth, serving Melvanar), NOT pure Piety. Pure Piety stays devotional, "
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
                    "that held the whole continent; the Great Fracture shattered it into perpetually "
                    "warring city-states and warbands. Now nomadic warbands + some static city-states, "
                    "perpetually training for inevitable conflict.",
    },
    "Ithiss": {
        "type": "pure",
        "domains": ["Cunning"],
        "region": "Dreadwood + Marrow Shoals",
        "identity": "An ANARCHIC ARISTOCRACY comprised of BROTHERHOODS AND GUILDS that form CRIMINAL "
            "EMPIRES. A pirate/bandit haven — far more anarchy than anywhere else; no central "
            "authority, but a rigid internal hierarchy of the feared and successful. The game with "
            "no rules imposed on it.",
        "trade_relation": "Primary supplier of illegally sourced FENCED GOODS to the Prezish, who "
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
    "Belvareth": {
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
    "Prezish": {
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
        "region": "Cailendroff Isles",
        "identity": "Believers that their warband is led by the LAST REMAINING BLOODLINE of the last "
            "monarch of the Draggath Empire, and that the Draggath Wastes must be united under one "
            "banner — his. Exiled during the Great Fracture, they have never had the means to "
            "return, the harder now with Sarkopekt free companies patrolling the Sea of Damnation, "
            "never knowing who they work for. They are unsure even of the Voldrastel, who are "
            "rumoured to hold the CAILENDROFF EDICT blasphemy to both gods and men. So they use "
            "piety and cunning to generate loyalists and recruits — growing the warband's size, "
            "skill base, and economic standing toward a FINAL CRUSADE to reunite the Kraghs under "
            "their true king, the Draggath dynasty.",
    },
    "Sarkopekt": {
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
            "Trusteki families, who turned to trade, met the Shassolin and the Prezish, and formed "
            "a secret network dedicated to world power without ever being known.",

    },
    "Voldrastel": {
        "type": "triple",
        "domains": ["Piety", "Industry", "Prowess"],
        "region": "The Twelfth Reach (12 islands)",
        "role": "Neutral defenders of the trade routes and seas — safe passage and honest brokering as an "
            "intermediary, for a toll and a broker's fee. The stoic wardens of the world's roads and "
            "sea routes: powerful, and wielded for good.",
        "identity": "The MORAL AUTHORITY and the direct ANTAGONIST OF THE PREZISH. Heroes to others for "
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
                           "highest calling. FROM INSIDE: the Age of Renown is the age REASON "
                           "FINALLY GOVERNS.",
    "external_reputation": "Vain, hollow, produces nothing. Their work is the most THEORETICAL — "
                           "from outside, a lifetime spent on something that never touches the "
                           "ground. The output is real, but it is abstraction, and abstraction is "
                           "invisible to everyone outside the Hall. FROM OUTSIDE: the Age of "
                           "Renown is the age NOBODY DOES ANYTHING.",
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
        "Ithiss (Cunning)": "Do not believe the Astravantheliad know anything about business — and "
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
# YEAR 0 = THE GREAT FRACTURE. Everything prior is negative.
#
# AGES ARE GRADIENTS, not hard boundaries — same principle as the geography.
# The start years below are the dates the True Word RECORDS, not the moment
# anything actually changed. Ages are declared retroactively; nobody living
# through the Fracture knew it ended one.
#
# PROVISIONAL — nothing is written in stone yet.
# ---------------------------------------------------------------------------

TIMELINE = {
    "unit": "One year = one full Trusteki agricultural cycle.",
    "epoch": "Year 0 = The Great Fracture.",
    "gradient_rule": "Age boundaries are ranges, not points. Recorded start years are the "
                     "True Word's reckoning, assigned in hindsight.",
    "present": "~4570s–4580s. A generation or two into the Age of Renown.",

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
        "name": "The Age of Darkness",
        "dating": "Before the count. No firm reckoning survives; the True Word records only "
                  "that it was.",
        "premise": "The old gods brought four peoples into the four corners of the world.",
        "the_four_foundings": {
            "Trusteki": "Formed as FARMERS worshipping the old deity TRUSTI, in the old "
                        "continent of the ancient Coloured Mountains.",
            "Draggath": "Formed as WARRIORS under the Draggath Monarchy — eager expansionists "
                        "following the monarch's commands, believing the monarch to be the ear "
                        "and WARRIOR-PROPHET of the old god CAILEN.",
            "Ithiss":  "Far south-west. Nomadic and sparse, incapable of trusting one another "
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
            "Ithiss": "Some, seeing the bounty taken in ambushes on Trusteki caravans, believed "
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
        "event": "THE GREAT FRACTURE",
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
         "event": "The Great Fracture. Draggath falls."},
        {"year": "0–~400", "age": "Prowess",
         "event": "Geography transforms over several generations. Lenavorites build simple rafts "
                  "and flee west — naming the STRAIT OF SORROW, as many and most fell ill on the "
                  "journey and died, only to find a worse swampy wetland to settle, inhabited by "
                  "bandits and conmen of the immoral kind."},
        {"year": "0–~400", "age": "Prowess",
         "event": "The Ithiss leave their underground cities as the climate changes."},
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

        # ---- AGE OF INDUSTRY (1352–1942) ----
        {"year": 1352, "age": "Industry",
         "event": "From the proliferation of the SCARLET FOREST, the migration to "
                  "Blighthold from the Coloured Mountains, and the general capacity to move at "
                  "sea."},
        {"year": 1352, "age": "Industry",
         "event": "The soil south of Blighthold turns blood red; SCARLET TREES grow from it. A "
                  "verdant swelling — trees reaching the size of the old wood of Fair Whitewood "
                  "within a single generation. The Trusteki's skill lets them survive and REPEL "
                  "the blight."},
        {"year": "1352–1942", "age": "Industry",
         "event": "THE MIGRATIONS. Some Trusteki, not stalwart, move north seeking religion in "
                  "the wintery forested mountain pass of FAIR WHITEWOOD. Others build ships and "
                  "flee east, finding a natural port dubbed HEATHPORT with plentiful mines. "
                  "Others venture south to the archipelago of the MARROW SHOALS, meeting the "
                  "fleeing Ithiss coming from the south, seeking another way of life."},
        {"year": "1352–1942", "age": "Industry",
         "event": "THE UTOPIA. Survival and cooperative spirit propel the Trusteki into a great "
                  "utopia — far from perfect. Wealth eventually outpaces meaning; criminality and "
                  "indulgence follow."},

        # ---- AGE OF PIETY (1942–3066) ----
        {"year": 1942, "age": "Piety",
         "event": "Lenavorites are scattered in tiny ABBEYS, PRIORIES and "
                  "MONASTERIES, forming many small orders. These begin combining into larger and "
                  "larger administrative bodies IN THE SEARCH OF TRUTH. Rises as a response to "
                  "the excess and over-indulgence of the Industrial utopia."},
        {"year": "1942–2100", "age": "Piety",
         "event": "THE UNIFYING FORCE. The FOUR GODS are recorded — Ollanenor, Anumaranth, "
                  "Melvanar, Lorenthal. THE PAPACY BEGINS at this moment. Mission work starts as "
                  "a COLLECTIVE movement."},
        {"year": "1942–2100", "age": "Piety",
         "event": "THE INQUISITION appears — mostly IDLE AND SYMBOLIC. As proof of the absence of "
                  "any other false gods, they do nothing."},
        {"year": "2100–3066", "age": "Piety",
         "event": "Peak reach. Missions carry the faith to the furthest shores, and the "
                  "bureaucracy doubles, and doubles again."},

        # ---- AGE OF CUNNING (3066–4516) ----
        {"year": 3066, "age": "Cunning",
         "event": "Consolidating the small orders into one papacy required declaring "
                  "who stood OUTSIDE it. EXCOMMUNICATIONS for failing to recognize the "
                  "tetramorph — and the excommunicated go somewhere."},
        {"year": 3066, "age": "Cunning",
         "event": "THE FALSE GOD MANIFESTS ON PROPHET'S LANDING, among the excommunicated. A "
                  "schism of DISTANCE as much as doctrine — out past where the papacy's reach "
                  "ended. By the time the center noticed, it was an institution."},
        {"year": "3100–4516", "age": "Cunning",
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
        {"year": "3300–4516", "age": "Cunning",
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
         "event": "The present day. A generation or two into the Age."},
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
        "shassith_founding_refusal": "The Ithiss's founding act was REJECTING Clypso, the god "
                                     "who brought them together. That is why Cunning is "
                                     "permanently a doubter domain.",
        "who_keeps_the_calendar": "The Order of the True Word maintains the reckoning — so the "
                                  "papacy DATES the world even where it no longer GOVERNS it. "
                                  "Prophet's Landing presumably keeps its own count.",
        "ages_declared_retroactively": "Nobody knew the Fracture ended an Age; they thought it "
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
            "event": "The Great Fracture",
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
    "Darkness":  "The Age of Darkness",
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
        "year": "2910 (provisional)",
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

# Explicit event->culture ownership. The generator attaches an event to a culture
# ONLY via this list (falling back to a text scan if the field is absent), so that
# cultures merely MENTIONED in commentary are not linked as participants.


# ---------------------------------------------------------------------------
# MAP / GEOGRAPHY
# ---------------------------------------------------------------------------

MAP = {
    "world_name": "Vaelohk — the centre island, and the name the world took from it",
       "sea": "One sea, and no name for the whole of it. Each shore names the water it can "
               "see, and the ring is wide enough that they are all describing something "
               "different.",
        "sea_stretches": {
            "The Lonely Sea": "A vast open sea of DOLDRUMS.",
            "The Sea of Drakes": "Tumultuous. Mythology holds that flying drakes destroy ships to "
                                 "protect it. Borders the Prowess corner.",
            "The Sea of Miracles": "Where miracles are said to have happened.",
            "The Sea of Damnation": "Fraught with DRAKTENI and SARKOPEKT — where the damned are sent to "
                                    "meet their deserved fate. The name is HONEST BY ACCIDENT: what is "
                                    "actually out there is a conquest fleet and mercenary free "
                                    "companies of unknown allegiance. Whether the damnation is "
                                    "theological or just Drakteni siege-ships depends on who you ask.",
        },
    "corners": {
        "Industry": "NW — Blighthold (castle in mountains), Scarlet Forest",
        "Prowess": "NE — Draggath Wastes (tundra), Bleak Highlands, Glen of Pravak, Drakenheart, Sea of Drakes",
        "Cunning": "SW — Dreadwood, Marrow Shoals",
        "Piety": "S/SE — Lenaveron and the Lost Woods",
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
        # ---- Prowess corner (NE) ----
        "Draggath Wastes": "Once the Great Monarchy that held the whole continent; the Great "
                           "Fracture shattered it into warring city-states. Named for the final "
                           "monarch — and for the empire, the dynasty, and the land, all synonymous. "
                           "Fertile once: endless war (salted earth, deforestation) made it "
                           "badlands, and the ruins ARE the former bounty. Recursive scarcity — the "
                           "more they fought over the lessening fertile land, the less there was.",
        "Bleak Highlands": "Pastoralists, living as historical Highlanders did — herding clans "
                           "under a CHIEF they swear fealty to. The northern limit of Vorghith "
                           "expansion: VOGEN, their general, drove up to here in 1136 and no "
                           "further. Also a Sarkopekt free-company node. When the Pincer was "
                           "organised it was Highland clans who enlisted in the Mason-King's "
                           "mercenary company in exchange for his services — paying in "
                           "FEALTY-SERVICE rather than coin, which is how their oaths already "
                           "work.",
        "Glen of Pravak": "Named for the WARBAND of Pravak — the most well-trained Kragh warband of "
                          "the early Fracture, which held the last remaining glen of tillable land "
                          "FOR CENTURIES. Their strong internal pact DISALLOWED VORGHITH "
                          "INFILTRATION: the one known counter to the problem that would later cost "
                          "the Kraghs the bay, solved in one glen and never generalised. Their dual "
                          "concentration on ATHLETICISM AND STRATEGY, plus intimate knowledge of the "
                          "ground, let them posture every battle in the glen into their favour. "
                          "Pravak is long gone, but his attention to POSITIONAL STRATEGY AND TACTICS "
                          "reshaped how the Kraghs train.",
        "Cravencroft": "The Kraghs hold that giants here destroy the weak and the outcast. A threat "
                       "aimed at their own: giants that eat the weak is the story a glory-or-death "
                       "culture tells to keep weakness from taking root. Nobody volunteers to test "
                       "it.",
        "Hermit's Row": "A narrow pair of mountain ranges. The DRAKTENI hold a position and "
                        "settlement here; the KRAGHS hold the narrows against them.",
        "Vogen's Gallows": "Named for VOGEN, the Vorghith general whose signature was assassinating "
                           "opponents by PUBLIC EXECUTION. The best prison-turned-fortress and "
                           "island bay on the continent — abandoned by the Kraghs when they could no "
                           "longer tell who among them was Vorghith, and inherited by the prisoners. "
                           "Public execution is psychological and economic warfare, not battlefield "
                           "glory: a Kragh kills you in open combat for honour, Vogen hangs you in "
                           "the square so everyone watches.",

        # ---- Industry corner (NW) ----
        "Blighthold": "Castle in the mountains. The heath where the Trusteki grew crops through the "
                      "BLIGHT using ancient trade secrets, working together to survive the diseased "
                      "land. NAMED FOR WHAT IT ENDURED — and it doubles as reverse-marketing "
                      "to keep people from coming. Received the migration from "
                      "the Coloured Mountains at the opening of the Age of Plenty.",
        "Scarlet Forest": "The soil south of Blighthold turned blood red after the Blight, and "
                          "SCARLET TREES grew from it — a verdant swelling, trees reaching the size "
                          "of the old wood of Fair Whitewood within a single generation. Produces "
                          "the BEST WOOD IN THE WORLD. The most damaged land became the most "
                          "valuable, and they would never fight the earth again.",
        "Coloured Mountains": "The ancient continent where the TRUSTEKI first formed as farmers "
                              "worshipping the old deity TRUSTI. Their migration to Blighthold opens "
                              "the Age of Plenty.",
        "Heathport": "A natural port with plentiful mines, found by Trusteki who built ships and "
                     "fled east after the Blight — where they met Prowess and became the DRAKTENI. "
                     "Now one end of the Ithiss-to-Prezish illicit route (Heathport to the Wharf "
                     "of St. Brannoch).",
        "Drakenheart": "Drakteni seat. Their craft is conquest: firepower built to expand beyond the "
                       "continent, campaigns constantly funded and refunded. It is also the SMALLEST "
                       "LANDMASS for the size of the culture on it — the engine of everything they "
                       "do. They colonise to make room for themselves as an empire.",

        # ---- Cunning corner (SW) ----
        "Dreadwood": "Ithiss heartland. An ANARCHIC ARISTOCRACY of brotherhoods and guilds forming "
                     "criminal empires — no central authority, but a rigid internal hierarchy of the "
                     "feared and successful.",
        "Crag Pass": "A natural chokepoint of narrow paths, labyrinths, and slot canyons, found and "
                     "controlled by the ISSETH from their underground network — reached in secret, "
                     "held without garrison. Where Trusteki caravans learned the dangers of the "
                     "south, and the route by which Ithiss who wanted another life ventured north.",
        "Marrow Shoals": "Shared water — ISSETH and PREZISH both. Where Trusteki venturing south met the Ithiss coming north, "
                         "forming the Prezish.",
        "Bay of Pigs": "A WEAPONIZED FALSE EXONYM. The dismissive name was given by outsiders, and "
                       "the locals KEEP IT DELIBERATELY — a bay named for filth attracts no "
                       "attention and lowers a merchant's guard. Prezish seat: pirates, smugglers, "
                       "brokers, money-lenders and profiteers. The name is the first move of the con.",

        # ---- Piety corner (S/SE) ----
        "Lenaveron": "Named by the LENAVORITES after themselves when they migrated north and west "
                     "out of the frozen tundra — THE FIRST WRITTEN RECORD IN THE WORLD. Papacy "
                     "heartland; seat of the Papal Palace (Anumaranth) and the Inquisitorial Palace "
                     "(Ollanenor).",
        "Lost Woods": "Sacred to the crusader order. Pilgrims come to 'meet the God of Gods' — and "
                      "the Belvareth cut them down; the meeting IS death. Theologically correct from "
                      "inside: seeking Esselantheum directly is the blasphemy, and Melvanar's "
                      "doctrine spreads by the reduction of false gods. Everyone sincere, nobody "
                      "lying. The only land left untouched by the Great Fracture.",
        "Wheat Fields": "Not a border — a PROVING GROUND. The strongest warbands and warlords come "
                        "here on purpose to test themselves against the Belvareth, known as the best "
                        "warriors in the world; some believe they truly are their god's WRATH MADE "
                        "MANIFEST. A frontier under conquest-pressure would fall or expand; a "
                        "proving ground stays exactly where it is forever, because both sides want "
                        "it to. Never paved: hallowed ground, where the world comes to be measured. "
                        "Men reaped like wheat.",
        "Tombs of the Old Gods": "The frozen south-eastern tundra the Lenavorites abandoned. Site of "
                                 "the GREAT BASILICA — an old-wonder of the vanished high "
                                 "civilization. The graveyards and basilicas were left to crumble "
                                 "and the old gods forgotten: ABANDONED INSTITUTIONS, not dead "
                                 "beings. The Madekites chase the lost technology of the Basilica still.",
        "Fair Whitewood": "Wintery forested mountain pass. Settled by Trusteki who moved north "
                          "'seeking religion' and became the MADEKITES — hard tundra rich with "
                          "quarries, where the pain and sacrifice of building is devotion. Their "
                          "fortress-cathedrals exist because the expansionist Drakteni will not stop "
                          "coming.",
        "Strait of Sorrow": "Named by the Lenavorites who built simple rafts and fled west after the "
                            "Fracture — MANY AND MOST FELL ILL ON THE JOURNEY AND DIED, only to "
                            "find a worse swampy wetland to settle, inhabited by bandits and conmen "
                            "of the immoral kind.",
        "Shallow Mire / Quiet Hollow": "Swampy wetland at the end of the Strait of Sorrow. SHASSOLIN "
                                       "territory — administrators and missionaries of the false "
                                       "religion, stranded frontier clergy abandoned and "
                                       "repurposed.",
        "Wharf of St. Brannoch": "Named for a saint. A natural sanctuary off the coast of "
                                 "Lenaveron, and the busiest of the Sarkopekt nodes — where "
                                 "city-states, warbands and travelling nomads hire themselves "
                                 "out. Also the far end of the Ithiss-to-Prezish illicit route "
                                 "from Heathport.",

        # ---- Islands, sea, and the centre ----
        "Vaelohk": "The centre island, and the world's name. Grounded and educated: home to the "
                   "Academic Halls, the technocratic senate, and the Duke. Place-names here are "
                   "plain common-tongue (The Duchy's Mouth, Bay of Renown).",
        "Ivory Isle": "Known historically as the seat of MASON-KING KARALIUS II — shipwright and builder "
                      "of masonry citadels, the expensive solution that always worked. His wealth "
                      "was recognised, not self-styled. Now a Sarkopekt node sitting between the "
                      "seat of power and the war-market.",
        "Dead Waters": "Named for what came out of the shipyard raised on its then-unnamed shore. The "
                       "Pincer folded the Belvareth here — the only defeat ever recorded of them.",
        "Sea of Ash": "A sea COMPLETELY CONTAMINATED BY ASH. Crossable, but it yields nothing — no "
                      "fish, no drinking water. You carry everything across it or you do not "
                      "arrive. Some say it is the ash of the old gods.",
        "Prophet's Landing": "A beautiful tropical archipelago — PARADISE AS BAIT. "
                             "Where the false god manifested among the EXCOMMUNICATED (expelled for "
                             "failing to recognise the tetramorph). The only place in the world "
                             "where ESSELANTHEUM is spoken aloud; saying it IS the sales pitch.",
        "The Twelfth Reach": "Twelve islands. A diaspora zone receiving displaced Prowess x Industry "
                             "peoples, governed by the VOLDRASTEL — neutral wardens of the trade "
                             "routes, safe passage and honest brokering for a toll and a broker's "
                             "fee.",
        "Cailendroff Isles": "Home of the exiled pretender's people, driven out during the Great "
                             "Fracture and never possessing the means to return — the harder now "
                             "with Sarkopekt free companies patrolling the Sea of Damnation under "
                             "unknown allegiance.",
        "Bay of Lost Hope": "A Sarkopekt free-company node.",

        # ---- Still undefined ----
        "Weary Mountains": "UNDEFINED.",
        "Lemstet Bay": "UNDEFINED.",
        "Crooked Bay": "UNDEFINED.",
        "Flat Pass": "UNDEFINED — understated-grim register only.",
        "The Duchy's Mouth": "UNDEFINED — centre, plain common-tongue.",
        "Bay of Renown": "UNDEFINED — centre, plain common-tongue. The only place sharing the game's "
                         "title.",
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
    "Pre-0 dates are all unfixed — the Age of the Old Gods has no reckoning.",
    "Confirm the Sarkopekt already exist as arms dealers by 2910 for the Pincer to work.",
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
    "Ithiss": {  # Cunning
        "lead": "Pure Cunning",
        "note": "Axes = the Cunning column. Pirate/bandit haven; anarchy; the game with no rules.",
    },
    "Trusteki": {  # Industry
        "lead": "Pure Industry",
        "note": "Axes = the Industry column. Bloodline knowledge = highest status; insular.",
    },

    # ======================= PAIRS =======================
    "Belvareth": {  # Piety × Prowess — Lost Woods crusader order
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
        "defined_against": "The wasteful AND the amateurish, the unequipped [FUSE]",
        "naming": "[name] [craft-surname] [numeral] — surnames of war-trades (Gunner, Sapper) [Industry grammar]",
        "monuments": ["Advanced Blast Furnace", "Ministry of Military Strategy"]
    },

    "Prezish": {  # Cunning × Industry — the great trade cartel
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
        "attitude_to_change": "Past — RESTORATION; reverse the Great Fracture of Draggath [FUSE]",
        "military_doctrine": "Crusade-reconquest + the schemers' plots [FUSE]",
        "taboo": "Doubting the prince's legitimacy (retreat + heresy + exposure all in one) [FUSE]",
        "defined_against": "The usurpers / all who deny the true anointed king [FUSE]",
        "naming": "Royal names + war-bynames that have demonstrated your allegiance to the true crown; the prince is the only St. name. 'the True King of Draggath over the water' [FUSE]",
        "monuments": ["Imperial Palace","Royal Pavilion"]
    },

    "Sarkopekt": {  # Cunning × Industry × Prowess — arms dealers / war-machine
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
        "Prezish":     "Trusteki south to Marrow Shoals, meeting fleeing Ithiss -> met Cunning.",
        "second_order": "The triples form from SECOND-GENERATION contact — diaspora cultures meeting "
                        "each other. The Ossensteins are the type case: the original and most "
                        "successful Trusteki families turned to trade, met the Shassolin and the "
                        "Prezish, and formed a secret network.",
    },

    "non_industry": {
        "Belvareth":    "REFUGEE PACT. Draggaths fleeing the Fracture met zealous Lenavorites "
                       "fleeing the Tombs of the Old Gods. The Draggaths agreed to teach martial "
                       "prowess if the Lenavorites taught them their god — the god of wrath.",
        "Shassolin":   "STRANDED CLERGY. Frontier church administrators and missionaries, abandoned "
                       "when the alministralum's edges broke off. Not infiltrators — repurposed.",
        "Cailendroffs":"EXILE. Driven out during the Great Fracture, never possessing the means to "
                       "return. No Industry = no way home.",
        "Vorghith":    "SHIPWRECK AND IMPRISONMENT. Shipwrecked and imprisoned pirates and bandits "
                       "(Ithiss stock) stranded in Kragh territory. With no fleet and no numbers "
                       "they cut supply lines instead — crippling the Kraghs so profusely they were "
                       "never given an opportunity to fight back. After Vogen's Gallows the Kraghs "
                       "recoiled inland, surrendering the best prison-turned-fortress and island bay "
                       "on the continent. THE PRISONERS INHERITED THE PRISON.",
    },

    "the_centre": {
        "Astravantheliad": "SETTLEMENT BY THE MOST DIVERSE. Not conquest, not diaspora, not a pact — "
                           "they came as a COLLECTIVE, from all different walks of life, and settled "
                           "the centre.",
        "families_embrace_all_culture": "The melting pot is ADDITIVE, NOT ERASIVE. A family that "
                                        "arrived Kragh does not stop being Kragh-descended and does "
                                        "not stay merely Kragh — it takes on the rest. This is why "
                                        "every citizen carries all four domains at a baseline: not "
                                        "curriculum, HOUSEHOLD INHERITANCE. They have all four "
                                        "because their families hold all four.",
        "when": "NO FOUNDING EVENT. They accreted DURING AND AFTER all the other migrations — the "
                "most diverse kept arriving across the Ages of Plenty, the Tetramorph, and Doubt. "
                "The DUKEDOM is the young thing, not the people: they created the office ~4516 to "
                "give themselves a voice as natural arbiters, and that act opens the Age of Renown.",
        "the_two_ladders": "RENOWN gets a family to the centre; EXPERTISE gets a person near the "
                           "Duke. Two separate ascents — admission and proximity — which is why the "
                           "technocratic senate is a meritocracy rather than a court of birth.",
        "why_the_objections_sting": "Many Astravantheliad are KIN to the cultures that dismiss them. "
                                    "A Kragh refusing a refinement on his stance is refusing a "
                                    "Kragh-descended theorist. The charge underneath is not \'what "
                                    "would you know\' but \'YOU LEFT.\'",
        "the_delegates": "Every culture has kin at the centre, which is why the Astravantheliad are "
                         "the primary delegates in every envoy. The one who meets the Kraghs may be "
                         "Kragh-blooded — an advantage and an insult at once.",
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

# PLACES_ADDENDA removed — all three entries were exact duplicates of
# MAP["regional_lore"], which is their correct home.

EVENTS["Vogen"] = {
    "year": "1136 (provisional)",
    "who": "A Vorghith general. He led a warband to control everything up to the BLEAK "
           "HIGHLANDS — the northern limit of their expansion — and went no further.",
    "signature": "Assassinating his opponents by PUBLIC EXECUTION. VOGEN'S GALLOWS is named "
                 "for the method, and the site has carried his name for some three thousand "
                 "years since. Public execution is not battlefield glory: a Kragh kills you in "
                 "open combat for honour, and Vogen hangs you in the square so that everyone "
                 "watches.",
    "cultures": ["Vorghith", "Kraghs"],
}

EVENTS["Mason-King Karalius II"] = {
    "year": "2910 (provisional)",
    "who": "Sarkopekt. Famous shipwright and builder of MASONRY CITADELS, seated at Ivory Isle. "
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
                      "you. The Voldrastel refuse to deal with him on principle; the Prezish keep "
                      "his terms on file.",
}

EVENTS["The Pincer of Dead Waters"]["cultures"] = ["Belvareth", "Sarkopekt", "Kraghs"]
EVENTS["Mason-King Karalius II"]["cultures"] = ["Sarkopekt"]

EVENTS["The Pincer of Dead Waters"]["organised_by"] = (
    "THE HIGHLANDERS, who agreed to JOIN THE MASON-KING'S MERCENARY COMPANY in exchange for his "
    "services. Payment in men, not coin — Karalius came out of the deal with a fleet and an army. "
    "The warlord did not have a stroke of genius; he had a BUDGET. Every prior assault on the Wheat "
    "Fields broke on the treeline because nobody was willing to pay Karalius' number. The one who "
    "finally was, won."
)
EVENTS["The Pincer of Dead Waters"]["significance"] = (
    "THE ONLY DEFEAT EVER RECORDED OF THE BELVARATH. They gave ground in the Wheat Fields for the "
    "first time that day — on ground that is never paved because it is hallowed. For an order whose "
    "taboo is retreat AND doubt, this is not a battle loss but a THEOLOGICAL EVENT: the standard "
    "failed the test, and every warlord ever turned back there learned it could be done. Worse, the "
    "tactic MIRRORED them — a two-pronged attack against an order whose entire discipline is holding "
    "two halves in balance. 156 years later the alministralum's edges began to break."
)
PRECEPTORY = {
    "what": "The holy order. The BELVARATH are a SUBSET of it — one militant order under the "
            "Preceptory umbrella, not the whole institution.",
    "the_draghen": "The pairing is called a DRAGHEN — a Draggath word at the centre of a "
                   "Lenavorite-named order. The faith supplied the name; the warriors supplied "
                   "the bond, and both halves are still in the vocabulary four and a half "
                   "thousand years later. A man speaks of HIS draghen, is draghen-bound, fights "
                   "AS draghen.",
    "the_pairing": "Every Belvareth is PAIRED WITH THEIR OPPOSITE ORIGIN — one Draggath-descended, "
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
                           "Belvareth have done the same thing in the same woods since the Fracture. "
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
    "one_name_between_two": "A draghen holds ONE saint-name between them. Ollanenor delivers a "
                            "name when a person gives themselves up to an order — and the "
                            "Belvareth give themselves up in twos, so one name is what comes "
                            "back. The pair is the person. A brother who loses his draghen has "
                            "lost half of his own name, and is not whole again until he is "
                            "re-bound and renamed.",
    "open": "Does the Preceptory hold other orders besides the Belvareth?",
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
    "Prezish vs Voldrastel": {
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

CULTURES["Trusteki"]["trade_role"] = (
    "THE PRIMARY TRADERS AND SUPPLIERS OF THE WORLD. This is what keeps them functioning with no "
    "martial might and relatively stable: they are INDISPENSABLE. You do not raid the people who "
    "supply you. Their safety is economic, not military — wealthy and powerful while focused on the "
    "craft, outputting to whoever is willing to purchase. They are the honest base layer every "
    "other trade culture acts upon: the Prezish corner it, the Voldrastel guard it, the Vorghith "
    "strangle it, the Ithiss fence through it, the Sarkopekt sell arms alongside it."
)
CULTURES["Trusteki"]["internal_conflict"] = (
    "ALMOST NONE. Families producing and competing in the same craft are judged BY THE MARKET, NOT "
    "BY EACH OTHER — competition is externalised onto an impartial arbiter, so there is no "
    "advantage to seize by scheming. The familial trade and craft dynasties are so old that the "
    "market is LEGIBLE: everyone understands what it needs, families step in to fill the gaps, and "
    "it is all respected by other Trusteki. NO CUNNING HERE. The structural ANTI-ISSETH: both "
    "lack a central authority, but Cunning turns that into predation and Industry turns it into a "
    "guild. It is also why the Ossensteins had to LEAVE — you cannot be a puppetmaster among people "
    "who will not play the game."
)

CULTURES["Lenavorites"]["internal_conflict"] = (
    "LOW, AND DOCTRINAL. Mostly cooperative — like Catholics vs other Christians: real debate on "
    "smaller issues, general agreement, everyone rowing in the same direction. NO ONE REFUSES TO "
    "ADMINISTRATE OR PERFORM THEIR ROLE; the machine runs. The disagreements are over "
    "CHARACTERISATION AND PRIORITY within the tetramorph — which face to weight, how a given god "
    "should be understood. Not schism: INFLECTION. And these debates are the SEED VOCABULARY OF "
    "EVERY FUTURE SCHISM — a characterisation dispute held quietly inside orthodoxy for centuries "
    "is the fault line a real break eventually cracks along. The Belvareth are one that already "
    "left: they did not reject the church, they OVER-WEIGHTED WRATH until they were a distinct "
    "order. The internal debate is the schism that has not happened yet."
)

CULTURES["Kraghs"]["warband_spectrum"] = (
    "Since PRAVAK, Kragh warbands sit on a SPECTRUM from individual skill to positional strategy. A "
    "warband's place on it is ADVERTISED — a recruiting pitch to unpledged young men choosing where "
    "to make their mark. The strategy-end warbands train almost purely in military strategy over "
    "personal prowess. Battlefield cunning is honoured; the knife in the dark is beneath them."
)

CULTURES["Astravantheliad"]["the_fund"] = (
    "ONE SHARED ACCOUNT. Complete egalitarians who are also, all of them, wealthy — the isle "
    "operates as a single pooled endowment. If you need money you withdraw; if you do not, you put "
    "in. This is not communal idealism, it is a LIQUIDITY POOL, and it does three things. Nobody "
    "accumulates, so nobody can be leveraged — their taboo about being indebted to another is "
    "enforced by the structure rather than by virtue. The fund is always deployable, because idle "
    "money returns to it, which is what lets an entire isle underwrite sixty-year research "
    "projects. And there is no such thing as an Astravantheliad debt crisis, a ruined family, or a "
    "fortune to seize: an invader takes an island, not a treasury. WEALTH IS FLAT, so it cannot be "
    "the currency of status — which leaves EXPERTISE as the only differentiator, and is why the "
    "technocracy's meritocracy holds."
)
CULTURES["Astravantheliad"]["the_army"] = (
    "MEDIOCRE AND DECENTLY EQUIPPED. Every citizen carries basic military training as part of the "
    "four-domain baseline, so they field a competent militia: everyone has had the drill, the kit "
    "is good, nobody is a specialist. Enough to hold their own island and be a real cost to invade; "
    "nowhere near enough to project force or take ground from people who do that professionally. "
    "That threshold is exactly why the office exists — a defenceless centre would be a prize and "
    "the Duke would be somebody's puppet within a generation, while a centre that could compel "
    "would arbitrate at swordpoint like everyone else. THE OFFICE IS THE INSTRUMENT OF A PEOPLE WHO "
    "CAN DEFEND BUT CANNOT COMPEL. Contrast the Drakteni: the same Industry capacity for equipment, "
    "opposite application — they forge the advantage and take ground with it; the centre equips "
    "everyone adequately and takes ground from no one. The kit is insurance, not a plan."
)

CULTURES["Voldrastel"]["doctrine"] = (
    "THE CARRY TRADE. Model: the Dutch Republic fused with 18th-century Britain. From the Dutch — a "
    "MERCHANT-REPUBLIC governed by the trading class itself, wealth from the ENTREPOT (facilitating "
    "flow, not owning production), financial instruments, defensive survival by being too costly to "
    "take and too useful to destroy, and tolerance as commercial policy. From Britain — "
    "BALANCE-OF-POWER doctrine, naval command of the routes, coalition-shifting to prevent any "
    "hegemon, and a virtue that happens to be profitable. In a world of fifteen cultures fighting "
    "over what they can HOLD, the Voldrastel win by holding NOTHING and moving EVERYTHING."
)
CULTURES["Voldrastel"]["strategy"] = (
    "STATUS-QUO ENFORCERS. They want the world's general balance MAINTAINED, because the more "
    "control their antagonists gain, the less footing and bargaining power they have. Their "
    "morality and their interest point the same way — not hypocrisy, but the structure of a "
    "carry-trade balancer: you genuinely believe in the open system because the open system is what "
    "makes you rich. FOUR FRONTS: out-manoeuvre the DRAKTENI (expansion changes the board); "
    "interdict the PREZISH (predators on the flow they guarantee); relieve the MADEKITES when "
    "needed (same front as the Drakteni — defend the victim to check the aggressor); shield the "
    "TRUSTEKI (protect the producer, protect the whole trade order)."
)
CULTURES["Voldrastel"]["limits"] = (
    "THEIR REACH IS NOT INFINITE. They oppose all destabilisation in principle but must TRIAGE. "
    "OSSENSTEINS: rarely even recognised — you cannot oppose a hand you cannot see, and their "
    "invisibility is their immunity. (The irony: the culture whose entire purpose is stopping "
    "board-owners is blind to the faction that already won.) CAILENDROFFS: currently self-contained "
    "— a threat in potential, not in motion, so no expenditure is warranted YET; but the "
    "Cailendroffs are actively recruiting toward a crusade, so the non-action is provisional. FALSE "
    "PROPHET: a spiritual threat, headed off by the Lenavorites — the church's front, not the "
    "wardens'. Implicit division of labour: the Lenavorite administration polices belief, the "
    "Voldrastel police the routes."
)
CULTURES["Voldrastel"]["pragmatism"] = (
    "They hold the Cailendroff Edict a fraud AND would take the pretender's success over his "
    "failure. A UNIFIED DRAGGATH WASTES IS AN OBJECTIVE GOOD to a culture that thrives on trade and "
    "unification: peace ends the perpetual civil war, opens the northeast to routes, and creates "
    "one negotiable partner instead of a thousand warbands. They are not rooting for the "
    "Cailendroffs — they would SETTLE for them. Legitimacy is the church's concern; the Voldrastel "
    "care about the outcome. THEY WOULD CROWN A LIAR TO CLOSE A WOUND."
)



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

# ---------------------------------------------------------------------------
# CUNNING NARRATION — how the LORE ITSELF behaves near Cunning.
# The documentation enacts the domain: a reader finding rumour where they
# expected facts is EXPERIENCING Cunning, not reading about it.
# ---------------------------------------------------------------------------

CUNNING_NARRATION = {
    "principle": "The more Cunning a culture carries, the less MECHANICAL and more HAND-WAVEY its "
                 "fact patterns. You will be told things you doubt on their face and given no "
                 "further explanation. Word count does not drop — the RATIO of fact to folklore "
                 "shifts. Trusteki are all ledger, no legend; Ithiss are all legend, no ledger.",
    "the_safeguard": "SO LONG AS THE UNRELIABILITY IS OBVIOUS IN ITS UNRELIABLENESS, it works. The "
                     "reader must always be able to tell they are being handled. A gap that reads "
                     "as lazy writing FAILS; a gap that reads as 'they would never tell you that' "
                     "SUCCEEDS. Frame the withholding — 'accounts disagree', 'the ledgers say one "
                     "thing and the songs say another' — never leave it as a blank field.",
    "not_uniform": "Cunning is not one thing narratively. FOUR MODES, and the correlation is with "
                   "WHAT KIND of Cunning, not HOW MUCH — a flat ratio would wrongly make the "
                   "Sarkopekt as hand-wavey as the Ithiss.",
    "modes": {
        "OBFUSCATION — deception is the point": {
            "cultures": ["Ithiss", "Prezish", "Vorghith"],
            "where_the_doubt_lives": "EVERYWHERE. The whole telling is suspect. Hand-wavey, "
                                     "doubtful, unexplained; the unreliable narrator worn openly.",
        },
        "INVISIBILITY — concealment, not deception": {
            "cultures": ["Ossensteins"],
            "where_the_doubt_lives": "IN THE GAPS. Not unreliable — ABSENT. What is said may be "
                                     "accurate; there simply is not much of it. You doubt the "
                                     "COMPLETENESS, not the truth.",
        },
        "THE SINGLE LOAD-BEARING LIE": {
            "cultures": ["Cailendroffs"],
            "where_the_doubt_lives": "IN ONE SENTENCE. Reliable everywhere except the one claim the "
                                     "whole culture rests on. Factual about warbands, exile, and "
                                     "recruitment — unverifiable about the bloodline. Precise, then "
                                     "a hole exactly where it matters.",
        },
        "MORAL CUNNING — not epistemic": {
            "cultures": ["Sarkopekt"],
            "where_the_doubt_lives": "IN THE VALUES, NOT THE FACTS. Their Cunning is the "
                                     "neutral-evil arms-dealing worldview, not how the story is "
                                     "told. They keep LEDGERS — massaged and self-serving, but "
                                     "present. Read a Sarkopekt entry and you get facts; the "
                                     "Cunning is in what those facts are comfortable with. "
                                     "RELIABLE-SEEMING, which is its own kind of unreliable: a "
                                     "culture defined against the honest has no particular reason "
                                     "to be truthful in its own books, and the lie would be "
                                     "plausible and unremarked. Immaculate accounts. Who is to say.",
        },
    },
}


# ---------------------------------------------------------------------------
# THE ORDER OF THE LAST PROPHET — the false religion as a MACHINE.
# Six interlocking parts, no exit, extracting hardest from the most desperate,
# defended by its own victims, invisible at the top.
# ---------------------------------------------------------------------------

FALSE_RELIGION_ENGINE = {
    "the_doctrine": "PERPETUAL INSUFFICIENCY. Early-Catholic INDULGENCES supply the transaction "
                    "(salvation is purchasable) and 'YOU WILL NEVER BE ENOUGH' makes it a "
                    "SUBSCRIPTION rather than a sale — a salvation you could complete would end the "
                    "cash flow. ONLY THE LAST TRUE PROPHET CAN SAVE YOU: you cannot reach "
                    "Esselantheum yourself (blasphemy to try) and you will never be enough on your "
                    "own, so the only path runs through him. The pitch is not 'buy this' — it is "
                    "'you are structurally incapable, and I am the only bridge.'",
    "the_social_proof": "A critique of modern Christendom: the congregation is not Christlike at "
                        "all, but they assure EACH OTHER they are on the right side of everything "
                        "because they have all — literally and metaphorically — BOUGHT IN. Doubt is "
                        "too expensive to afford: to question it is to admit you were fleeced AND "
                        "damned. The marks defend the con to protect their own investment. The "
                        "Ossensteins do not have to maintain it; the converts do it for them.",
    "the_failure_loop": "IT REINFORCES ON FAILURE, so no outcome disconfirms it. Things improve -> "
                        "the indulgences worked, buy more to maintain it. Things do NOT improve -> "
                        "you did not buy enough, AND your neighbours did not believe hard enough. "
                        "'We aren't doing well because not enough are believing in our small local "
                        "community — can't you see?' Every hardship becomes a hunt for the weak "
                        "link, so suspicion of your neighbour becomes an act of devotion: the "
                        "Inquisition's paranoia engine running at VILLAGE level, self-administered. "
                        "And the poorer a community gets, the MORE it tithes — the pump extracts "
                        "hardest from those it is hurting most.",
    "the_siphon": "THREE TIERS, IGNORANT BOTTOM AND MIDDLE. The purchaser buys believing it serves "
                  "their salvation and their church. The SHASSOLIN collect believing they are the "
                  "puppetmasters. The OSSENSTEINS siphon it up, and neither tier knows the money's "
                  "destination. The tithe never serves the payer and never even serves the church "
                  "that takes it — it climbs an invisible ladder. The Shassolin's self-delusion is "
                  "LOAD-BEARING: because the field operators genuinely believe they run it, they "
                  "sell with real conviction and there is no visible hand to trace upward. The "
                  "machine's middle managers are as fooled as the customers.",
    "the_manufactured_hardship": "Because bad times INCREASE tithing, the Ossensteins do not wait "
                                 "for hardship — they SOW IT. They own more than half the world's "
                                 "wealth and pull the strings of macroeconomic events, and now "
                                 "there is a motive: every famine, crash, and shortage they "
                                 "engineer drives desperate communities deeper into the indulgence "
                                 "engine, which pumps the money back up to them. They are not "
                                 "parasites on hard times but FARMERS of them — engineer the "
                                 "winter, sell the firewood. Common folk tell wives'-tales of "
                                 "shadowy masters who curse the harvest and rule the world's "
                                 "fortunes, and are dismissed as superstitious: the folklore points "
                                 "at something real that is not supernatural (see MYTHOS). The "
                                 "closest thing to a truth-teller in the world is treated as mad.",
    "the_theodicy_trap": "The doctrine teaches that bad times come from insufficient faith. The "
                         "truth is bad times come from the people who FUND the doctrine. The "
                         "explanation for suffering is owned by the CAUSE of suffering. And under "
                         "DIVINITY_RULE nothing is ever confirmed, so 'improvement' and 'decline' "
                         "are read into noise that the doctrine interprets in only one direction: "
                         "ALWAYS BUY MORE. There is no lived experience that escapes the frame.",
    "the_mirror": "It is the EXACT INVERSE of the Lenavorites. Same engine — permanent inadequacy — "
                  "opposite currency. The orthodox pay in SUFFERING (self-flagellation, guilt, "
                  "penance toward a worthiness never reached); the false church lets you pay in "
                  "COIN and FEEL saved. Which is why it wins converts: the same impossible goal, "
                  "with the lash swapped for a receipt and a community that congratulates you. The "
                  "excommunicated who founded Prophet's Landing did not invent a new god — they "
                  "kept the structure and made it PLEASANT, which is the most damning thing about "
                  "it.",
    "the_class_structure": "THREE TIERS, AND ONLY TWO OF THEM ARE VISIBLE TO EACH OTHER.\n"
                           "  THE BOUND — the poor work, live on church land, and are PAID IN "
                           "INDULGENCES rather than coin. Their wage is credit against a debt they "
                           "never chose, issued by the people paying them, and it can only ever "
                           "offset a running deficit. You cannot save indulgences into freedom. "
                           "Serfdom with the ledger kept in salvation — and the labour costs the "
                           "church nothing, because the currency is manufactured at will. The tithe "
                           "is the retail business; the bound labour is the real one.\n"
                           "  THE ABSOLVED — local wealth (merchants, minor lords, anyone with "
                           "coin) buys its way out instantly. Same instrument, opposite direction: "
                           "the sin is identical and only the settlement differs. NOBODY HAS TO BE "
                           "LYING for this to work. The doctrine says the debt is real and payment "
                           "discharges it; the rich simply have a faster method, and an "
                           "administrator can watch it happen and see nothing wrong.\n"
                           "  THE OWNERS — the Ossensteins are NOT the upper class. They are "
                           "outside the hierarchy entirely, holding the instrument everyone inside "
                           "is using. No Ossenstein is a bishop, a landlord, or a name on a deed. "
                           "The visible upper class is LOCAL MONEY, and local money is a CUSTOMER, "
                           "not a proprietor.",

    "who_the_absolved_are": "PREZISH, chiefly — and local Lenavorite money. The Prezish fit "
                            "because an indulgence is a NEGOTIABLE INSTRUMENT: it has a price, it "
                            "settles a debt, and it is issued by someone with every incentive to "
                            "keep issuing. They would be in that market within a week of finding "
                            "it. NOT the Madekites: they are Piety x Industry with no Cunning, "
                            "their theology holds that SUFFERING IS THE PAYMENT, and buying "
                            "absolution with coin would be the vain settlement their own taboo "
                            "forbids. They are also cash-poor by construction — quarrying frozen "
                            "tundra and pouring everything into cathedrals the Drakteni keep "
                            "besieging.",

    "the_secondary_market": "The Prezish do not merely buy indulgences — they TRADE them, holding "
                            "absolution as inventory: bulk rate from a Shassolin administrator, "
                            "retail to a merchant who needs one before a voyage. Two consequences. "
                            "(1) SECONDARY MARKETS SET THE REAL PRICE. The Shassolin issue; the "
                            "Prezish decide what it is actually worth — cornering supply and "
                            "setting prices, their cartel behaviour applied to salvation. (2) It "
                            "CORRUPTS THE INSTRUMENT FROM OUTSIDE. The Ossensteins manufacture "
                            "indulgences at zero cost, but once arbitraged the currency has a "
                            "market rate the church does not control, and the bound poor could in "
                            "principle discover what their wages are actually worth. Not a "
                            "rebellion. An exchange rate.",

    "the_orthodox_leak": "Local Lenavorite wealth quietly uses the false church's faster method — "
                         "so the instrument leaks UPWARD INTO THE ORTHODOXY. The Inquisition's "
                         "paranoia about internal conversion turns out to be CORRECT, and it still "
                         "finds nothing: the converts are not heretics, they are customers.",

    "the_kino_principle": "The wealthy are Kino from Andor — the prisoner who runs the room. His "
                          "authority over the men on the floor is real and it matters; the distance "
                          "between him and whoever owns the facility is so large it is not a "
                          "relationship at all. He is not junior management. He is INVENTORY WITH A "
                          "JOB. That is the local wealthy under the Ossensteins: rich by every "
                          "measure their neighbours can apply, buying absolution their workers will "
                          "never afford, and from above indistinguishable from the people they are "
                          "standing on. Both tiers are the product. One has a better position "
                          "inside it. (This beats a feudal-knight framing, because a knight has a "
                          "RELATIONSHIP with his lord — homage sworn, obligations both ways, a name "
                          "the lord knows. Nobody is an Ossenstein's vassal, because swearing "
                          "requires knowing who you are swearing to.)",

    "why_the_ladder_is_load_bearing": "The wealthy buying out is not a leak in the system — it is "
                                      "the part that makes the poor accept it. If nobody visibly "
                                      "escaped, the debt would look like a TRAP. Because some "
                                      "people clearly do escape, it looks like a LADDER — and the "
                                      "failure-loop supplies the explanation: if you are not "
                                      "climbing it, the fault is your faith. The wealthy think they "
                                      "have beaten the system. THEY ARE THE REASON IT WORKS.",

    "the_three_stories": {
        "The Last True Prophet": "SHASSOLIN LORE (and their converts). A genuine messenger, the only "
                                 "bridge to salvation. Sincere belief; they would die for him.",
        "The False Prophet": "ALL OTHER PIETY. A heretic and blasphemer — a schism of distance, a "
                             "con claiming access that is forbidden.",
        "The Truth": "A Wizard of Oz. Strip the curtain and there is no dark messiah and "
                     "no genuine heretic — just machinery and a paid actor. This is the "
                     "account told by those who claim to know.",
    },
}


# ---------------------------------------------------------------------------
# THE DUKE — deliberately opaque. The opacity IS the characterization.
# ---------------------------------------------------------------------------

THE_DUKE = {
    "the_role": "The STABLE, UNFLINCHING, NON-EMOTIVE force that keeps the world centred. He "
                "REIGNS, he does not rule — the fixed point the world orbits, not an active player "
                "scheming for advantage. His power is precisely that HE DOES NOT MOVE.",
    "why_opaque": "Not missing information — THAT IS WHAT HE IS. A monarch whose whole function is "
                  "to be the fixed, silent, ceremonial centre would be DIMINISHED by a personality, "
                  "a scheme, or a stated opinion. The moment the Duke wants something he stops "
                  "being the centre and becomes a faction. His blankness is his sovereignty.",
    "the_origin": "THE TECHNOCRACY CREATED IT. The Astravantheliad accreted gradually at the "
                  "centre across all the migrations — no founding moment, just the most "
                  "diverse continuing to settle there. But a culture with no domain-force "
                  "(no army that can take anything, no cartel, no church) cannot make its arbitration COUNT. So "
                  "they installed a seat: an office to curtail those not operating in the "
                  "interest of the whole, which gave them a voice in the world as its "
                  "NATURAL ARBITERS. The Dukedom is young — ~4516, which makes the founding "
                  "of the office and the beginning of the Age of Renown the same act.",
    "why_never_mighty": "The scholars were not installing a RIVAL — they were installing a "
                        "FIXED POINT THEY COULD ADVISE. A Duke with ambitions of his own "
                        "would need managing; a Duke with none needs counsel. 'Duke' rather "
                        "than King or Emperor is a SPECIFICATION.",
    "who_benefits_from_the_blankness": "His opacity was designed, by the people who benefit "
                                       "from it. The Astravantheliad worship proximity to a "
                                       "centre they built to be approachable — and the "
                                       "reason closeness can be measured by merit rather "
                                       "than favour is that they engineered a seat with no "
                                       "favour to give.",
    "why_it_makes_the_centre_a_meritocracy": "The Astravantheliad worship PROXIMITY to power, which "
                                             "only works if the Duke is a FIXED POINT — you can "
                                             "measure distance to something that stands still. An "
                                             "active schemer would make closeness about faction and "
                                             "favour; because he is opaque and unmoving, closeness "
                                             "is about MERIT and INFLUENCE. He is a mirror, not a "
                                             "face: proximity reflects YOUR standing because he "
                                             "supplies no agenda of his own to serve.",
}


# ---------------------------------------------------------------------------
# MACRO FRAME — what the world is FOR. The setting is a generator, not a stage.
# ---------------------------------------------------------------------------

MACRO_FRAME = {
    "the_premise": "The world is sufficiently big that EMPIRES ARE ALWAYS RISING AND FALLING. "
                   "Ruined empires are common, especially in Draggath. Most are forgotten — the few "
                   "still told survived BECAUSE THEY BECAME RENOWNED. Renown is the win condition "
                   "of history itself: to be remembered is to have won, in a world that forgets "
                   "almost everyone. MOST EMPIRES ARE FORGOTTEN. MAKE YOURS RENOWNED.",
    "three_axes_of_agency": {
        "WHERE ON THE MAP": "Sets the neighbours, the terrain-mood, the hostilities available.",
        "WHERE IN THE ~4,600 YEARS": "Sets which Age's conditions you play under — Fracture's chaos, "
                                     "Plenty's cooperation, the Tetramorph's zealotry, Doubt's "
                                     "paranoia, Renown's cold tension.",
        "WHICH CULTURE YOU ALIGN": "Sets your values, your enemies, your whole relationship to the "
                                   "board.",
    },
    "the_effect": "Pick a point in that three-dimensional space and you have defined the MOOD of "
                  "your game before a single action — and given your province its own back story "
                  "and its own interface with the world at the time it exists. This is the payoff "
                  "for the perspectival, gradient-based worldbuilding: because nothing is fixed "
                  "canon at the local level, a player's province slots in anywhere without "
                  "contradiction.",
    "why_the_world_map_is_lore_only": "It is not the board — it is the MENU. You read it to decide "
                                      "what kind of game you want, then generate a province that "
                                      "fits.",
    "two_tiers_of_canon": {
        "AUTHORED": "The fifteen cultures, the Ages, Draggath, Karalius, Vogen, the Pincer. These "
                    "REALLY HAPPENED — the fixed reference points, the empires already remembered.",
        "EMERGENT": "Players tell their province's story inside that world, and if a game is "
                    "remarkable enough the COMMUNITY — players within that culture, voting — "
                    "elevates it to Renown and it joins the record. Each culture accretes its own "
                    "remembered histories over time.",
        "why_it_fits": "The world FORGETS ALMOST EVERYONE, so most games SHOULD be forgotten, and "
                       "that is accurate. The few voted in earned it exactly as the fictional "
                       "survivors did. The out-of-game process MIRRORS THE IN-WORLD ONE — and the "
                       "community record of Renowned games IS the Order of the True Word made real: "
                       "the lore's central institution models the game's own archive.",
        "boundary": "OPEN — soft (community lore, authored spine authoritative), hard (voted-in "
                    "games become load-bearing), or CURATED PROMOTION (a few graduate into the "
                    "file). Curated promotion matches how the file is actually maintained.",
    },
    "domain_as_interface": {
        "thesis": "The four domains are not just in-world factions — they are the INTERFACE "
                  "LANGUAGE of the entire game. Every system the player touches is AUTHORED BY the "
                  "domain that would own it in the fiction. A circular loop: domain -> game -> lore "
                  "-> compendium -> reference -> domain.",
        "mapping": {
            "Menus, record-keeping, rules admin": "LENAVORITE (the Order of the True Word) — "
                                                  "epistles and ledgers.",
            "Combat resolution": "KRAGH — blunt, hammered, glory-tallied, the martial chronicle.",
            "Pursuits / infrastructure / tech": "TRUSTEKI — inherited craft, mastery, generational "
                                                "IP, clipped and mechanical.",
            "Doubt / extortion / sabotage systems": "ISSETH — folklore and rumour, deniable, never "
                                                    "a straight confession.",
        },
        "the_payoff": "The game TEACHES ITS OWN LORE THROUGH USE. A player learning combat absorbs "
                      "Kragh values without reading a word of fiction; someone navigating the doubt "
                      "mechanics IS BEING Ithiss. Framework fully undercurrent — felt, not read.",
        "the_discipline": "COHESION LIVES IN STRUCTURE AND BEHAVIOUR, NOT SKINS. The aesthetic is "
                          "the LEAST important part — it lives in the player's head, the art, or "
                          "customisation. The Ithiss doubt-mechanics withhold because concealment "
                          "is what Cunning IS, not because the page is painted spooky. IF THE "
                          "STRUCTURE IS RIGHT THE AESTHETIC IS OPTIONAL; IF THE STRUCTURE IS WRONG "
                          "NO AESTHETIC CAN SAVE IT. The cohesion is testable in monospace.",
        "the_single_authority": "Each domain's lore_voice / lore_medium / phonology_signature in "
                                "DOMAINS is the STYLE GUIDE FOR THE INTERFACE, not just fiction. "
                                "The loop only holds if no voice is ever authored twice — one "
                                "definition, referenced everywhere. The moment a UI element invents "
                                "its own voice instead of deriving it from the logged domain, the "
                                "loop breaks.",
    },
}


# Belvareth serve Melvanar, not the God of Gods directly:
CULTURE_AXES["Belvareth"]["sacred"] = (
    "MELVANAR (Wrath), served through the sword — faith as holy violence. They worshipped wrath "
    "before Melvanar had a written name [FUSE]"
)

# Replace the two resolved entries in OPEN_THREADS:
#   "Name the Duke. The center of the world is still unnamed."   -> DELETE
#   "Name the False Prophet."                                     -> DELETE
# and add:
OPEN_THREADS += [
    "RESOLVED: the Duke stays DELIBERATELY OPAQUE — see THE_DUKE. Not a gap.",
    "RESOLVED: the False Prophet stays deliberately unnamed, and may not be a nameable thing at "
    "all — see FALSE_RELIGION_ENGINE['the_three_stories'].",
    "Is the emergent-canon boundary soft, hard, or curated promotion? (MACRO_FRAME)",
    "Which interface layer to dial first — Lenavorite record-keeping or Kragh combat?",
]

if __name__ == "__main__":
    print(f"Renown world-lore: {len(CULTURES)} cultures, {len(DOMAINS)} domains, {len(GODS)} gods.")
    for name, c in CULTURES.items():
        print(f"  [{c['type']:<6}] {name:<16} {'×'.join(c['domains'])}")
    print(f"Culture axes: {len(CULTURE_AXES)} cultures resolved.")
    for name, ax in CULTURE_AXES.items():
        print(f"  {name:<16} lead: {ax['lead']}")


# ---------------------------------------------------------------------------
# DESIGN_ONLY — routing, not deletion.
#
# Everything here stays in this file. It is simply marked as DESIGNER-FACING so
# the generator can emit two documents from one source:
#
#   world.txt         reader   — the world as someone encountering it would meet it
#   world_design.txt  designer — everything, including the notes below
#
# The test for this list: does the entry EXPLAIN THE TRICK rather than perform it?
# Rules about how the lore behaves, why a device works, what a section is for, and
# analysis of the setting's own machinery all belong here. The reader gets the
# effect; the designer gets the reason.
# ---------------------------------------------------------------------------

DESIGN_ONLY = {
    # whole top-level structures
    "dicts": [
        "DIVINITY_RULE",        # states the rule instead of letting it operate
        "CUNNING_NARRATION",    # tells the reader which entries are unreliable
        "LORE_SEQUENCE",        # why the reading order works
        "CORE_SPINE",           # first principles of the construction
        "GOD_OPPOSITIONS",      # structural analysis of the pantheon
        "EXPANSION_HOOKS",      # product roadmap
        "OPEN_THREADS",         # unresolved design questions
        "PHONOLOGY",            # naming machinery
        "WEALTH_SHAPES",        # economic analysis of the setting
        "SPECIALISATION_DEPTH", # the tech-depth rule
        "REPUTATION",           # the matrix as a matrix
        "TERMS",                # glossary of design vocabulary
        "ARCHIVE_OPPOSITION",   # analysis of two institutions
    ],

    # individual keys inside otherwise reader-facing structures
    "keys": {
        "MYTHOS":                ["rule", "The Drakes", "The Giants of Cravencroft"],
        "MAP":                   ["naming_registers", "diagonals"],
        "THE_DUKE":              ["why_opaque", "why_never_mighty",
                                  "who_benefits_from_the_blankness",
                                  "why_it_makes_the_centre_a_meritocracy"],
        "ARCHIVE_OPPOSITION":    ["The Order of the True Word (Anumaranth)",
                                  "The Academic Halls (Astravantheliad)", "the_conflict"],
        "GODS":                  ["tell"],
        "AGES":                  ["structure", "an_age_is", "delivery", "naming_logic", "note"],
        "TIMELINE":              ["gradient_rule", "implications", "unit"],
        "MACRO_FRAME":           ["the_premise", "the_effect", "why_the_world_map_is_lore_only",
                                  "two_tiers_of_canon", "domain_as_interface"],
        "FALSE_RELIGION_ENGINE": ["the_theodicy_trap", "the_mirror", "the_siphon",
                                  "the_class_structure", "the_kino_principle",
                                  "who_the_absolved_are", "the_secondary_market",
                                  "the_orthodox_leak",
                                  "why_the_ladder_is_load_bearing",
                                  "the_failure_loop", "the_social_proof",
                                  "the_manufactured_hardship", "the_three_stories"],
        "PRECEPTORY":            ["open"],
        "TETRAMORPH":            ["function"],
        "ASTRAVANTHELIAD_PARADOX": ["why_illegible"],
        "FORMATION":             ["rule"],
    },

    # AGES["sequence"][n]["content"] duplicates TIMELINE["events"] at lower
    # resolution. Reader gets the dated chronicle; designer gets both.
    "ages_sequence_content": True,

    # EVENTS[*]["teaches"] is mechanics commentary, not lore.
    "event_keys": ["teaches"],

    # CULTURE_AXES pure-corner "note" fields restate the domain column.
    "culture_axes_keys": ["note", "lead"],
}


# ---------------------------------------------------------------------------
# PLACE_OWNERS — which culture's profile a place belongs in.
#
# The reader meets a place inside the culture that explains it, rather than
# reading a gazetteer before meeting anyone. Section 4 keeps only the shape of
# the world: the corners, the sea, and how places are named.
# ---------------------------------------------------------------------------

PLACE_OWNERS = {
    "Kraghs":          ["Draggath Wastes", "Bleak Highlands", "Glen of Pravak", "Cravencroft"],
    "Trusteki":        ["Blighthold", "Scarlet Forest", "Coloured Mountains"],
    "Ithiss":        ["Dreadwood", "Crag Pass"],
    "Lenavorites":     ["Lenaveron", "Tombs of the Old Gods"],
    "Belvareth":        ["Lost Woods", "Wheat Fields"],
    "Vorghith":        ["Vogen's Gallows"],
    "Drakteni":        ["Heathport", "Drakenheart", "Hermit's Row"],
    "Prezish":         ["Bay of Pigs", "Marrow Shoals"],
    "Shassolin":       ["Shallow Mire / Quiet Hollow", "Strait of Sorrow"],
    "Madekites":       ["Fair Whitewood"],
    "Cailendroffs":    ["Cailendroff Isles"],
    "Sarkopekt":       ["Ivory Isle", "Dead Waters", "Bay of Lost Hope",
                        "Wharf of St. Brannoch"],
    "Ossensteins":     ["Prophet's Landing"],
    "Voldrastel":      ["The Twelfth Reach"],
    "Astravantheliad": ["Vaelohk"],
}

# Places with no culture — they stay in section 4.
PLACE_UNOWNED = ["Sea of Ash", "Weary Mountains", "Lemstet Bay", "Crooked Bay", "Flat Pass",
                 "The Duchy's Mouth", "Bay of Renown"]


# ---------------------------------------------------------------------------
# PROSE — reader-facing openers. The only place in this file written to be READ
# rather than referenced. Everything else is data; this is the voice.
# ---------------------------------------------------------------------------

PROSE = {
    "THE PREMISE": (
        "Four and a half thousand years ago the world broke, and it has been filling the "
        "silence with empires ever since.\n\n"
        "They do not last. Walk the Draggath Wastes and you will cross the bones of a dozen "
        "of them in a day — foundations under the dust, a gate standing in open country with "
        "no wall left to hold, a road that goes somewhere that is no longer there. Every one "
        "of them was certain. Every one of them had a banner and a boast and a name its "
        "people would have died for, and did.\n\n"
        "Nobody remembers what they were called.\n\n"
        "A handful are remembered. Not the largest, not the richest, not even the ones that "
        "lasted longest — the ones that did something the world could not put down. "
        "Draggath, whose name became the word for empire and then the word for ruin. Vogen, "
        "who took the north and left a gallows where his name should be. Karalius, who never "
        "fought a battle and decided one. These are not the great; they are simply the "
        "remembered, and in a world this forgetful the two have become the same thing.\n\n"
        "That is what is on offer. Not conquest — conquest is common, and the wastes are "
        "full of men who managed it. Not wealth; the wealthiest people alive cannot be named "
        "by anyone. What is on offer is RENOWN: to be one of the few the world does not "
        "misplace.\n\n"
        "Most empires are forgotten. Make yours renowned."
    ),

    "THE WORLD": (
        "From the northern cliffs it is the Sea of Drakes, and the men there will tell you "
        "why ships do not come back. From the pilgrim coast it is the Sea of Miracles, and "
        "they will tell you what happened there, and when, and to whom. From the eastern "
        "shore it is the Sea of Damnation, which is where the damned are sent — though what "
        "is actually out there is a war fleet and a company of mercenaries who will not say "
        "who is paying them. The water does not care. It is wide enough that all three are "
        "describing something true.\n\n"
        "Around it, four corners and a centre. Ice and bad soil in the north-east, where the "
        "old empire died and the warbands still fight over what killed it. Mountains and "
        "mines in the north-west, where a people who survived a plague of the earth itself "
        "now supply half the world. Warrens and shoals in the south-west, where there is no "
        "law and never has been. Cathedrals and cold in the south, where a church that no "
        "longer governs its own frontier is still certain it does.\n\n"
        "And in the middle, an island the world is named for, where the Duke sits and says "
        "nothing, and everyone who matters is trying to stand nearer to him."
    ),

    "HOW PEOPLES FORM": (
        "Ask anyone in the world what they are and you will get one of four answers, or a "
        "mixture of them.\n\n"
        "Some live for GLORY, and hold that a life is measured by what it dared. Some live "
        "by GUILE, and hold that the honest are simply the slow. Some live for LEGACY, and "
        "will spend four generations perfecting a joint no one will ever see. Some live in "
        "DEVOTION, and give the self up entirely, name and all.\n\n"
        "These are the domains. They are not nations or religions or races. They are the "
        "four things a people can decide matter most, and everything else — how they are "
        "governed, who inherits, what they bury their dead with, what they cannot forgive — "
        "falls out of that one choice.\n\n"
        "Four peoples were brought to the four corners in the age before the count, and each "
        "made one of those choices. Then the world broke, and they moved, and they met each "
        "other. Fifteen peoples stand now where four once did, and every one of them is a "
        "record of who met whom, and on what terms."
    ),

    "THE FIFTEEN": (
        "Fifteen peoples, and not one of them arrived at what they are on purpose.\n\n"
        "They are set out here the way the world would hand them to you — not four, then six, "
        "then four, but a trade and a faith and a war and a court, with the people who make "
        "each of those things possible standing inside it. Some hold one domain and have "
        "spent four thousand years finding out what that costs. Some hold three. None of them "
        "is a compromise: two peoples who share a domain will still hate each other over what "
        "it is FOR, and it is always the shared half they fight about, never the different "
        "one.\n\n"
        "None of them is the hero. Several of them think they are."
    ),

    "THE RECKONING": (
        "The Order of the True Word has counted every year since the world broke, and "
        "measures them in Trusteki harvests, because when the counting began nobody could "
        "agree on anything else.\n\n"
        "Five ages have passed under that count. Each began because the one before it had "
        "failed — war answered by patience, patience answered by faith, faith answered by "
        "rot, and rot answered at last by the quiet, poisonous balance we are standing in "
        "now.\n\n"
        "Nobody living through an age knows they are in one. The names were all given "
        "afterwards, by clerks."
    ),

    # openers for the four culture groups
    "THE FOUR HEARTLANDS": (
        "These four made their choice before there was a world to make it in, and have "
        "spent every year since finding out what it costs."
    ),
    "THE SIX PAIRS": (
        "Two domains in one people. Not halved — doubled, and pulling."
    ),
    "THE FOUR POLYMATHS": (
        "Three domains. Enough to do almost anything, and enough to be trusted by almost "
        "no one."
    ),
    "THE CENTRE": (
        "All four, and nothing of their own."
    ),
}


# ---------------------------------------------------------------------------
# THREADS — how the fifteen are introduced.
#
# Not a taxonomy. Each thread opens on a thing the world HAS — a trade, a
# faith, a war, a court — and the peoples arrive because that thing requires
# them. A reader meets a culture at the moment it becomes necessary.
# ---------------------------------------------------------------------------

THREADS = [
    ("WHAT THE WORLD IS MADE OF",
     ["Trusteki", "Ithiss", "Prezish", "Voldrastel"]),
    ("THE FAITH, AND ITS BREAKING",
     ["Lenavorites", "Madekites", "Belvareth", "Shassolin"]),
    ("THE WAR THAT DID NOT END",
     ["Kraghs", "Vorghith", "Drakteni", "Cailendroffs", "Sarkopekt"]),
    ("THE CENTRE",
     ["Astravantheliad", "Ossensteins"]),
]

PROSE.update({
    "WHAT THE WORLD IS MADE OF": (
        "Everything in the world was made by somebody, and almost all of it was made in the "
        "north-west.\n\n"
        "The Trusteki survived a plague of the earth itself and came out of it as the people "
        "who supply everyone. They have no army worth the name. They have never needed one — "
        "you do not burn the farm that feeds you, and every court in the world knows it.\n\n"
        "But goods move, and anything that moves can be taken. In the south-west there is no "
        "law and never has been, and what the Ithiss take has to be sold by somebody who "
        "looks respectable. The Prezish look extremely respectable. And where a cargo can be "
        "taken it can also be guarded, for a fee, by people who have made a virtue of "
        "guarding it.\n\n"
        "Four peoples, one road. They need each other exactly as much as they hate each other."
    ),
    "THE FAITH, AND ITS BREAKING": (
        "There are four gods you may approach and one you may not.\n\n"
        "The four stand around a throne. Wrath, Peace, Balance, and the Saints — four faces "
        "turned outward, and the thing behind them has a name that is blasphemy to speak. "
        "The Lenavorites built an administration around that arrangement so vast it took a "
        "thousand years to grow and has been quietly failing at the edges ever since.\n\n"
        "What broke off did not stop being faithful. It stopped being reachable — and out "
        "past where the letters no longer arrived, other things grew in the same soil. A "
        "people who build cathedrals under siege because the suffering is the point. An "
        "order in a wood that kills the pilgrims who come to it, and is entirely sincere. And "
        "a church on a warm archipelago that will sell you access to God, and never quite "
        "finish selling it."
    ),
    "THE WAR THAT DID NOT END": (
        "Draggath was the word for empire before it was the word for ruin.\n\n"
        "When it fell, the fighting did not stop — it simply ran out of prizes. Every "
        "generation fought over less than the last had, and the fighting is what made it "
        "less. The Kraghs are still there, still training, in the dust of the thing they "
        "destroyed.\n\n"
        "Everything downstream of that fall is a different answer to it. Men who refuse to "
        "fight you and strangle you instead. Men who decided that if you cannot hold a "
        "continent you should build ships and take another. Men who follow a prince claiming "
        "a bloodline nobody can trace across four thousand years, and who believe him. And "
        "men who worked out that in a world this violent, the reliable money is not in "
        "winning — it is in selling."
    ),
    "THE CENTRE": (
        "In the middle of the sea there is an island where nobody is from.\n\n"
        "Everyone came here. Families that arrived Kragh, or Trusteki, or from somewhere "
        "with no name left, and did not stop being those things but stopped being ONLY "
        "them. Their children can fight a little, trade a little, recognise the four faces, "
        "and talk their way out of most rooms — and then spend sixty years on one small "
        "problem inside one hall, because that is what earns you a seat nearer the Duke.\n\n"
        "The Duke says nothing. That is the office.\n\n"
        "And somewhere out past all of it are families nobody can name, who are said to own "
        "more of the world than the Dukedom does. There is no proof of this. There is a great "
        "deal of talk."
    ),
})


# ---------------------------------------------------------------------------
# OVERVIEW — the one-slot opener. Place, history, and people in a single
# passage, instead of a region line, a stat block, and a paragraph. When a
# culture has one, the reader edition leads with it and drops the region line.
# ---------------------------------------------------------------------------

OVERVIEW = {
    "Voldrastel": (
        "To the far north-west, across the centre isle, lies an archipelago — the Twelfth Reach, "
        "held by the Voldrastel. A people founded on the ideals of fairness and justice, they are "
        "wardens of the seas and of the indefensible, promoting peace and stability by any means "
        "necessary. To travel the seas under the safety of the Voldrastel comes at a price. One "
        "must pay tolls, or hire them to transport cargo, as they out-manoeuvre the Drakteni, "
        "interdict the Prezish, assist the Madekites, and shield the Trusteki. They generate gold "
        "without production. Their value is their presence."
    ),
    "Sarkopekt": (
        "Off the coast of Lenaveron, the Wharf of St. Brannoch operates as a natural sanctuary, "
        "allowing a merchant class of city-states, warbands, and travelling nomads to work as "
        "freelancers and arms-dealers, with small nodes in every corner of the world — from the "
        "Bay of Lost Hope to the shores of the Bleak Highlands. These people are known as the "
        "Sarkopekt. Run by merchant kings and border princes, striking deals of protection, a "
        "supply of arms, or hired freelancers as a standing army, living in the moral ambiguities "
        "of others' objectives and desires, for a steep price. These people will tear wealth from "
        "flesh, given the chance."
    ),
    "Cailendroffs": (
        "Close by in the isles, the Cailendroffs have been exiled since the Great Fracture, over "
        "four thousand years ago, long scheming the return of their monarch to the Draggath throne "
        "— whom they believe is the last surviving bloodline of the oldest dynasty. The "
        "Cailendroffs believe they are direct descendants of the warrior-prophet Cailen, one of the "
        "old gods, who chose Draggath as Emperor. These people believe they are the last true way "
        "to unite the Kraghs, and are preparing their armies for crusade, converting as many as "
        "they can to reinstate the Scion of Draggath over the Water."
    ),
    "Ossensteins": (
        "In the shadows of every important academic hall, administrative building, and public "
        "forum, the Ossensteins are rumoured to exist. It is believed they own more than half the "
        "wealth in all of Vaelohk, and that they are the handlers of the False Prophet — creating "
        "disasters and catastrophes to profit and to influence."
    ),
    "Astravantheliad": (
        "In the centre lies a large isle, Vaelohk, home to those who travelled through the Sea of "
        "Drakes, survived the doldrums of the Lonely Sea, and saw miracles on the Sea of Miracles. "
        "From there the Astravantheliad rose, embracing all knowledge, generalising in all works "
        "and walks of life, continuously researching and seeking mastery in life. With this came "
        "great influence, which was harnessed by the Duke — whose authority is granted by the "
        "Astravantheliad as a neutral arbiter to all cultures."
    ),
    "Vorghith": (
        "Many Ithiss of the Dreadwood, shipwrecked or imprisoned, found venture in a world where "
        "fighting in the open was expected — glory prioritised. From the shadows the Vorghith rose "
        "the night, attacking the Kraghs in their sleep and behind their front lines, causing fear "
        "and disrupting the supply lines of those who cross them. The Kraghs, never knowing friend "
        "from foe, retreated from the prison fortress and bay. From there a wave of terror spread: "
        "raiding settlements in the night, burning crops and granaries, razing infrastructure, and "
        "capturing neighbouring leaders to execute them in the prison's square — Vogen's Gallows. "
        "The Vorghith refuse a fair fight and evade any sustained skirmish, always retreating into "
        "the towns they will strike that night."
    ),
    "Drakteni": (
        "West of the Wastes, Trusteki who had run from the disease-ridden peninsula of Blighthold "
        "found Kraghs escaping the war-torn desolation of the wasteland behind them. Together they "
        "settled a small continent rich with mines, erecting siege works and blast furnaces to "
        "construct equipment of war, eager to expand their territory. The youngest of cultures, "
        "these people focused — erecting a martial hierarchy, building armaments, siege craft and "
        "professional soldiery into a way of life. The expansion of their territory grew into their "
        "greatest edict, laying campaigns against the Kraghs in Hermit's Row and besieging the "
        "Madekites in the frozen, desolate cathedral fortresses of Fair Whitewood."
    ),
    "Belvareth": (
        "South of the Draggath Wastes lie the Bleak Highlands, rough terrain suitable for smaller "
        "warbands who pledge fealty to larger ones. The most determined Kraghs, who sought glory "
        "and rich land, marched south to the Wheat Fields — a place once known for its fertile "
        "soil, now a perpetual battlefield in an attempt to lay claim to the Lost Woods, which are "
        "fervently protected by the Belvareth, the Order of the Preceptory of Melvanar. The Lost "
        "Woods are hallowed ground to those who are pious, and the Belvareth were formed by the "
        "most devout of the old gods and the Kraghs who sought a new way of life. Together they "
        "pair, in order to train in body and spirit and defend this sacred site from all outsiders "
        "of any kind."
    ),
    "Madekites": (
        "Other pious fled into the frozen forest of Fair Whitewood, rich with tundra and forestry, "
        "during the fall of the old gods. They sought to redeem themselves, labouring to prove "
        "their devotion, suffering as a form of worship — all of it serving to reconstruct the "
        "wonders of the old gods, seeking perfection from stone and the ancient techniques used to "
        "raise cathedrals and citadels that insulate them from all foreign influence, reach, and "
        "affront. They build defence from devotion, in the desolate frozen tundra, chasing a vain "
        "perfection."
    ),
    "Trusteki": (
        "The Trusteki settled in what is now known as Blighthold. During the great famine the "
        "Trusti fled the Coloured Mountains and settled, focusing their efforts on evolving their "
        "techniques, seeking mastery of their pursuits, and adapting to the changing climate of the "
        "Blight. From that blight red trees emerged from diseased, red soil, growing to the size of "
        "Old Wood in a fraction of the time. The Trusteki continued to refine their craft, passing "
        "their knowledge each generation down the family tree. They formed democratic republics, "
        "built infrastructure, and elected those who served the interests of their people. They "
        "created large shipyards and supply lines, connecting their craft to the world for an "
        "honest price. This wealth and abundance created opportunity for those less dependent on "
        "moral quandaries."
    ),
    "Ithiss": (
        "The Ithiss have long survived as a people in the Dreadwoods, originally living in "
        "underground cities before the Dreadwoods grew. The people of the underground cities "
        "rejected the god Clypso, who in return planted a seed of doubt that would never be "
        "unsown. A vicious aristocracy ensues in an otherwise lawless land, neighbouring guilds "
        "and brotherhoods destabilising their opponents and razing settlements of those who are "
        "too powerful. The Ithiss may not create supply lines or fight for glory, but they strike "
        "fear and alter the way of life for their neighbours. The Ithiss do what serves their "
        "interest, especially when it hurts others."
    ),
    "Prezish": (
        "Some who fled that way of life found opportunity in trade, fencing stolen goods, or "
        "brokering deals in back rooms — they are the Prezish. They roamed north into the Marrow "
        "Shoals, working with migrating Trusteki, helping them navigate the waters, for a steep "
        "price in gold or an idle threat of being thrown overboard. The Prezish grew an ecosystem "
        "that controlled trade routes, set prices, and cornered markets. Many become pirates who "
        "profit from deception, threat of force, sabotage, and blackmail. A Prezish is always "
        "interested in a negotiation — of course, if it fails, they will interdict. Nothing crosses "
        "the waters without them knowing, or taking a cut."
    ),
    "Shassolin": (
        "Others moved east out of the Dreadwood, finding marsh and pious people seeking refuge, "
        "whose journey named the "
        "Strait of Sorrow. The Shassolin found religion in its despondency. They formed a new "
        "order — one of a new prophet, the last prophet, capable of speaking to the God of Gods "
        "himself, knowing and uttering its name, Esselantheum, and carrying messages directly to "
        "him. Missionary work is perpetual, seeking more to convert, to tithe, and to offer "
        "indulgences for their lack of faith. Unfortunately, it never seems to be enough."
    ),
    "Lenavorites": (
        "In the corner to the far east lie the Tombs of the Old Gods: vast ancient ruins of gothic "
        "basilicas and beautiful monuments to gods whose names have long been forgotten. From that "
        "cultural hearth these people dispersed — north into the Lost Woods, south into the deeper "
        "tundra to find Fair Whitewood, west across the Strait of Sorrow, or into the mountains, "
        "where the first record ever set down in all of Vaelohk was its name: Lenaveron. The "
        "Lenavorites are a self-flagellating, unforgiving people, eager to regain their lost "
        "devotion, seeking piety through any means. Tithe. Spread the gospel. Offer yourself as a "
        "missionary, or a martyr. And most importantly: record it. From the Lenavorites came a "
        "large papal institution of administration. The Inquisition of Ollanenor taught the way of "
        "life and assigned your role in it by assigning your name according to a saint, forgoing "
        "all prior sense of self."
    ),
    "Kraghs": (
        "In the Draggath Wastes there once stood an empire whose monarch reigned as the longest "
        "and largest dynasty in all of Vaelohk. Then a great famine swept Draggath, and a great "
        "fracturing occurred, and the empire turned into civil war — each city-state and warband "
        "fighting over shrinking tillable, fertile soil. From that civil war arose the Kraghs, a "
        "people of prowess. They rule as iron-fisted leaders, treasuring martial training and "
        "strength above all else, settling disputes by battle, eager to prove themselves against "
        "their neighbouring counterparts. Plunder and vassals lie waiting for those who succeed in "
        "the ruins of the Draggath Wastes — an ancient empire's remains scattered across desolate, "
        "sandy soil."
    ),
}


# ---------------------------------------------------------------------------
# WEALTH_SHAPES — the world can only see DISTRIBUTION, never AGGREGATE.
# ---------------------------------------------------------------------------

WEALTH_SHAPES = {
    "the_instrument": "Nobody in the world has a view of total wealth. They have the people in "
                      "front of them. So the culture with the highest MEDIAN reads as the richest, "
                      "and a culture whose wealth sits with forty invisible families reads as "
                      "nothing at all. The Ossensteins are not hiding cleverly — they are NOT "
                      "MEASURABLE by the only instrument anyone has.",
    "Ossensteins": "Highest TOTAL by far — believed to hold more than half the wealth of Vaelohk. "
                   "Median is meaningless; there may be forty of them. A culture whose wealth "
                   "statistic is aggregate is not a society, it is a holding.",
    "Astravantheliad": "Highest MEDIAN, modest total — one isle. Everyone comfortable, nobody "
                       "destitute, nobody a magnate. Visibly strange in a world of warbands and "
                       "serfs, and resented about as often as admired: a whole island of people "
                       "who have never wanted for anything, arguing about geometry. MOST OF THE "
                       "WORLD ASSUMES THEY ARE THE WEALTHIEST CULTURE, and the assumption is "
                       "reasonable on the evidence available.",
    "Trusteki": "Second-highest median, and a different mechanism: EARNED AND INHERITED BY LINEAGE, "
                "so the floor is high but families genuinely differ — an old craft-line is richer "
                "than a new one. Prosperity, where the centre has endowment.",
    "the_two_answers": "The centre and the Ossensteins are opposite answers to one question: what "
                       "do you do with wealth? CIRCULATE ALL OF IT, or WITHDRAW ALL OF IT. The "
                       "Ossenstein hoard is money removed from circulation and unaccounted for — "
                       "which is why nobody feels rich anywhere else. Half the world's money is not "
                       "in the world. Everyone's poverty has a cause nobody can name.",
}


# ---------------------------------------------------------------------------
# SPECIALISATION_DEPTH — domain count is inverse to how deep you can reach.
# ---------------------------------------------------------------------------

SPECIALISATION_DEPTH = {
    "rule": "Depth is inverse to breadth. Two domains means you reach the top of both trees; four "
            "means you cap out mid-tier everywhere. Same craft capability in principle, a fraction "
            "of the specialisation in practice.",
    "Pure":   "Deepest possible in one domain. Nobody out-techs a pure corner in its own lane.",
    "Pair":   "Deep in two. The Drakteni hold higher tech access than the centre for exactly this "
              "reason — articulated plate, poleaxes, estocs, siege trains, all of it bought with "
              "the breadth they gave up.",
    "Triple": "Competent in three, top of none. Versatile, never dominant.",
    "Centre": "Present in four, unremarkable in all.",
    "the_inversion": "The centre LOOKS like the most capable culture — every domain, best educated, "
                     "every option available. Mechanically it is the least capable at anything "
                     "specific. The breadth is a CEILING, not an advantage, and it is exactly why "
                     "influence is the only power they have: unable to out-build, out-fight, "
                     "out-scheme or out-preach anyone, they broker between people who can.",
}


# ---------------------------------------------------------------------------
# POSITIONS — a coarse grid so directional prose can be checked, not guessed.
#
# Origin (0,0) is Vaelohk, the centre isle. +x is east, +y is north.
# These are RELATIVE PLACEMENTS for bearing arithmetic, not map coordinates.
#
# The overviews position themselves against each other ("west of the Wastes",
# "others moved east"). That reads as a journey — and it breaks the moment a
# thread is reordered, because "east" was measured from whoever used to come
# before. bearing() lets the generator check every directional phrase against
# the culture actually preceding it in reading order.
# ---------------------------------------------------------------------------

POSITIONS = {
    # centre
    "Vaelohk":                (0, 0),
    # north-west — Industry
    "Blighthold":             (-3, 2),
    "Scarlet Forest":         (-3, 1),
    "Coloured Mountains":     (-4, 3),
    "Fair Whitewood":         (-1, 3),
    # north-east — Prowess
    "Draggath Wastes":        (3, 3),
    "Bleak Highlands":        (3, 2),
    "Glen of Pravak":         (2, 3),
    "Cravencroft":            (4, 3),
    "Hermit's Row":           (2, 2),
    "Vogen's Gallows":        (4, 2),
    "Heathport":              (1, 2),
    "Drakenheart":            (1, 3),
    "Dead Waters":            (2, 1),
    # south-west — Cunning
    "Dreadwood":              (-3, -3),
    "Crag Pass":              (-3, -2),
    "Marrow Shoals":          (-2, -2),
    "Bay of Pigs":            (-3, -1),
    # south / south-east — Piety
    "Lenaveron":              (2, -2),
    "Lost Woods":             (1, -3),
    "Wheat Fields":           (1, -2),
    "Tombs of the Old Gods":  (4, -3),
    "Strait of Sorrow":       (0, -3),
    "Shallow Mire / Quiet Hollow": (-1, -3),
    "Wharf of St. Brannoch":  (3, -1),
    # islands
    "Ivory Isle":             (1, 1),
    "The Twelfth Reach":      (-2, 2),
    "Cailendroff Isles":      (3, 0),
    "Prophet's Landing":      (-1, -1),
    "Bay of Lost Hope":       (-2, 0),
    "Sea of Ash":             (0, -4),
}

# Where each culture is measured FROM, for bearing arithmetic.
CULTURE_SEATS = {
    "Trusteki":        "Blighthold",
    "Ithiss":          "Dreadwood",
    "Prezish":         "Marrow Shoals",
    "Voldrastel":      "The Twelfth Reach",
    "Lenavorites":     "Lenaveron",
    "Madekites":       "Fair Whitewood",
    "Belvareth":       "Lost Woods",
    "Shassolin":       "Shallow Mire / Quiet Hollow",
    "Kraghs":          "Draggath Wastes",
    "Vorghith":        "Vogen's Gallows",
    "Drakteni":        "Drakenheart",
    "Cailendroffs":    "Cailendroff Isles",
    "Sarkopekt":       "Wharf of St. Brannoch",
    "Astravantheliad": "Vaelohk",
    "Ossensteins":     "Prophet's Landing",
}
ARTISTIC_REGISTER = {
    "Kraghs": "ANCIENT ART, and mostly PROPAGANDA. History told in relief and frieze: victories, "
              "the longest-reigning warlords, the great deeds — with folklore worked into the "
              "record until the two cannot be separated, the way the ancient Greeks did it. Nobody "
              "carves a defeat. A CULTURAL GRADIENT runs through them: Egyptian at the oldest and "
              "most monumental end, then Roman, then English, then Highlander at the fringe — the "
              "same people at four distances from the fallen empire.",
    "Belvareth": "GOTHIC HORROR. The register their god deserves.",
    "Drakteni": "THE PRINTING PRESS. The only culture that can mass-produce a claim — history "
                "set in type, distributed, and identical in every copy.",
    "Vorghith": "CAVE PAINTINGS. Most do not survive, and nothing was made to.",
    "Voldrastel": "RENAISSANCE.",
    "Astravantheliad": "ENLIGHTENMENT.",
    "Cailendroffs": "NEOCLASSICAL — a revival style, which is the whole claim in a visual idiom: "
                    "the deliberate imitation of an antiquity they say they descend from.",
}

NAMED_PERSONS = {
    "rule": "HISTORICAL ONLY. No living individual is named anywhere in the lore — not the Duke, "
            "not the prince, not the False Prophet. The people who have names are the people the "
            "world has already finished with.",
    "who_remembers": "AND EACH CULTURE REMEMBERS ITS OWN. There is no shared roll of great "
                     "figures. The Kraghs carve Draggath and Pravak; the Vorghith keep Vogen; the "
                     "Sarkopekt keep Karalius. Nobody keeps anybody else's — a renowned name "
                     "travels only as far as the people who profit from telling it.",
    "why": "Renown is the win condition of history, so a name in the record is a RESULT, not "
           "furniture. Naming the living would spend that currency on people the world has not "
           "finished judging. It also keeps the present tense open: every seat that matters — the "
           "Duke, the prince, the Prophet — is occupied by someone the reader can fill in, or a "
           "player can become.",
    "the_named": ["Draggath (last monarch; empire, dynasty, land)",
                  "Cailen (old god; the Draggath monarch was his warrior-prophet)",
                  "Trusti (old god of the Trusteki)",
                  "Clypso (old god the Ithiss rejected)",
                  "Pravak (Kragh warband-leader, early Fracture)",
                  "Vogen (Vorghith general, 1136)",
                  "Mason-King Karalius II (Sarkopekt shipwright, ~2910)",
                  "the four greater deities, and Esselantheum"],
}



# Heraldry — 'primary' is the culture's principal charge/beast.
# Kept as a dict so secondary charges, tinctures, ordinaries, and mottos
# can be added later without a schema change.

# Pure corners
CULTURES["Kraghs"]["heraldry"]          = {"primary": "Lion"}
CULTURES["Trusteki"]["heraldry"]        = {"primary": "Beaver"}
CULTURES["Ithiss"]["heraldry"]          = {"primary": "Fox"}
CULTURES["Lenavorites"]["heraldry"]     = {"primary": "Pelican"}

# Pairs
CULTURES["Vorghith"]["heraldry"]        = {"primary": "Raven"}
CULTURES["Shassolin"]["heraldry"]       = {"primary": "Mantis"}
CULTURES["Prezish"]["heraldry"]         = {"primary": "Octopus"}
CULTURES["Madekites"]["heraldry"]       = {"primary": "Stag"}
CULTURES["Drakteni"]["heraldry"]        = {"primary": "Ox"}
CULTURES["Belvareth"]["heraldry"]       = {"primary": "Tree"}

# Triples
CULTURES["Cailendroffs"]["heraldry"]    = {"primary": "Rooster"}
CULTURES["Sarkopekt"]["heraldry"]       = {"primary": "Wolf"}
CULTURES["Ossensteins"]["heraldry"]     = {"primary": "Spider"}
CULTURES["Voldrastel"]["heraldry"]      = {"primary": "Sea Eagle"}

# Center / all four
CULTURES["Astravantheliad"]["heraldry"] = {"primary": "Owl"}




PROSE["THE HOOK"] = (
    "Four and a half thousand years ago the world fractured, shattering dynasties, "
    "overturning climates, forcing migrations, and it has been filling the silence "
    "with forgotten empires ever since.\n\n"
    "However, these empires do not last. Walk the Draggath Wastes and you will cross "
    "the ruins of abandoned cities of once-great empires — foundations under the "
    "dust, a gate standing in open country with no wall left to hold, a road that "
    "leads to an empty place: every one of them was once a certain claim. Every one "
    "of them had a banner, an edict, a value and a name its people would have died "
    "for, and did.\n\n"
    "Nobody remembers their name.\n\n"
    "There are some who have been remembered. Not the largest, nor the richest, nor "
    "the most dominant; but the ones that did something the world could not forget. "
    "Draggath, whose name became the word for empire, for everlasting monarchy, and "
    "then the word for ruin. Vogen, who outmaneuvered the strong and left a gallows "
    "where his name once was. Karalius, who never fought his own battles yet decided "
    "many. These are not the great — they are the remembered. Yet, in a world this "
    "forgetful, the two have become the same thing.\n\n"
    "That is what is on offer. Not conquest — conquest is common. Empires rise to "
    "their zenith and fall with the same certainty as the sunrise, and the wastes "
    "are full of the men who managed it. Not wealth; the wealthiest people alive "
    "cannot be named by anyone, hiding in the shadows. What is to be claimed is "
    "RENOWN: to be one of the few empires the world does not misplace.\n\n"
    "Most empires are forgotten. Make yours renowned."
)

PROSE["THE PREMISE"] = (
    "The world of Renown, called Vaelohk, broke apart almost five thousand years "
    "ago, ending the Age of Darkness. With the end of an age came rampant storms "
    "that raised water, carved rock, and shifted climate and biome, causing great "
    "migration and upheaval.\n\n"
    "Before it sat the longest-reigning empire in the world of old — a name so "
    "ancient that the land, the dynasty and the monarch all shared it: Draggath. "
    "Within its reach the empire's land turned to desert, badland and bleak "
    "highland, causing a Great Fracturing within its peoples. This turned a great "
    "society of valour and honour into a civil war amongst city-states, nomadic "
    "tribes and powerful warbands.\n\n"
    "And so began the Age of Prowess.\n\n"
    "Deep in the Coloured Mountains, an ancient people believing in the deity of "
    "plenty, Trusti, migrated east to an unknown land to escape a blight caused by "
    "the dark storms. For centuries the Trusti cooperated, learning and passing "
    "down ancient techniques each family generation, creating a lineage of craft. "
    "Over time these people developed beyond subsistence farming and created a "
    "society of crafters, traders and merchants, all working in the best interest "
    "of its community. Following the blight, an Age of Plenty had begun. The red "
    "soil left over from the blight raised scarlet forests that grew to the size of "
    "ancient trees within a generation, and with it came shipyards, migrations, "
    "trade and wealth. The peninsula of Blighthold became a beacon of affluence, "
    "which created much attention.\n\n"
    "An ancient, sparsely populated, arid land of the south-western dunes was "
    "occupied only by the most cunning. These were the people of Clypso — a people "
    "of night. Living under the sands was hard rock, cut and chiselled into "
    "underground catacombs, buildings and customs-houses to sleep in and to avoid "
    "the dangerous heat of Clypso's Wrath: a legend of ancient history, the revenge "
    "of the demigod upon whom they cast doubt.\n\n"
    "That is, until the great storms came and never stopped. First the wells "
    "overflowed. Then so did the tunnels. The Ithiss of Clypso left their sunken "
    "catacombs to find the landscape changing into a lush forest, and they began to "
    "settle above ground. But the Ithiss were untrusting, and soon began stealing "
    "from one another in the night, hiding into the forests to count their spoils. "
    "To survive, brotherhoods, guilds and syndicates formed, levying power to "
    "control the flow of goods in their territories, and with wanton disregard "
    "punishing those who attempted to steal from them."
)


PROSE["THE PREMISE"] += (
    "\n\n"
    "Long ago, in the place now known as the Tomb of the Old Gods, was a "
    "pharisaical people, arrogant, legalistic, and vain. The Essels had built a "
    "civilisation of worship and adoration, sculpting, carving, and erecting the "
    "world's tallest and grandest cathedrals and basilicas.\n\n"
    "Over time, the Essels' vanity grew, and with it came its laxity. Eventually, "
    "the gods of old disappeared from the lips of its Pharisees, and in response, "
    "their names became sacrilege to merely mention, fearing the penance of their "
    "acknowledgment.\n\n"
    "As the storms rose over the mountains, the civilisation once pious left their "
    "golden cities as ash fell from the sky. These people migrated across the sea "
    "of ash into the boxed mountains of Lenaveron, where the Lenavorites issued "
    "their first record — the name of its home.\n\n"
    "The Lenavorites, over time, began to focus their efforts on history, record "
    "keeping, and the formation of the Truth. Soon, new gods were born: Ollanenor, "
    "the god of Saints; Lorenthal, the god of Peace; Melvanar, the god of Wrath; "
    "and Anumaranth, the god of Balance.\n\n"
    "For each god existed an Order that rose to fill the void caused by the "
    "migrations and lack of purpose.\n\n"
    "Ollanenor was run by the Order of Saints, the first order, used to determine a "
    "priest's Saint's name — the name they took, foregoing their old identity, to "
    "take on the work of that Saint as their own. The Inquisition, a growing arm of "
    "the order, trains the populace of Lenaveron preparing for their Saint's name, "
    "removing all pharisaic tendencies from its own people to prevent the next "
    "fall, always suspicious of its imminent arrival.\n\n"
    "The Order of Mission represents Lorenthal, and is responsible for the mission "
    "work of expanding its name and authority across all borders.\n\n"
    "The Order of Penance of Melvanar prepares its people and all inhabitants of "
    "Vaelohk for the return of Melvanar, seeking justice against those who had "
    "fallen from his path.\n\n"
    "Lastly, from Anumaranth came the Order of the True Word. They were strict "
    "record keepers, fact finders, and administrators. In order to fund the grand "
    "instrument of the papacy, the Tithe was implemented, causing all under the "
    "reach of the four gods, the Tetramorph, to tithe in order to fund and fuel "
    "the great power of Lenaveron."
)






def bearing(frm, to):
    """Compass bearing from one culture (or place) to another. Returns e.g.
    'north-west', 'east', or 'the same ground' when they overlap."""
    a = POSITIONS.get(CULTURE_SEATS.get(frm, frm))
    b = POSITIONS.get(CULTURE_SEATS.get(to, to))
    if a is None or b is None:
        return None
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx == 0 and dy == 0:
        return "the same ground"
    ns = "north" if dy > 0 else ("south" if dy < 0 else "")
    ew = "east" if dx > 0 else ("west" if dx < 0 else "")
    # drop the minor axis when one dominates by 2:1
    if ns and ew:
        if abs(dy) >= 2 * abs(dx):
            ew = ""
        elif abs(dx) >= 2 * abs(dy):
            ns = ""
    return "-".join(p for p in (ns, ew) if p)