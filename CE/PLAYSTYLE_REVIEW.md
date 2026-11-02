# Playstyle reference — fit review (SIMPLE build, 2026-10-30)

All approved changes are applied in `renown_data_d10.py`. Monument lists are the SIMPLE overlay (~4663); Wonders,
Heritages and mechanic names are in the `CULTURES` block. Heritages outside the final cut stay in the lists but aren't printed.

## Cultures (current)

| Culture | Type · Archetype | Monuments | Wonders |
|---|---|---|---|
| Trusteki | Pure · Pure Engine | Office of Works, Manor House, Polish House, Port Authority | The Grand Exchange, High Chancery |
| Kraghs | Pure · Pure Aggro | Royal Pavilion, Marshal Tiltyard, Ministry of Military Strategy, Baggage Train | Colossus |
| Ithiss | Pure · Pure Tempo | Thieves' Guild, Outlaw Rookery, Whispering Undercroft, Outrider Intercept Post | High Chancery |
| Lenavorites | Pure · Pure Control | Senate Hall, Inquisitorial Palace, Exalted Basilica | The Eternal Sepulchre, High Chancery |
| Belvareth | Pair · Sustained Tempo | Preceptory of the Knight's Templar, Royal Pavilion, Exalted Basilica, Marshal Tiltyard | The Eternal Sepulchre, Colossus |
| Vorghith | Pair · Fluid Aggro | Outrider Intercept Post, Baggage Train, Outlaw Rookery, Marshal Tiltyard | Colossus |
| Drakteni | Pair · Scaling Aggro | Advanced Blast Furnace, Ministry of Military Strategy, Artillery Park, Imperial Palace | Colossus |
| Prezish | Pair · Sustained Engine | Aristocratic Court, Thieves' Guild, Port Authority, Polish House | The Grand Exchange, High Chancery |
| Shassolin | Pair · Sustained Control | Senate Hall, Inquisitorial Palace, Ossuary Crypt, Serfdom | High Chancery, The Eternal Sepulchre |
| Madekites | Pair · Scaling Control | Office of Works, Papal Palace, Exalted Basilica, Port Authority, Manor House | The Eternal Sepulchre, The Grand Exchange |
| Cailendroffs | Triple · Fluid Control | Inquisitorial Palace, Royal Pavilion, Preceptory of the Knight's Templar, Whispering Undercroft | Colossus, High Chancery |
| Sarkopekt | Triple · Scaling Tempo | Outrider Intercept Post, Baggage Train, Advanced Blast Furnace, Artillery Park | Colossus, The Grand Exchange |
| Ossensteins | Triple · Scaling Engine | Office of Works, Aristocratic Court, Whispering Undercroft, Studium Generale, Ossuary Crypt | The Grand Exchange, High Chancery |
| Voldrastel | Triple · Sustained Aggro | Papal Palace, Imperial Palace, Preceptory of the Knight's Templar, Office of Works | The Grand Exchange, The Eternal Sepulchre |
| Astravantheliad | Centre · Fluid Tempo | Senate Hall, Studium Generale, Aristocratic Court, Office of Works | High Chancery, The Grand Exchange, The Eternal Sepulchre |

Monument counts: Lenavorites 3; Ossensteins and Madekites 5; every other culture 4.

Monument summaries:
- Aristocratic Court → "Extorts Both Sides of Rivals' Diplomacy".
- Polish House → "Massive Income... and Attention".
- Marshal Tiltyard → "Shock Cavalry".

The Elder Grove moved from Trusteki to Vorghith. Plague Pit is replaced by Ossuary Crypt in Heritage pairs.
The Illusionists and The Crowned Star are already `deprecated: True`.

## Monument volume

