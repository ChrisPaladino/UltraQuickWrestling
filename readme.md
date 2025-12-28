# Ultra Quick Wrestling - Python Edition

A Python console simulation of **Ultra Quick Wrestling**, the fast-paced 1991-themed pro wrestling game originally published by Downey Games. This version recreates the action using real wrestler stats, dynamic match types, and storytelling logic pulled straight from the rulebook.

---

## 📦 Project Structure

ultra_quick_wrestling/
├── main.py              # Entry point for the console app
├── engine/
│   ├── __init__.py
│   ├── match.py         # Core match simulation
│   ├── wrestler.py      # Wrestler model + rating logic
│   └── data_loader.py   # Reads wrestlers.json and game_data.json
├── data/
│   ├── wrestlers.json
│   └── game_data.json
├── rules/
│   └── UltraQuickWrestling_Rules.md

---

## ▶️ Getting Started

### Requirements

- Python 3.x
- Standard Library modules only: `json`, `os`, `random`

### How to Run (Console)

From the repository root, run the console driver:

```bash
python main.py
```

You'll be prompted to:

1. Select two wrestlers from the 1991 roster (by number).
2. Resolve any duplicate personas by designating who works Face and who works Heel.
3. Choose a match type (TV Taping, PPV, Cage, No DQ, Specialty).
4. View the narrated match log in your terminal.

---

## 🧠 Rules & Logic Overview

This project implements the official UQW rules including:

- Wrestler attributes like **Savvy**, **Cheating**, **Speed**, and **Heat**
- A rule-driven flow:
  - **Match modifier roll (d10):** adjusts which attribute feeds the core rating for this bout.
  - **Pre-match chart (d10 → d100):** selects which side is targeted, applies storyline events, and can temporarily or permanently tweak ratings before the bell.
  - **Result chart (d100):** compares the adjusted Face/Heel ratings and rolls against the difference bands to determine the winner, then consults the appropriate match-type result table.
- Post-match outcomes pulled from the match-type win chart, with optional unusual results when triggered.
- Possibility of unusual or storyline-driven results (like run-ins, distractions, surprise wins).

Advanced and supplemental rules are partially implemented or planned.

---

## 🔮 Future Roadmap

- Match history log / federation tracker
- Tag Team and Battle Royale support
- Heat rating persistence
- Toggle between core and advanced rule modes
- Planned GUI exploration (design TBD; not yet shipped)

---

## ⚙️ Optional & Advanced Rules

Advanced rule handling lives in `engine/advanced_rules.py` and can be toggled when creating a `Match`. These hooks cover persistent Heat changes, rivalry escalation, injury penalties/recovery, title swaps, and simple season ticking.

### Enabling

Pass an `advanced_rules_config` dictionary (or `AdvancedRulesConfig`) into `Match`:

```python
from engine.match import Match

config = {
  "enabled": True,
  "title_on_the_line": "World Championship",  # optional
  "injury_chance": 0.15,
  "enable_seasons": True,
  "enable_persistent_modifiers": True,        # optional; defaults to True
  "clean_win_bonus": 5,
  "clean_loss_penalty": 5,
  "title_overall_bonus": 5,
  "heat_on_title_changes": True,
}
match = Match(face_data, heel_data, match_type, game_data, assigned_roles, advanced_rules_config=config)
```

If `enabled` is `False` or omitted, core rules run unchanged.

### Available Toggles

- `enable_injuries` (default `True`): Apply injury penalties, decrement durations, and add new injuries based on `injury_chance`.
- `enable_titles` (default `True`): Move `title_on_the_line` between competitors.
- `enable_rivalries` (default `True`): When both wrestlers share `rivalry_id`, apply rivalry heat bonuses/penalties.
- `enable_heat` (default `True`): Persist `heat_modifier` changes per match and factor them into ratings.
- `enable_seasons` (default `True`): Track `season.current_week`/`season.length` in `data/wrestlers.json`.
- `enable_persistent_modifiers` (default `True`): Allow permanent modifiers to be written/read. Turn this off to disable rivalry heat swings, clean-finish bonuses/penalties, title sync bonuses, and ongoing heat deltas even while other advanced hooks stay active.

Other tunables include `injury_penalty`, `injury_duration`, `rivalry_heat_bonus`, `rivalry_heat_penalty`, and `base_heat_delta`.

#### Persistent modifiers

- Clean finishes can apply overall changes (`clean_win_bonus`, `clean_loss_penalty`), and champions can gain an overall boost (`title_overall_bonus`) and optional Heat delta (`heat_on_title_changes`/`heat_change_on_titles`). These are saved to `overall_modifier`/`heat_modifier`.
- Defaults mirror the existing behavior: persistence is on, clean bonuses/penalties are `0` (off), `title_overall_bonus` is `0` (off), and `heat_on_title_changes` is `True`.
- Persistent modifiers share the same `data/wrestlers.json` storage that `enable_seasons` uses. You can run persistent modifiers with or without seasons enabled; turning seasons off does not disable modifier persistence.

### Persisted Data

`data/wrestlers.json` now carries optional fields per wrestler:

- `titles`: list of championships held
- `rivalry_id`: identifier string shared by opponents in a feud
- `heat_modifier`: persistent heat delta applied to match ratings
- `injured` / `injury_duration`: injury tracking (backward compatible defaults provided)

A top-level `season` block (`length`, `current_week`) tracks booking seasons when enabled.

---

## 📚 Reference

- All rules implemented based on *Ultra Quick Wrestling* by Downey Games (© 2005)
- Wrestler data pulled from the 1991 set provided with the game

## AI Wrestler Prompts

Describe the physical appearance of this pro wrestler such that I can feed a paragraph into an AI art generation program and get a portrait. Do not include mood, or feeling - only physical descriptions. Do so in a paragraph format, not a list, not a character sheet.

This is a fictional pro wrestler named . They're a . I'd like you to estimate height (in inches) and weight (in lbs). I also need 2 suggestions they're finishing move.
