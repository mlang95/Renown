/* presets.js - GENERATED from region_presets.py. Do not hand-edit. */
(function(root){root.RenownPresets={
 "Bleak Highlands": {
  "name": "Bleak Highlands",
  "substrate": "plains",
  "palette": [
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "mountain": 0.3,
   "tundra": 0.1
  },
  "morphology": {
   "mountain": "scatter",
   "tundra": "blob"
  },
  "buffers": [],
  "band": {},
  "scatter": {
   "mountain": [
    110,
    1,
    3,
    3,
    0.7,
    5,
    0.3
   ]
  },
  "border": {
   "n": 0,
   "s": 0,
   "e": {
    "width": [
     0,
     1
    ],
    "span": [
     0.2,
     0.5
    ]
   },
   "w": 0
  },
  "carve": null,
  "structure": null,
  "require_hill": true,
  "resource_min": {
   "forestry": 0,
   "apiary": 0,
   "mine": 1
  },
  "art": {
   "plains": "wastes",
   "tundra": "badlands"
  },
  "notes": "Herding clans under a chief \u2014 the line Vogen reached in 1136 and got no further. Broken country rather than a wall: peaks stand alone or join in short ridges, occasionally two hexes thick. Every route exists and none is fast, so an army bleeds tempo everywhere instead of being stopped in one pass. No forest, so forestry is unavailable.",
  "massif": {},
  "perimeter": {}
 },
 "Blighthold": {
  "name": "Blighthold",
  "substrate": "plains",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "mountain": 0.2,
   "tundra": 0.12,
   "forest": 0.1
  },
  "morphology": {
   "mountain": "massif",
   "tundra": "blob",
   "forest": "scatter"
  },
  "buffers": [],
  "band": {},
  "scatter": {
   "forest": [
    35,
    1,
    2,
    2
   ]
  },
  "border": {
   "n": 0,
   "s": 0,
   "w": 0,
   "e": {
    "width": [
     0,
     1
    ],
    "span": [
     0.2,
     0.5
    ]
   }
  },
  "carve": null,
  "structure": null,
  "require_hill": true,
  "resource_min": {
   "mine": 4,
   "quarry": 3
  },
  "art": {},
  "notes": "The heath they grew crops through the Blight. A handful of chunky massifs set away from the centre \u2014 high ground that frames the worked land instead of cutting it in half.",
  "massif": {
   "mountain": [
    12,
    10,
    16,
    6,
    4,
    6
   ]
  },
  "perimeter": {}
 },
 "Coloured Mountains": {
  "name": "Coloured Mountains",
  "substrate": "mountain",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "tundra": 0.16,
   "forest": 0.14
  },
  "morphology": {
   "tundra": "blob",
   "forest": "scatter"
  },
  "buffers": [],
  "band": {},
  "scatter": {
   "forest": [
    45,
    1,
    3,
    2
   ]
  },
  "border": {
   "n": 0,
   "s": 0,
   "w": {
    "width": [
     0,
     1
    ],
    "span": [
     0.2,
     0.5
    ]
   },
   "e": 0
  },
  "carve": {
   "routes": 2,
   "width": 1,
   "clearing_radius": 1,
   "temp": 0.9,
   "mazes": [
    2,
    3
   ],
   "maze_temp": 1.1,
   "junction_p": 0.4,
   "connect": "spanning"
  },
  "structure": null,
  "require_hill": false,
  "resource_min": {
   "mine": 5,
   "quarry": 4,
   "arable": 1,
   "salt": 1
  },
  "art": {},
  "notes": "The ancient continent. Wider valleys than Crag Pass \u2014 this is where a people farmed, not a labyrinth.",
  "massif": {},
  "perimeter": {}
 },
 "Crag Pass": {
  "name": "Crag Pass",
  "substrate": "mountain",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "water"
  ],
  "shares": {
   "forest": 0.14
  },
  "morphology": {
   "forest": "blob"
  },
  "buffers": [],
  "band": {},
  "scatter": {},
  "border": 0,
  "carve": {
   "routes": 0,
   "width": 1,
   "clearing_radius": 1,
   "temp": 1.3,
   "mazes": [
    2,
    3
   ],
   "maze_temp": 1.3,
   "junction_p": 0.6,
   "connect": "spanning"
  },
  "structure": null,
  "require_hill": false,
  "resource_min": {
   "salt": 0,
   "arable": 1,
   "forestry": 1,
   "apiary": 0,
   "quarry": 1,
   "mine": 2
  },
  "art": {},
  "notes": "Labyrinth. Everything is impassable except the carved network. Chokepoint warfare; movement is the whole game.",
  "massif": {},
  "perimeter": {}
 },
 "Default": {
  "name": "Default",
  "substrate": "plains",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "tundra",
   "water",
   "wetland"
  ],
  "shares": {
   "forest": 0.18,
   "wetland": 0.18,
   "tundra": 0.08,
   "mountain": 0.08
  },
  "morphology": {
   "forest": "blob",
   "wetland": "blob",
   "tundra": "blob",
   "mountain": "band"
  },
  "buffers": [
   [
    "forest",
    "wetland"
   ],
   [
    "forest",
    "tundra"
   ],
   [
    "wetland",
    "tundra"
   ]
  ],
  "band": {},
  "scatter": {},
  "border": {
   "n": 0,
   "s": 0,
   "e": {
    "width": [
     0,
     1
    ],
    "span": [
     0.3,
     0.7
    ]
   },
   "w": {
    "width": [
     0,
     1
    ],
    "span": [
     0.3,
     0.7
    ]
   }
  },
  "carve": null,
  "structure": null,
  "require_hill": true,
  "resource_min": {},
  "art": {},
  "notes": "Terrain stays out of the way. Baseline.",
  "massif": {},
  "perimeter": {}
 },
 "Draggath Wastes": {
  "name": "Draggath Wastes",
  "substrate": "plains",
  "palette": [
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "tundra": 0.42,
   "mountain": 0.12
  },
  "morphology": {
   "tundra": "blob",
   "mountain": "scatter"
  },
  "buffers": [],
  "band": {},
  "scatter": {
   "mountain": [
    55,
    1,
    3,
    3
   ]
  },
  "border": {
   "n": 0,
   "s": 0,
   "w": {
    "width": [
     0,
     1
    ],
    "span": [
     0.2,
     0.5
    ]
   },
   "e": 0
  },
  "carve": {
   "rivers": [
    1,
    2
   ],
   "river_temp": 1.0
  },
  "structure": null,
  "require_hill": true,
  "resource_min": {
   "forestry": 0,
   "apiary": 0
  },
  "art": {
   "plains": "wastes",
   "tundra": "badlands"
  },
  "notes": "Badlands. Tundra painted as salted earth. Strained everywhere; arable is scarce and contested \u2014 recursive scarcity.",
  "massif": {},
  "perimeter": {}
 },
 "Drakenheart": {
  "name": "Drakenheart",
  "substrate": "plains",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "water": 0.22,
   "mountain": 0.22,
   "forest": 0.08,
   "tundra": 0.06
  },
  "morphology": {
   "water": "channels",
   "mountain": "scatter",
   "forest": "scatter",
   "tundra": "blob"
  },
  "buffers": [],
  "band": {
   "water": [
    "e",
    0.0,
    0.6
   ]
  },
  "scatter": {
   "mountain": [
    70,
    1,
    4,
    3
   ],
   "forest": [
    35,
    1,
    2,
    2
   ]
  },
  "border": {
   "n": {
    "width": [
     1,
     2
    ],
    "span": [
     0.6,
     1.0
    ]
   },
   "s": {
    "width": [
     1,
     2
    ],
    "span": [
     0.6,
     1.0
    ]
   },
   "w": {
    "width": [
     1,
     2
    ],
    "span": [
     0.5,
     1.0
    ]
   },
   "e": {
    "width": [
     1,
     2
    ],
    "span": [
     0.5,
     1.0
    ]
   }
  },
  "carve": null,
  "structure": null,
  "require_hill": true,
  "resource_min": {
   "mine": 3,
   "salt": 0
  },
  "art": {},
  "notes": "Drakteni seat. Land is the scarce resource and the engine of everything they do \u2014 heavily channelled, mine-rich. Straits stay one hex so expansion is possible without a Shipyard, but every crossing ends your Move.",
  "massif": {},
  "perimeter": {}
 },
 "Dreadwood": {
  "name": "Dreadwood",
  "substrate": "forest",
  "palette": [
   "forest",
   "plains",
   "water",
   "wetland"
  ],
  "shares": {
   "wetland": 0.1
  },
  "morphology": {
   "wetland": "blob"
  },
  "buffers": [],
  "band": {},
  "scatter": {},
  "border": {
   "n": 0,
   "s": 0,
   "w": {
    "width": 1,
    "span": [
     0.3,
     0.6
    ]
   },
   "e": 0
  },
  "carve": {
   "routes": 0,
   "width": 1,
   "clearing_radius": 1,
   "temp": 0.9,
   "mazes": [
    1,
    2
   ],
   "maze_temp": 1.1,
   "junction_p": 0.5,
   "connect": "spanning"
  },
  "structure": {
   "dendritic": {
    "depth": 2,
    "branches": [
     2,
     2
    ],
    "trunk": [
     5,
     9
    ],
    "decay": 0.6
   }
  },
  "require_hill": false,
  "resource_min": {
   "quarry": 0,
   "salt": 0,
   "mine": 0,
   "arable": 1
  },
  "art": {},
  "notes": "Ithiss heartland. Woodland matrix; settlements sit in clearings linked by narrow grass passages. No tundra, no mountain: quarry/salt/mine are unavailable by design. Lanes branch and dead-end rather than joining up, so a limb is a commitment and a defender has ground that cannot be flanked through.",
  "massif": {},
  "perimeter": {}
 },
 "Fair Whitewood": {
  "name": "Fair Whitewood",
  "substrate": "tundra",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "forest": 0.24,
   "mountain": 0.16
  },
  "morphology": {
   "forest": "blob",
   "mountain": "band"
  },
  "buffers": [],
  "band": {
   "mountain": [
    "w",
    0.16,
    0.4,
    [
     0.35,
     0.6
    ]
   ]
  },
  "scatter": {},
  "border": {
   "n": {
    "width": [
     0,
     1
    ],
    "span": [
     0.3,
     0.6
    ]
   },
   "s": {
    "width": [
     0,
     1
    ],
    "span": [
     0.3,
     0.6
    ]
   },
   "w": 0,
   "e": 0
  },
  "carve": {
   "routes": 2,
   "width": 1,
   "clearing_radius": 1,
   "temp": 0.8,
   "connect": "spanning"
  },
  "structure": null,
  "require_hill": false,
  "resource_min": {
   "arable": 1,
   "apiary": 0,
   "quarry": 3,
   "salt": 2
  },
  "art": {},
  "notes": "Madekite. Wintery forested mountain pass. Ridges run part-way down the map rather than sealing it, so the passes are between the ranges instead of through them. Strained is the default condition; quarry-rich, arable-poor.",
  "massif": {},
  "perimeter": {}
 },
 "Glen of Pravak": {
  "name": "Glen of Pravak",
  "substrate": "plains",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "mountain": 0.18,
   "tundra": 0.1,
   "forest": 0.14
  },
  "morphology": {
   "mountain": "scatter",
   "tundra": "blob",
   "forest": "scatter"
  },
  "buffers": [],
  "band": {},
  "scatter": {
   "forest": [
    60,
    1,
    2,
    2
   ],
   "mountain": [
    10,
    1,
    3,
    4
   ]
  },
  "border": 0,
  "carve": null,
  "structure": {
   "ring": {
    "terrain": "mountain",
    "radius": 9,
    "thickness": 3,
    "gaps": 3
   }
  },
  "require_hill": true,
  "resource_min": {
   "salt": 0,
   "forestry": 1
  },
  "art": {},
  "notes": "A glen ringed by rock - the one piece of tillable land left, and the middle of the map is the thing worth taking rather than the thing in the way. Three passes through the ring, so every approach is known ground and can be watched.",
  "massif": {},
  "perimeter": {}
 },
 "Hermit's Row": {
  "name": "Hermit's Row",
  "substrate": "plains",
  "palette": [
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "mountain": 0.24,
   "tundra": 0.12
  },
  "morphology": {
   "mountain": "band",
   "tundra": "blob"
  },
  "buffers": [],
  "band": {
   "mountain": [
    "w",
    0.1,
    0.5
   ]
  },
  "scatter": {},
  "border": {
   "n": 0,
   "s": 0,
   "e": {
    "width": [
     0,
     1
    ],
    "span": [
     0.2,
     0.5
    ]
   },
   "w": 0
  },
  "carve": null,
  "structure": null,
  "require_hill": true,
  "resource_min": {
   "forestry": 0,
   "apiary": 0
  },
  "art": {
   "plains": "wastes",
   "tundra": "badlands"
  },
  "notes": "A narrow pair of ranges. Two walls, one contested narrows between them.",
  "massif": {},
  "perimeter": {}
 },
 "Lenaveron": {
  "name": "Lenaveron",
  "substrate": "plains",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "tundra": 0.12,
   "mountain": 0.1
  },
  "morphology": {
   "tundra": "blob",
   "mountain": "perimeter"
  },
  "buffers": [],
  "band": {},
  "scatter": {},
  "border": {
   "n": 0,
   "s": 0,
   "e": {
    "width": [
     1,
     2
    ],
    "span": [
     0.5,
     0.9
    ]
   },
   "w": 0
  },
  "carve": {
   "rivers": [
    1,
    2
   ],
   "river_temp": 1.0
  },
  "structure": {
   "compartments": {
    "cells": 7,
    "gate": [
     1,
     1
    ],
    "site_inset": 5,
    "water_seam_p": 0.15,
    "mountain_run": [
     6,
     12
    ],
    "forest_run": [
     3,
     5
    ],
    "forest_thick": 0.75,
    "wall": {
     "mountain": 0.45,
     "forest": 0.55
    }
   }
  },
  "require_hill": true,
  "resource_min": {
   "forestry": 1
  },
  "art": {},
  "notes": "Papacy heartland. Open and buildable in the middle \u2014 Piety wants Public Order, not chokepoints \u2014 with long thin ranges running along the margins. Ridges and rivers close the interior into walled compartments with one gate each - a Piety region should be held by knowing the ground, not by meeting in the open. Forest belongs to the walls rather than being scattered loose across the fields.",
  "perimeter": {
   "mountain": [
    7,
    [
     14,
     26
    ],
    [
     1,
     2
    ],
    [
     1,
     6
    ]
   ]
  },
  "massif": {}
 },
 "Lost Woods": {
  "name": "Lost Woods",
  "substrate": "forest",
  "palette": [
   "forest",
   "plains",
   "water",
   "wetland"
  ],
  "shares": {
   "wetland": 0.06
  },
  "morphology": {
   "wetland": "blob"
  },
  "buffers": [],
  "band": {},
  "scatter": {},
  "border": {
   "n": 0,
   "s": 0,
   "w": {
    "width": [
     1,
     2
    ],
    "span": [
     0.5,
     0.9
    ]
   },
   "e": 0
  },
  "carve": {
   "routes": 0,
   "width": 1,
   "clearing_radius": 1,
   "temp": 0.6,
   "mazes": [
    1,
    2
   ],
   "maze_temp": 0.9,
   "junction_p": 0.7,
   "rivers": [
    3,
    4
   ],
   "river_temp": 1.0,
   "connect": "spanning"
  },
  "structure": null,
  "require_hill": false,
  "resource_min": {
   "quarry": 0,
   "salt": 0,
   "mine": 0,
   "arable": 1
  },
  "art": {},
  "notes": "The only land untouched by the Great Fracture. Denser than Dreadwood and barely carved: one or two passages, everything else is wood. Defender Seizes the Initiative almost always.",
  "massif": {},
  "perimeter": {}
 },
 "Marrow Shoals": {
  "name": "Marrow Shoals",
  "substrate": "water",
  "palette": [
   "forest",
   "plains",
   "water",
   "wetland"
  ],
  "shares": {
   "wetland": 0.1,
   "forest": 0.06
  },
  "morphology": {
   "wetland": "blob",
   "forest": "scatter"
  },
  "buffers": [],
  "band": {},
  "scatter": {
   "forest": [
    25,
    1,
    2,
    2
   ]
  },
  "border": 0,
  "carve": {
   "islands": [
    6,
    6
   ],
   "island_size": [
    44,
    58
   ],
   "islets": [
    16,
    4
   ],
   "land_target": 0.48,
   "gap": [
    2,
    3
   ]
  },
  "structure": null,
  "require_hill": false,
  "resource_min": {
   "mine": 0,
   "quarry": 0,
   "salt": 0,
   "arable": 2,
   "forestry": 2
  },
  "art": {},
  "notes": "A true archipelago \u2014 one small isle per player plus scattered islets to expand onto. Deep water between them: you reach anyone else only once a Shipyard is mastered. Land is the scarcest thing on the board.",
  "sea_crossing": "shipyard",
  "massif": {},
  "perimeter": {}
 },
 "Scarlet Forest": {
  "name": "Scarlet Forest",
  "substrate": "forest",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "water",
   "wetland"
  ],
  "shares": {
   "mountain": 0.08,
   "wetland": 0.05
  },
  "morphology": {
   "mountain": "band",
   "wetland": "blob"
  },
  "buffers": [],
  "band": {},
  "scatter": {},
  "border": {
   "n": 0,
   "s": 0,
   "w": {
    "width": 1,
    "span": [
     0.3,
     0.7
    ]
   },
   "e": 0
  },
  "carve": {
   "routes": 1,
   "width": 1,
   "clearing_radius": 1,
   "temp": 0.8,
   "mazes": [
    2,
    3
   ],
   "maze_temp": 1.1,
   "junction_p": 0.5,
   "rivers": [
    1,
    2
   ],
   "river_temp": 1.0,
   "connect": "spanning"
  },
  "structure": null,
  "require_hill": false,
  "resource_min": {
   "forestry": 6,
   "salt": 0,
   "quarry": 1,
   "arable": 2
  },
  "art": {
   "plains": "scarlet_plain",
   "forest": "scarlet_forest"
  },
  "notes": "Best wood in the world. Woodland matrix but wider passages than Dreadwood; forestry saturated.",
  "massif": {},
  "perimeter": {}
 },
 "Shallow Mire": {
  "name": "Shallow Mire",
  "substrate": "wetland",
  "palette": [
   "forest",
   "plains",
   "water",
   "wetland"
  ],
  "shares": {
   "forest": 0.12
  },
  "morphology": {
   "forest": "blob"
  },
  "buffers": [],
  "band": {},
  "scatter": {},
  "border": {
   "n": {
    "width": [
     1,
     2
    ],
    "span": [
     0.4,
     0.8
    ]
   },
   "s": {
    "width": [
     1,
     2
    ],
    "span": [
     0.4,
     0.8
    ]
   },
   "w": {
    "width": [
     0,
     2
    ],
    "span": [
     0.3,
     0.7
    ]
   },
   "e": {
    "width": [
     0,
     2
    ],
    "span": [
     0.3,
     0.7
    ]
   }
  },
  "carve": {
   "routes": 3,
   "width": 1,
   "clearing_radius": 1,
   "temp": 0.7,
   "connect": "spanning"
  },
  "structure": null,
  "require_hill": false,
  "resource_min": {
   "quarry": 0,
   "salt": 0,
   "mine": 0,
   "arable": 1
  },
  "art": {},
  "notes": "Shassolin territory. Mire everywhere: Unwieldy, Immune Steady, -1 Save is the default battle condition. No tundra.",
  "massif": {},
  "perimeter": {}
 },
 "The Twelfth Reach": {
  "name": "The Twelfth Reach",
  "substrate": "water",
  "palette": [
   "forest",
   "plains",
   "tundra",
   "water",
   "wetland"
  ],
  "shares": {
   "forest": 0.14,
   "wetland": 0.06,
   "tundra": 0.04
  },
  "morphology": {
   "forest": "blob",
   "wetland": "blob",
   "tundra": "blob"
  },
  "buffers": [],
  "band": {},
  "scatter": {},
  "border": 0,
  "carve": {
   "islands": [
    3,
    4
   ],
   "island_size": [
    95,
    130
   ],
   "islets": [
    5,
    9
   ],
   "land_target": 0.58,
   "gap": [
    2,
    5
   ]
  },
  "structure": null,
  "require_hill": true,
  "resource_min": {
   "mine": 0,
   "quarry": 0,
   "salt": 0
  },
  "art": {},
  "notes": "Two to four substantial islands rather than a scatter \u2014 a diaspora zone, not a reef. Players share an island with a neighbour and must cross open water to reach the rest.",
  "sea_crossing": "shipyard",
  "massif": {},
  "perimeter": {}
 },
 "Tombs of the Old Gods": {
  "name": "Tombs of the Old Gods",
  "substrate": "tundra",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "mountain": 0.12,
   "plains": 0.0,
   "forest": 0.06
  },
  "morphology": {
   "mountain": "scatter",
   "forest": "scatter"
  },
  "buffers": [],
  "band": {},
  "scatter": {
   "mountain": [
    40,
    1,
    3,
    3
   ],
   "forest": [
    25,
    1,
    2,
    3
   ]
  },
  "border": {
   "n": 0,
   "s": 0,
   "e": {
    "width": [
     0,
     1
    ],
    "span": [
     0.3,
     0.6
    ]
   },
   "w": 0
  },
  "carve": {
   "routes": 2,
   "width": 1,
   "clearing_radius": 1,
   "temp": 0.8,
   "mazes": [
    2,
    3
   ],
   "maze_temp": 1.1,
   "junction_p": 0.4,
   "connect": "spanning"
  },
  "structure": null,
  "require_hill": false,
  "resource_min": {
   "arable": 1,
   "forestry": 1,
   "quarry": 4,
   "salt": 3
  },
  "art": {},
  "notes": "Frozen tundra the Lenavorites abandoned. Strained is the default state; quarry and salt are abundant, food is not.",
  "massif": {},
  "perimeter": {}
 },
 "Vaelohk": {
  "name": "Vaelohk",
  "substrate": "plains",
  "palette": [
   "forest",
   "mountain",
   "plains",
   "tundra",
   "water"
  ],
  "shares": {
   "forest": 0.34,
   "mountain": 0.06,
   "water": 0.04,
   "tundra": 0.05
  },
  "morphology": {
   "forest": "blob",
   "mountain": "scatter",
   "water": "blob",
   "tundra": "blob"
  },
  "buffers": [
   [
    "forest",
    "tundra"
   ]
  ],
  "band": {},
  "scatter": {
   "mountain": [
    22,
    1,
    2,
    4
   ]
  },
  "border": {
   "n": {
    "width": [
     1,
     2
    ],
    "span": [
     0.7,
     1.0
    ]
   },
   "s": {
    "width": [
     1,
     2
    ],
    "span": [
     0.7,
     1.0
    ]
   },
   "w": {
    "width": [
     1,
     2
    ],
    "span": [
     0.7,
     1.0
    ]
   },
   "e": {
    "width": [
     1,
     2
    ],
    "span": [
     0.7,
     1.0
    ]
   }
  },
  "carve": {
   "rivers": [
    2,
    3
   ],
   "river_temp": 1.0
  },
  "structure": {
   "radial": {
    "hub_radius": 2,
    "width": 1,
    "temp": 0.45
   }
  },
  "require_hill": true,
  "resource_min": {},
  "art": {},
  "notes": "The centre island and the world's name. Deliberately the most even preset \u2014 no dominant terrain, everything available. The Sullen Lake is the one inland water body. One lane runs from every region to the centre island's heart, so the middle is what everyone is equidistant from and committed toward - the question is when to march down your spoke, not which way.",
  "massif": {},
  "perimeter": {}
 },
 "Wheat Fields": {
  "name": "Wheat Fields",
  "substrate": "plains",
  "palette": [
   "forest",
   "plains",
   "water",
   "wetland"
  ],
  "shares": {
   "forest": 0.22,
   "wetland": 0.04
  },
  "morphology": {
   "forest": "scatter",
   "wetland": "blob"
  },
  "buffers": [],
  "band": {},
  "scatter": {
   "forest": [
    120,
    1,
    3,
    2
   ]
  },
  "border": {
   "n": 0,
   "s": 0,
   "e": {
    "width": [
     0,
     1
    ],
    "span": [
     0.2,
     0.5
    ]
   },
   "w": {
    "width": [
     0,
     1
    ],
    "span": [
     0.2,
     0.5
    ]
   }
  },
  "carve": {
   "rivers": [
    1,
    2
   ],
   "river_temp": 1.0
  },
  "structure": null,
  "require_hill": true,
  "resource_min": {
   "quarry": 0,
   "salt": 0,
   "mine": 0,
   "forestry": 1
  },
  "art": {},
  "notes": "Proving ground. Open field: ranged +1 Strike almost everywhere, Hills decide initiative. Never paved.",
  "massif": {},
  "perimeter": {}
 }
};})(typeof module!=='undefined'&&module.exports?module.exports:(typeof window!=='undefined'?window:globalThis));
