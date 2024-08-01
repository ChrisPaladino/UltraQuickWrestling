#### Bugs
1. Wrestler 1 should be "Face" and Wrestler 2 should be "Heel" - for purposes of this match, regardless of their persona. Suggestion to have FACE and HEEL instead of Wrestler 1 and 2.
2. Face and Heel comparisons (match.py line 79) seem to be case-sensitive. Overall - we should convert things to lowercase to compare them.

#### To Implement
- Need a way to track the source/original vs. the changed stats (overalls, heat, records) so that we can reset things back to default
- Need to know rankings (heel #7, face #1, 1-10 of each)
- Review the charts to ensure we can capture the effects and targets
	- This means including a list of ordered FACE and HEEL wrestlers

#### Bugs
- Wrestler 1 should be "Face" and Wrestler 2 should be "Heel" - for purposes of this match, regardless of their persona. Suggestion to have FACE and HEEL instead of Wrestler 1 and 2.
- Face and Heel comparisons (match.py line 79) seem to be case-sensitive. Overall - we should convert things to lowercase to compare them.
- game_data.json should have the Face and Heel pre-match event "duration" to be the # of matches, not a text string; 0 is permanent. Let's assume 2 matches per week, so a month would be "8".

#### Google Sheets Formula
=if(H4 <> "", (I$2 - (H4 - 1) * ((I$2 - I$1) / (counta(H$4:H$76)- 1))), "")

#### Wrestler attributes
1. Name
2. Personna (Heel or Face)
3. Finisher
4. Attributes
	- Size
	- Speed
	- Strength
	- Savvy
	- Cheating
	- Tech
	- Cage
	- Object
	- Brawl
	- Ladder
	- Table
	- Tag
5. Overall Rating
6. Heat

#### Match attributes
1. Type
	- TV Taping
	- PPV Match
	- No DQ Match
	- Cage Match
	- Specialty Match

#### Gameplay
1. pick wrestlers
2. take each overall rating
3. roll d10 and check MATCH MODIFIER CHART
4. add that rating from each wrestler to their overall value for the attribute rolled
	1. normal = no modifiers
	2. if a wrestler has a "/", the first rating is FACE, and the 2nd is HEEL
	3. special match types can use specific modifiers (Table, Ladder, etc.)
5. roll d10 and check the PRE-MATCH CHART to see the subject and chart to roll next
6. roll d100 on the sub-chart and execute
7. subtract the two adjusted ratings to get a difference
8. cross-reference that difference to see the % for a win to get the likely winner
9. roll d100 and consult the WIN CHART for the persona of the winner and type of match conducted
10. Execute this result, rolling on any new charts if needed

#### Fed
- Start with 20-40 wrestlers
- Take 10 HEELS and 10 FACES and assign them heat from 10 (highest overall) down to 1 (least overall of the 10 selected)

#### Overall Adjustments
- World title adds 100 to overall (lost when he loses the title)
- Minor title adds 50 points (again, lost when we lose the title)
- Wins on a Clean pin adds 20 to Overall
- Loses on a Clean pin subtracts 25 from overall rating
- Heat rating going up adds 20 to overall
- Heat rating goes down subtract 20 from overall rating

#### Tag Matches
- Combine the overalls and add the TAG rating of each to get the initial overall

#### Battle Royal
- Pair folks into mini-battles, add BRAWL to each