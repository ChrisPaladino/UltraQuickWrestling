# Ultra Quick Wrestling - Python Edition

A Python GUI-based simulation of **Ultra Quick Wrestling**, the fast-paced 1991-themed pro wrestling game originally published by Downey Games. This version recreates the action using real wrestler stats, dynamic match types, and storytelling logic pulled straight from the rulebook.

---

## 📦 Project Structure

UltraQuickWrestling/
│
├── data/
│   ├── images/                # Wrestler images
│   ├── wrestlers.json         # Wrestler profiles and stats
│   └── game_data.json         # Rules, charts, modifiers, and outcomes
│
├── match_simulator.py         # 🖥 Main TKinter GUI app
├── match.py                   # 🤼‍♂️ Match resolution logic + Wrestler class
├── data_manager.py            # 📊 Loads and saves wrestler/game data
├── wrestler_editor.py         # ✏️ (Optional) Editor for creating/updating wrestlers
│
├── Ultra Quick Wrestling.pdf  # 🗂 Official rulebook (reference only)
└── README.md                  # 📘 This file

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

### Wrestler attributes

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