| Monument | Needs | Cultures | Which | Heritage pairs (* = complement) |
|---|---|--:|---|---|
| Office of Works | Sovereign Industry | 5 | Trusteki, Madekites, Ossensteins, Voldrastel, Astravantheliad | Gilded Crescent*, Illuminated Order, Iron Faith, Iron Throne, Tunnellers |
| Aristocratic Court | Sov Industry + Rising Cunning | 3 | Prezish, Ossensteins, Astravantheliad | Entwined Crown, Merchant Republics*, Grand Compact, Velvet Hand, Dukedom* |
| Baggage Train | Sovereign Prowess | 3 | Kraghs, Vorghith, Sarkopekt | Battering Ram*, Boundless Steppe, Iron Shore, Winter Wolves, Ancient Wilds* |
| Exalted Basilica | Sovereign Piety | 3 | Lenavorites, Belvareth, Madekites | Iron Throne*, Sacred Throne, Undying Flame, Bloodied Cross* |
| Inquisitorial Palace | Sov Piety + Rising Cunning | 3 | Lenavorites, Shassolin, Cailendroffs | Sacred Throne, Ashen Vale |
| Marshal Tiltyard | Sovereign Prowess | 3 | Kraghs, Belvareth, Vorghith | Boundless Steppe, Bloodied Cross, Smoldering Crown, Elder Grove |
| Outrider Intercept Post | Sov Cunning + Rising Prowess | 3 | Ithiss, Vorghith, Sarkopekt | Boundless Steppe*, Bandit King*, Crimson Tide*, Ancient Wilds, Smoldering Crown*, Elder Grove, Yew Heart* |
| Port Authority | Sovereign Industry | 3 | Trusteki, Prezish, Madekites | Crimson Tide, Gilded Crescent, Merchant Republics, Verdant Kingdom, Grand Compact, Sublime Gate* |
| Preceptory of the Knight's Templar | Sov Piety + Est Prowess | 3 | Belvareth, Cailendroffs, Voldrastel | Iron Faith, Undying Flame, Bloodied Cross, Pale Throne* |
| Royal Pavilion | Sovereign Prowess | 3 | Kraghs, Belvareth, Cailendroffs | Final Word, Iron Shore*, Undying Flame*, Winter Wolves, Pale Throne, Elder Grove*, Yew Heart |
| Senate Hall | Sovereign Piety | 3 | Lenavorites, Shassolin, Astravantheliad | Entwined Crown, Eternal Court, Illuminated Order*, Velvet Hand, Dukedom |
| Whispering Undercroft | Sovereign Cunning | 3 | Ithiss, Cailendroffs, Ossensteins | Entwined Crown*, Eternal Court*, Hermit Crown |
| Advanced Blast Furnace | Sov Industry + Rising Prowess | 2 | Drakteni, Sarkopekt | Iron Shore, Tunnellers, Sublime Gate |
| Artillery Park | Sov Prowess + Est Industry | 2 | Drakteni, Sarkopekt | Battering Ram, Tunnellers*, Sublime Gate |
| Imperial Palace | Sov Prowess + Est Industry | 2 | Drakteni, Voldrastel | Final Word, Velvet Hand* |
| Manor House | Sovereign Industry | 2 | Trusteki, Madekites | Gilded Crescent, Hermit Crown*, Verdant Kingdom, Grand Compact* |
| Ministry of Military Strategy | Sovereign Prowess | 2 | Kraghs, Drakteni | Battering Ram, Final Word*, Ancient Wilds, Yew Heart |
| Ossuary Crypt | Sov Cunning + Est Piety | 2 | Shassolin, Ossensteins | Pale Throne, Ashen Vale |
| Outlaw Rookery | Sovereign Cunning | 2 | Ithiss, Vorghith | Bandit King, Winter Wolves*, Ashen Vale*, Smoldering Crown |
| Papal Palace | Sov Piety + Est Industry | 2 | Madekites, Voldrastel | Iron Faith*, Iron Throne, Sacred Throne* |
| Polish House | Sovereign Industry | 2 | Trusteki, Prezish | Verdant Kingdom* |
| Studium Generale | 3 Established | 2 | Ossensteins, Astravantheliad | Eternal Court, Hermit Crown, Illuminated Order, Dukedom |
| Thieves' Guild | Sov Cunning + Rising Industry | 2 | Ithiss, Prezish | Bandit King, Crimson Tide, Merchant Republics |
| Serfdom | Sovereign Cunning | 1 | Shassolin | — |

## Heritage pairs (final cut)

Pairs name Monuments from the cultures that carry the Heritage. The exception is The Pale Throne: Ossuary Crypt is in none of its cultures.

| Heritage | Pair | Complement |
|---|---|---|
| The Battering Ram | Artillery Park, Ministry of Military Strategy | Baggage Train |
| The Boundless Steppe | Baggage Train, Marshal Tiltyard | Outrider Intercept Post |
| The Bandit King | Outlaw Rookery, Thieves' Guild | Outrider Intercept Post |
| The Crimson Tide | Port Authority, Thieves' Guild | Outrider Intercept Post |
| The Entwined Crown | Senate Hall, Aristocratic Court | Whispering Undercroft |
| The Eternal Court | Studium Generale, Senate Hall | Whispering Undercroft |
| The Final Word | Imperial Palace, Royal Pavilion | Ministry of Military Strategy |
| The Gilded Crescent | Manor House, Port Authority | Office of Works |
| The Hermit Crown | Studium Generale, Whispering Undercroft | Manor House |
| The Illuminated Order | Studium Generale, Office of Works | Senate Hall |
| The Iron Faith | Office of Works, Preceptory of the Knight's Templar | Papal Palace |
| The Iron Shore | Baggage Train, Advanced Blast Furnace | Royal Pavilion |
| The Iron Throne | Office of Works, Papal Palace | Exalted Basilica |
| The Merchant Republics | Port Authority, Thieves' Guild | Aristocratic Court |
| The Sacred Throne | Exalted Basilica, Inquisitorial Palace | Papal Palace |
| The Tunnellers | Advanced Blast Furnace, Office of Works | Artillery Park |
| The Undying Flame | Preceptory of the Knight's Templar, Exalted Basilica | Royal Pavilion |
| The Verdant Kingdom | Port Authority, Manor House | Polish House |
| The Winter Wolves | Baggage Train, Royal Pavilion | Outlaw Rookery |
| The Ancient Wilds | Outrider Intercept Post, Ministry of Military Strategy | Baggage Train |
| The Bloodied Cross | Preceptory of the Knight's Templar, Marshal Tiltyard | Exalted Basilica |
| The Grand Compact | Port Authority, Aristocratic Court | Manor House |
| The Pale Throne | Ossuary Crypt, Royal Pavilion | Preceptory of the Knight's Templar |
| The Sublime Gate | Advanced Blast Furnace, Artillery Park | Port Authority |
| The Velvet Hand | Aristocratic Court, Senate Hall | Imperial Palace |
| The Ashen Vale | Ossuary Crypt, Inquisitorial Palace | Outlaw Rookery |
| The Smoldering Crown | Outlaw Rookery, Marshal Tiltyard | Outrider Intercept Post |
| The Dukedom | Senate Hall, Studium Generale | Aristocratic Court |
| The Elder Grove | Outrider Intercept Post, Marshal Tiltyard | Royal Pavilion |
| The Yew Heart | Royal Pavilion, Ministry of Military Strategy | Outrider Intercept Post |

## Rule 2.3 (Core Principles, `RULES_push_simple.md`)

Faction > Monument > Wonder > Standing > Infrastructure = Holding > Action > general rule; 2.2 decides within a level.
