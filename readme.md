# Ultra Quick Wrestling - Python Edition

A Python GUI-based simulation of **Ultra Quick Wrestling**, the fast-paced 1991-themed pro wrestling game originally published by Downey Games. This version recreates the action using real wrestler stats, dynamic match types, and storytelling logic pulled straight from the rulebook.

---

## 📦 Project Structure

ultra_quick_wrestling/
├── main.py              # Entry point for console app
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
- Standard Library modules only: `tkinter`, `json`, `os`, `random`

### How to Run

python match_simulator.py

The GUI will launch with options to:

- Select two wrestlers from the 1991 roster
- Pick a match type (TV Taping, PPV, Cage, No DQ, Specialty)
- Simulate and view the match result with storyline flavor and modifiers

---

## 🧠 Rules & Logic Overview

This project implements the official UQW rules including:

- Wrestler attributes like **Savvy**, **Cheating**, **Speed**, and **Heat**
- Match modifiers and pre-match storylines
- Random match outcomes based on overall ratings + dice rolls
- Possibility of unusual or storyline-driven results (like run-ins, distractions, surprise wins)

Advanced and supplemental rules are partially implemented or planned.

---

## 🔮 Future Roadmap

- Match history log / federation tracker
- Tag Team and Battle Royale support
- Heat rating persistence
- Toggle between core and advanced rule modes
- More dynamic, themed GUI (1980s/1990s wrestling vibe)

---

## 📚 Reference

- All rules implemented based on *Ultra Quick Wrestling* by Downey Games (© 2005)
- Wrestler data pulled from the 1991 set provided with the game

## AI Wrestler Prompts

Describe the physical appearance of this pro wrestler such that I can feed a paragraph into an AI art generation program and get a portrait. Do not include mood, or feeling - only physical descriptions. Do so in a paragraph format, not a list, not a character sheet.

This is a fictional pro wrestler named . They're a . I'd like you to estimate height (in inches) and weight (in lbs). I also need 2 suggestions they're finishing move.
