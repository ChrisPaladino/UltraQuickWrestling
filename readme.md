# Ultra Quick Wrestling - Python Edition

A Python simulation of **Ultra Quick Wrestling**, the fast-paced 1991-themed pro wrestling game originally published by Downey Games. This version recreates the action using real wrestler stats, dynamic match types, and storytelling logic pulled straight from the rulebook.

**Features:**
- ✅ Complete match simulation engine with all official UQW rules
- ✅ Tag team matches (2v2, 3v3, any combination)
- ✅ Advanced rules: injuries, championships, heat/momentum, rivalries, seasons
- ✅ Event booking and storyline management
- ✅ Command-line interface and Tkinter GUI
- ✅ Data-driven design (customize rules via JSON)
- ✅ Comprehensive test suite

---

## 📦 Project Structure

```
UltraQuickWrestling/
├── main.py              # Console CLI entry point
├── data/                # Game data and wrestler rosters (JSON)
├── src/                 # Source code
│   ├── engine/          # Core match simulation engine
│   └── gui/             # Tkinter GUI application
├── docs/                # Documentation
│   ├── ARCHITECTURE.md       # System design and components
│   ├── ROADMAP.md            # Feature implementation status
│   ├── DEVELOPER_GUIDE.md    # Development guide
│   ├── Ultra Quick Wrestling Rules.md
│   └── Ultra Quick Wrestling.pdf
└── tests/               # Pytest test suite
```

---

## ▶️ Quick Start

### Requirements

- **Python 3.10+** (Python 3.13 recommended)
- Standard library only (no external dependencies for core functionality)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/UltraQuickWrestling.git
   cd UltraQuickWrestling
   ```

2. **Run the CLI:**
   ```bash
   python main.py
   ```

3. **Or launch the GUI:**
   ```bash
   python -m src.gui.app
   ```

### Basic Usage (CLI)

**Interactive mode** - Follow prompts to select wrestlers and match type:
```bash
python main.py
```

**Quick match** - Command-line arguments:
```bash
python main.py --wrestler-a "Hulk Hogan" --wrestler-b "Randy Savage" --match-type "PPV"
```

**Tag team match:**
```bash
python main.py --tag \
  --team-a "Bret Hart,Jim Neidhart" \
  --team-b "Ted DiBiase,IRS" \
  --face-team A \
  --match-type "Tag Team Match"
```

---

## 🎮 Features Overview

### Core Match Engine
- **Match Types:** TV Taping, PPV, Cage Match, No DQ, Specialty matches
- **Dice-Based Mechanics:** Match modifiers, pre-match events, result charts
- **Win Charts:** Different outcomes based on match type and winner persona
- **Unusual Results:** Run-ins, distractions, double-DQs, and more

### Wrestler Attributes
- **Core Stats:** Overall, Strength, Speed, Savvy, Technical, Cheating, Size, Heat
- **Specialty Bonuses:** Cage, Object, Brawling, Ladder, Table, Tag
- **Dynamic Properties:** Injuries, championships, momentum tracking

### Tag Team Support
- Multi-wrestler teams (2v2, 3v3, etc.)
- Tag attribute bonuses
- Tag-specific win charts

### Advanced Rules (Optional)
- **Injuries:** Random injury system with recovery tracking
- **Championships:** Title tracking with automatic title changes
- **Heat/Momentum:** Wrestler popularity and momentum effects
- **Rivalries:** Enhanced effects for feuding wrestlers
- **Seasons:** Multi-week campaign tracking
- **Persistent Modifiers:** Long-term rating adjustments

### Booking System
- Event card creation and management
- Storyline/feud tracking
- Story beat logging
- Match-to-storyline linking

### User Interfaces
- **CLI:** Fast, scriptable command-line interface
- **GUI:** Full-featured Tkinter application with:
  - Roster management
  - Quick match simulation
  - Event booking
  - Season management
  - Storyline tracking

---

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design, components, and data flows
- **[ROADMAP.md](docs/ROADMAP.md)** - Feature implementation status and future plans
- **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** - Development setup and extension guide
- **[Ultra Quick Wrestling Rules.md](docs/Ultra%20Quick%20Wrestling%20Rules.md)** - Official game rules

---

## 🧪 Running Tests

```bash
# Install pytest (optional)
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_match.py
```

---

## 🎯 What's Implemented

### ✅ Complete
- Core match simulation (all match types)
- Tag team matches
- All advanced rules (injuries, titles, heat, rivalries, seasons)
- Event booking and storyline management
- CLI and GUI interfaces
- Data persistence (JSON)
- Comprehensive test coverage

### 🔄 In Progress
- Battle Royal matches
- Tournament mode
- Enhanced GUI features (batch import, visual history)

### 📋 Planned
- Manager/valet system
- Referee bias mechanics
- Stable/faction system
- AI booking assistant
- Web-based interface

**See [ROADMAP.md](docs/ROADMAP.md) for complete feature status.**

---

## ⚙️ Configuration & Advanced Rules

### Advanced Rules Quick Reference

Enable advanced rules for campaign/season play:

```python
from src.engine.match import create_match
from src.engine.advanced_rules import AdvancedRulesConfig

config = AdvancedRulesConfig(
    enabled=True,
    enable_injuries=True,        # Random injury system
    enable_titles=True,          # Championship tracking
    enable_heat=True,            # Momentum/popularity
    enable_rivalries=True,       # Feud enhancements
    enable_seasons=True,         # Multi-week campaigns
    injury_chance=0.15,          # 15% injury chance
    clean_win_bonus=20,          # Rating boost on clean win
    clean_loss_penalty=-25       # Rating penalty on clean loss
)

match = create_match(
    wrestler_a_data,
    wrestler_b_data,
    "PPV",
    game_data,
    assigned_roles,
    advanced_rules_config=config
)
```

### Data-Driven Customization

Customize game rules by editing `data/game_data.json`:
- Match modifiers (which attributes affect ratings)
- Pre-match events and effects
- Win charts for different match types
- Unusual results and storyline triggers

**No code changes required!** The engine reads all rules from JSON.

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** on GitHub
2. **Read the documentation:**
   - [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for development setup
   - [ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand the system
   - [ROADMAP.md](docs/ROADMAP.md) to find features to implement
3. **Create a feature branch:** `git checkout -b feature/my-feature`
4. **Make your changes** with tests and documentation
5. **Run the test suite:** `pytest tests/`
6. **Submit a pull request** with a clear description

### Areas Where We Need Help
- Battle Royal and Tournament mode implementation
- GUI enhancements (batch import, visual history)
- Manager/valet system
- Additional test coverage
- Documentation improvements

---

## 📄 License

This project is a fan-made recreation of Ultra Quick Wrestling for educational and entertainment purposes. Original game © Downey Games.

---

## 🎯 Credits

- **Original Game:** Ultra Quick Wrestling by Downey Games (1991)
- **Python Implementation:** Community contributors
- **Rules Reference:** Ultra Quick Wrestling rulebook

---

## 📞 Support & Community

- **Issues:** Report bugs or request features on GitHub Issues
- **Discussions:** Join conversations in GitHub Discussions
- **Documentation:** See `docs/` folder for comprehensive guides

---

**Happy Wrestling! 🤼**

