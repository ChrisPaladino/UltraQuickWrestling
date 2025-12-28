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

## 📚 Reference

- All rules implemented based on *Ultra Quick Wrestling* by Downey Games (© 2005)
- Wrestler data pulled from the 1991 set provided with the game

## AI Wrestler Prompts

Describe the physical appearance of this pro wrestler such that I can feed a paragraph into an AI art generation program and get a portrait. Do not include mood, or feeling - only physical descriptions. Do so in a paragraph format, not a list, not a character sheet.

This is a fictional pro wrestler named . They're a . I'd like you to estimate height (in inches) and weight (in lbs). I also need 2 suggestions they're finishing move.
