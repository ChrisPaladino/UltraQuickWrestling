# Developer Guide - Ultra Quick Wrestling

## Getting Started with Development

This guide will help you understand, modify, and extend the Ultra Quick Wrestling codebase.

## Development Environment Setup

### Prerequisites
- Python 3.10+ (Python 3.13 recommended)
- Git
- Code editor (VS Code recommended)

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/UltraQuickWrestling.git
   cd UltraQuickWrestling
   ```

2. **Create virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install development dependencies:**
   ```bash
   # No external dependencies for core functionality
   # Just Python standard library
   
   # For running tests:
   pip install pytest pytest-cov
   ```

4. **Run tests to verify setup:**
   ```bash
   pytest tests/
   ```

## Project Structure Deep Dive

```
UltraQuickWrestling/
├── main.py                  # CLI entry point
├── src/
│   ├── engine/             # Core simulation engine
│   │   ├── __init__.py
│   │   ├── match.py        # Match simulation (Match, TagMatch classes)
│   │   ├── wrestler.py     # Wrestler model and attributes
│   │   ├── booking.py      # Event and storyline management
│   │   ├── repository.py   # Data access layer
│   │   ├── advanced_rules.py  # Optional rules engine
│   │   ├── file_utils.py   # Atomic file operations
│   │   └── game_data.py    # Game data normalization
│   └── gui/
│       └── app.py          # Tkinter GUI application
├── data/                   # JSON data files
│   ├── wrestlers.json      # Wrestler roster
│   ├── belts.json          # Championships
│   ├── game_data.json      # Rules, charts, tables
│   ├── events.json         # Booking state
│   └── images/             # Wrestler images
├── docs/                   # Documentation
├── tests/                  # Test suite
└── readme.md              # Project overview
```

## Key Concepts

### 1. Data-Driven Design

Almost all game mechanics are defined in `data/game_data.json`, not hardcoded. This includes:
- Match modifiers
- Pre-match events
- Result probability charts
- Win outcome tables
- Unusual results

**Why?** Allows users to customize rules without touching code.

### 2. Atomic File Writes

All JSON writes use `safe_write_json()` in `file_utils.py`:
```python
def safe_write_json(file_path: str, data: dict):
    # 1. Write to temporary file
    # 2. Flush and fsync
    # 3. Atomic rename over original
```

**Why?** Prevents data corruption if program crashes mid-write.

### 3. Attribute Normalization

Wrestler attributes can be in different formats:
```json
// Flat structure
{"strength": 50, "speed": 100}

// Nested structure
{"attributes": {"strength": 50, "speed": 100}}

