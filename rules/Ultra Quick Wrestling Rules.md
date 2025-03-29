# Rules

The rules of Ultra Quick Wrestling are simple, and easy to follow. Most matches require only 2 or 3 rolls of the dice even with wild events.

## Wrestler Attributes

Each wrestler in UQW has a set of core stats that represent their abilities and style in the ring. These are used throughout the match to determine how they perform, especially when a specific match modifier is in play.

### Core Attributes

1. **Name** – Wrestler's name
2. **Finisher** – Their signature move
3. **Persona** – Heel or Face
4. **Overall** – The base rating used in all matches
5. **Strength** – Used in brute-force modifiers
6. **Speed** – Used in agility-based matches
7. **Savvy** – Used when tactical skill matters
8. **Technical** – Used for mat-based skill and submissions
9. **Cheating** – Used when rule-breaking pays off
10. **Size** – Used in power or size-based matchups
11. **Heat** – Momentum/popularity (used in story mode)

### Specialty Match Bonuses

1. **Cage** – Bonus used in cage matches
2. **Object** – Used in hardcore/no DQ matches
3. **Brawling** – Used in brawls, battle royals
4. **Ladder** – Used in climbing matches
5. **Table** – Used in table matches
6. **Tag** – Tag team synergy bonus

## Match Types

Ultra Quick Wrestling supports a variety of match types. These can influence the post-match narrative and determine which charts are used for results. The only limit to the type of matches you can conduct in Ultra Quick Pro Wrestling is your imagination. The system is adaptable to anything and everything you could possibly dream up. In order to accommodate that flexibility, the match types are broken down into the following categories.

Common match types include:

- **TV Taping** - TV matches feature fewer clean pins in the purpose of advancing a story line. Most TV matches will end with some sort of trickery or strange happening. Many wild events will happen at TV Tapings. Due to the Nature of TV Tapings very rarely will you see a Title Match. Most champions fight at TV tapings with the “Non-Title Match” provision.
- **PPV Match** - This is where feuds are either advanced or ended. The PPV match will feature more “clean” finishes. But, there are still occasional wild events and trickery in hopes of a feud continuing to a bigger PPV match. Most Titles are defended at PPV Matches.
- **No DQ Match** - Just as the name implies, this match has no disqualifications. These matches are often used to end bitter feuds. Sometimes, however, outside interference will still contribute to the match’s outcome.
- **Cage Match** - This is a match that aims to keep outside interference to a minimum. Often times, a cage match will end a bitter feud. But, as always in the wild and wacky world of pro wrestling, sometimes anything can happen!
- **Specialty Match** - This category covers other match types. Whether it is a ladder match, table match, bull rope match, or lumber jack match. Again, your imagination is the only limit to the possibilities. Nothing ends a bitter feud like a good old dog collar match, or a lumber jack match.

Each standard match (ie: not battle royal, and not tag team) will consist of two wrestlers, one FACE (good guy) and one HEEL (bad guy). If both wrestlers are of the same type (both Face or both Heel), one should be designated as a Face and one a Heel for the purposes of this match only.

The match will be determined by the point differential between the wrestlers' Match Ratings. **Match Rating = Overall + Modifier stat**

## Match procedure

1. Decide the type of Match (TV, PPV, etc)
2. Select two wrestlers, and look at their Overall Ratings
3. Roll a d10 and check the Match Modifier chart ("match_modifiers" in the game_data.json file)
    - Each wrestler adds the **stat listed** on the Match Modifier chart to their Overall Rating to calculate their Match Rating. For example, if the modifier is `Cheating`, both wrestlers add their `Cheating` score to their Overall. If the modifier is `Normal`, use only the Overall Rating.
    - Special match types can use specific modifiers (Table, Ladder, etc.)
4. Roll a d10 and check the PRE-MATCH CHART ("pre_match_chart" in the game_data.json file) to see which wrestler we are applying pre-match results to (Heel or Face)
5. Roll a d100 on the Pre-Match Events chart (pre_match_events in game_data.json, note there are entries for Face and Heel)
    - These entries may be temporary modifiers to the current match, or permanent attribute changes
6. Subtract the lower Match Rating from the higher one to get the **point difference**. This is used to determine the likelihood of the higher-rated wrestler winning.
7. Cross-reference that difference to see the % for a win to get the likely winner (result_chart in the game_data.json file) to see if the lower or higher rated wrestler wins
8. Roll d100 and consult the WIN CHART (win_charts in the game_data.json) reference the type of match (TV Taping or PPV for example) and if the winner was a Heel or Face
9. Execute this result, rolling on any new charts if needed for Unusual Results values (unusual_results in the json)

### Sample Match

1. Decide type of Match: TV Taping
2. Select two wrestlers
    - Chris Paladino: Overall: 2450; Cheating: -50
    - Fred Skul: Overall: 2415; Cheating: 50
3. Roll Match Modifier: 5 = Cheating
    - Chris Paladino: 2450 - 50 = 2400
    - Fred Skul: 2415 + 50 = 2465
4. Roll Pre-Match Chart: 4 = Face
5. Roll Pre-Match Event Chart: (in this case use the Face Pre-Match Event Chart)
    - 57: Opponent Sneak Attack Fails; -200 Overall for Heel this match
    - Fred Skul Match Rating: 2465 - 200 = 2265
6. Subtract lower Match Rating from Higher. Point difference: 135
7. Roll on result chart for difference: 73 = Low-Rated Wins
8. Roll on the Heel TV Taping Chart: 13 = Clean Pin fall via Finisher
9. Fred Skul wins via his finisher!

#### Overall Rating Modifiers (Optional)

These long-term effects apply when tracking wrestler momentum across multiple matches:

- **+100** – World Champion (lost when the title is dropped)
- **+50** – Minor Champion
- **+20** – Clean victory
- **–25** – Clean loss
- **+20** – Heat increases
- **–20** – Heat decreases

### Tag Matches

- Combine the overalls and add the TAG rating of each to get the initial overall

### Battle Royal

- Pair folks into mini-battles, add BRAWL to each

### Optional & Advanced Rules

This rulebook only covers the core match procedure. For rules on injuries, title tracking, rivalries, Heat effects, booking seasons, or AI automation, see the optional rules module.