// Variations
{"Strength": 50, "SPEED": 100}  // Case-insensitive
```

`Wrestler.normalize_attribute_name()` handles all variations.

**Why?** Backward compatibility with different data formats.

### 4. Advanced Rules as Optional Layer

`AdvancedRulesEngine` is completely optional:
```python
match = Match(..., advanced_rules_config=None)  # Disabled
match = Match(..., advanced_rules_config={...}) # Enabled
```

**Why?** Keeps core engine simple while allowing complex campaign play.

## Common Development Tasks

### Adding a New Wrestler Attribute

1. **Update the data model** (`data/wrestlers.json`):
   ```json
   {
     "name": "Example Wrestler",
     "attributes": {
       "new_attribute": 50
     }
   }
   ```

2. **Update Wrestler class** (`src/engine/wrestler.py`):
   ```python
   def normalize_attribute_name(name):
       # Add mapping if needed
       aliases = {
           "new_attribute": "new_attribute",
           "new_attr": "new_attribute"  # Alias support
       }
   ```

3. **Add to match modifiers** (optional, `data/game_data.json`):
   ```json
   {
     "roll": 10,
     "modifier": "New Attribute"
   }
   ```

4. **Update GUI** (`src/gui/app.py`):
   - Add field to wrestler editor form
   - Update display methods

5. **Add tests** (`tests/test_match_modifiers.py`):
   ```python
   def test_new_attribute_modifier(self):
       # Test that new attribute affects match rating
   ```

### Creating a New Match Type

1. **Add match type to game_data.json**:
   ```json
   "win_charts": {
     "New Match Type": {
       "Face Wins": [
         {"roll": "01-20", "result": "Clean pin via finisher"},
         ...
       ],
       "Heel Wins": [...]
     }
   }
   ```

2. **No code changes needed!** The engine is data-driven.

3. **Update GUI dropdown** (if adding to GUI):
   ```python
   # In MatchTab, dropdown populates from game_data
   match_types = list(self.data_store.game_data['win_charts'].keys())
   ```

4. **Add tests**:
   ```python
   def test_new_match_type(self):
       result = match.simulate()
       assert "New Match Type" in result_log
   ```

### Implementing a New Advanced Rule

Example: Adding a "Stamina" system

1. **Extend AdvancedRulesConfig** (`src/engine/advanced_rules.py`):
   ```python
   @dataclass
   class AdvancedRulesConfig:
       # ... existing fields ...
       enable_stamina: bool = True
       stamina_drain_per_match: int = 10
       stamina_recovery_per_week: int = 5
   ```

2. **Add stamina tracking to wrestler data**:
   ```json
   {
     "name": "Wrestler",
     "stamina": 100,
     "max_stamina": 100
   }
   ```

3. **Implement stamina logic**:
   ```python
   class AdvancedRulesEngine:
       def apply_post_match(self, ...):
           if self.config.enable_stamina:
               self._handle_stamina(winner, loser, log)
       
       def _handle_stamina(self, winner, loser, log):
           for wrestler in [winner, loser]:
               current = wrestler.get("stamina", 100)
               drained = current - self.config.stamina_drain_per_match
               wrestler["stamina"] = max(0, drained)
               log.append(f"{wrestler['name']} stamina: {current} → {drained}")
   ```

4. **Hook into pre-match** (stamina affects rating):
   ```python
   def apply_pre_match(self, ...):
       # If stamina < 50, apply penalty
       if wrestler.get("stamina", 100) < 50:
           adjustments[side] -= 100
   ```

5. **Add recovery logic** (in season advancement):
   ```python
   def _advance_season(self, log):
       for wrestler in roster["wrestlers"]:
           stamina = wrestler.get("stamina", 100)
           max_stam = wrestler.get("max_stamina", 100)
           recovered = min(max_stam, stamina + self.config.stamina_recovery_per_week)
           wrestler["stamina"] = recovered
   ```

6. **Add GUI support**:
   - Display stamina bar in roster tab
   - Add config option in settings

7. **Write tests**:
   ```python
   def test_stamina_drains_after_match(self):
       config = {"enable_stamina": True, "stamina_drain_per_match": 10}
       # ... create and simulate match ...
       assert wrestler["stamina"] == 90
   ```

### Adding a New Special Match Type (e.g., Battle Royal)

Battle Royals require more than data changes - they need new logic:

1. **Create new match class** (`src/engine/match.py`):
   ```python
   class BattleRoyalMatch:
       def __init__(self, participants, game_data):
           self.participants = [Wrestler(p) for p in participants]
           self.eliminated = []
           self.game_data = game_data
           self.result_log = []
       
       def simulate(self):
           # Pair wrestlers into mini-battles
           # Roll for eliminations
           # Track last wrestler standing
           # Return winner
       
       def _pair_wrestlers(self):
           # Implementation
       
       def _mini_battle(self, w1, w2):
           # Use brawling + overall
           rating_w1 = w1.get_base_overall() + w1.get_attribute_value("brawling")
           rating_w2 = w2.get_base_overall() + w2.get_attribute_value("brawling")
           # Determine elimination
   ```

2. **Update factory function**:
   ```python
   def create_match(..., match_format="singles"):
       if match_format == "battle_royal":
           return BattleRoyalMatch(...)
       elif is_tag:
           return TagMatch(...)
       else:
           return Match(...)
   ```

3. **Add CLI support** (`main.py`):
   ```python
   parser.add_argument("--battle-royal", action="store_true")
   parser.add_argument("--participants", nargs="+")
   ```

4. **Add GUI support** (`src/gui/app.py`):
   - New match format option
   - Multi-select for participants

5. **Write comprehensive tests**:
   ```python
   class BattleRoyalTests(unittest.TestCase):
       def test_last_wrestler_wins(self):
       def test_brawling_affects_eliminations(self):
       def test_all_but_one_eliminated(self):
   ```

## Testing Best Practices

### Unit Testing

Test individual components in isolation:

```python
def test_wrestler_attribute_normalization(self):
    wrestler_data = {"name": "Test", "attributes": {"Strength": 50}}
    wrestler = Wrestler(wrestler_data)
    
    # Should handle case variations
    assert wrestler.get_attribute_value("strength") == 50
    assert wrestler.get_attribute_value("STRENGTH") == 50
```

### Integration Testing

Test multiple components together:

```python
def test_full_match_flow(self):
    # Create wrestlers
    # Create match
    # Simulate
    # Verify result structure
    # Verify data persistence
```

### Mocking Dice Rolls

For deterministic tests, mock randomness:

```python
def test_specific_match_outcome(self):
    with patch('random.randint') as mock_rand:
        mock_rand.side_effect = [
            5,   # Match modifier roll (Cheating)
            4,   # Pre-match chart (Face)
            50,  # Pre-match event
            75,  # Result roll (High wins)
            30   # Win chart roll
        ]
        result = match.simulate()
        assert "Clean pin" in result
```

### Test Data Isolation

Use pytest fixtures for temporary data:

```python
@pytest.fixture
def temp_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    # Create test JSON files
    return data_dir
```

## Debugging Tips

### Enable Debug Logging

Matches already log debug info:
```python
result = match.simulate()
for line in match.result_log:
    if line.startswith("[DEBUG]"):
        print(line)
```

### Inspect Data Files

During development, manually check JSON files:
```python
import json
with open("data/wrestlers.json") as f:
    data = json.load(f)
    print(json.dumps(data, indent=2))
```

### GUI Debugging

Add print statements in event handlers:
```python
def on_simulate_match(self):
    print(f"DEBUG: Simulating {wrestler1} vs {wrestler2}")
    print(f"DEBUG: Match type: {self.match_type}")
    # ... rest of handler
```

### Test Individual Functions

Use Python REPL for quick testing:
```python
>>> from src.engine.wrestler import Wrestler
>>> w = Wrestler({"name": "Test", "overall": 2500})
>>> w.get_base_overall()
2500
```

## Code Style Guidelines

### Naming Conventions
- **Classes:** PascalCase (`Match`, `TagTeam`)
- **Functions:** snake_case (`simulate()`, `get_attribute_value()`)
- **Private methods:** Leading underscore (`_find_wrestler()`)
- **Constants:** UPPER_SNAKE_CASE (rare in this project)

### Docstrings
Use docstrings for public APIs:
```python
def create_match(wrestler_a_data, wrestler_b_data, match_type, game_data, assigned_roles):
    """
    Factory function to create a Match or TagMatch instance.
    
    Args:
        wrestler_a_data: Dict of wrestler A data
        wrestler_b_data: Dict of wrestler B data
        match_type: String match type (e.g., "TV Taping")
        game_data: Dict of game rules and charts
        assigned_roles: Dict mapping wrestler names to Face/Heel
    
    Returns:
        Match or TagMatch instance
    """
```

### Type Hints
Add type hints where beneficial:
```python
def get_attribute_value(self, attribute: str) -> float:
    """Get normalized attribute value."""
    # ...
```

### Error Handling
Provide helpful error messages:
```python
if not wrestlers:
    raise ValueError("TagTeam requires at least one member")

if preferred_upper not in ("A", "B", None):
    raise ValueError(f"Invalid face_team value: {preferred_face}")
```

## Performance Optimization

### Current Performance Characteristics
- **Match simulation:** <1ms per match
- **Roster loading:** ~10ms for 100 wrestlers
- **GUI rendering:** Instant for typical use cases

### Bottlenecks to Watch
1. **JSON file writes** - Atomic writes add I/O overhead
   - Optimization: Batch multiple changes into single save
2. **Large rosters** - 1000+ wrestlers slows GUI
   - Optimization: Pagination, lazy loading
3. **Season simulations** - Simulating entire season of matches
   - Optimization: Background threads, progress indicators

## Extending the GUI

### Adding a New Tab

1. **Create tab class**:
   ```python
   class NewTab(ttk.Frame):
       def __init__(self, parent, data_store):
           super().__init__(parent)
           self.data_store = data_store
           self._build_ui()
       
       def _build_ui(self):
           # Add widgets
       
       def refresh(self):
           # Update display when data changes
   ```

2. **Register in main app**:
   ```python
   class UltraQuickWrestlingApp:
       def _create_tabs(self):
           # ... existing tabs ...
           self.new_tab = NewTab(self.notebook, self.data_store)
           self.notebook.add(self.new_tab, text="New Tab")
   ```

### GUI Best Practices
- **Always refresh** after data changes: `self.data_store.reload()`
- **Use Treeview** for lists/tables
- **Messagebox** for errors and confirmations
- **Toplevel** for modal dialogs

## Common Pitfalls

### 1. Modifying Wrestler Data Without Saving
```python
# ❌ Wrong: Changes only in memory
wrestler["overall"] += 100

# ✅ Correct: Use repository function
repository.update_wrestler(wrestler_name, {"overall": new_value})
```

### 2. Forgetting to Reload Data in GUI
```python
# ❌ Wrong: Data out of sync
self.create_event(...)

# ✅ Correct: Reload after changes
self.create_event(...)
self.data_store.reload()
self.refresh_event_list()
```

### 3. Hardcoding Game Logic
```python
# ❌ Wrong: Hardcoded
if match_type == "TV Taping":
    unusual_chance = 0.30

# ✅ Correct: Data-driven
result_entry = game_data["win_charts"][match_type][winner_side][roll]
```

### 4. Not Handling Missing Attributes
```python
# ❌ Wrong: KeyError if attribute missing
strength = wrestler["attributes"]["strength"]

# ✅ Correct: Use Wrestler class
strength = Wrestler(wrestler).get_attribute_value("strength")
```

## Release Checklist

Before releasing a new version:

- [ ] All tests pass (`pytest tests/`)
- [ ] No lint errors
- [ ] Update version number (readme, changelog)
- [ ] Update ROADMAP.md with new features
- [ ] Update ARCHITECTURE.md if design changed
- [ ] Add migration guide if data format changed
- [ ] Test with real roster data
- [ ] Test GUI on Windows/Mac/Linux
- [ ] Create git tag (`v1.1.0`)
- [ ] Write release notes

## Getting Help

- **Read the docs:** Start with ARCHITECTURE.md and ROADMAP.md
- **Check tests:** See how existing features are tested
- **Ask questions:** Open a GitHub issue with "Question" label
- **Study the code:** It's well-commented and structured

## Contributing Your Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/battle-royal`)
3. Make your changes
4. Write tests
5. Update documentation
6. Commit with clear messages
7. Push and create a pull request

Happy coding! 🎮🤼
