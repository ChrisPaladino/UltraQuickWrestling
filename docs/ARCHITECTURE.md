# Ultra Quick Wrestling - Architecture Documentation

## Overview

Ultra Quick Wrestling (UQW) is a Python-based simulation of the 1991-era pro wrestling board game. The application features both a command-line interface and a Tkinter GUI for simulating wrestling matches using wrestler statistics and dice-based game mechanics.

## System Architecture

### Component Layers

```
┌─────────────────────────────────────────┐
│        User Interfaces                  │
│  ┌──────────┐      ┌───────────────┐   │
│  │ CLI      │      │ GUI (Tkinter) │   │
│  │ main.py  │      │ src/gui/app.py│   │
│  └──────────┘      └───────────────┘   │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│        Engine Layer                     │
│  ┌─────────────────────────────────┐   │
│  │ Match Simulation (match.py)     │   │
│  │ - Match workflow execution      │   │
│  │ - Dice rolls & rule application │   │
│  │ - Tag team support              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │ Wrestler    │  │ Booking         │  │
│  │ (wrestler.py)  │  (booking.py)   │  │
│  │ - Attributes│  │ - Events        │  │
│  │ - Ratings   │  │ - Storylines    │  │
│  └─────────────┘  └─────────────────┘  │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Advanced Rules                  │   │
│  │ (advanced_rules.py)             │   │
│  │ - Injuries, Titles, Heat        │   │
│  │ - Rivalries, Season tracking    │   │
│  └─────────────────────────────────┘   │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│        Data Layer                       │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │ Repository  │  │ File Utils      │  │
│  │ (repository)│  │ (file_utils.py) │  │
│  │ - CRUD ops  │  │ - Atomic writes │  │
│  └─────────────┘  └─────────────────┘  │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│        Data Storage (JSON)              │
│  - wrestlers.json                       │
│  - belts.json                           │
│  - game_data.json                       │
│  - events.json                          │
└─────────────────────────────────────────┘
```

## Core Components

### 1. Match Simulation Engine (`src/engine/match.py`)

The heart of the application. Implements the full UQW rulebook match flow:

**Key Classes:**
- `Match` - Singles match simulation
- `TagMatch` - Tag team match simulation (extends Match)
- `TagTeam` - Represents a team of wrestlers

**Match Workflow:**
1. **Match Modifier Roll** (d10) - Determines which attribute modifies base rating
2. **Pre-Match Chart Roll** (d10) - Determines target (Face/Heel)
3. **Pre-Match Event Roll** (d100) - Applies temporary/permanent modifiers
4. **Calculate Match Ratings** - Base Overall + Modifier Attribute + Adjustments
5. **Result Determination** (d100) - Based on rating differential
6. **Win Chart Consultation** - Determines match outcome and finish
7. **Post-Match Processing** - Applies advanced rules effects

**Factory Function:**
```python
create_match(
    wrestler_a_data,
    wrestler_b_data,
    match_type,
    game_data,
    assigned_roles,
    is_tag=False,
    advanced_rules_config=None,
    booking_context=None
)
```

### 2. Wrestler Model (`src/engine/wrestler.py`)

Represents individual wrestlers with their attributes and ratings.

**Attributes:**
- `name` - Wrestler's name
- `persona` - "Face" or "Heel"
- `finisher` - Signature finishing move
- `overall` - Base rating (primary stat)
- Core Attributes: `strength`, `speed`, `savvy`, `technical`, `cheating`, `size`, `heat`
- Specialty Attributes: `cage`, `object`, `brawling`, `ladder`, `table`, `tag`
- Dynamic Properties: `overall_modifier`, `heat_modifier`, `injured`, `titles`

**Key Methods:**
- `get_base_overall()` - Returns overall + overall_modifier
- `get_attribute_value(attr)` - Returns normalized attribute value
- `normalize_attribute_name(name)` - Handles attribute name variations

### 3. Booking System (`src/engine/booking.py`)

Manages events, storylines, and long-term narratives.

**Key Classes:**
- `EventCard` - Represents a wrestling show/event
- `CardMatch` - A match on an event card
- `Storyline` - Tracks feuds and rivalries
- `StoryBeat` - Individual moments in a storyline
- `MatchBookingContext` - Context for match simulation

**Booking Functions:**
- `load_state()` / `save_state()` - Persist booking data
- `upsert_event()`, `update_event()`, `delete_event()`
- `add_match_to_event()`, `update_match()`, `delete_match()`
- `upsert_storyline()`, `add_beat_to_storyline()`

### 4. Advanced Rules Engine (`src/engine/advanced_rules.py`)

Implements optional rules for campaign/season play.

**Features:**
- **Injuries** - Random injury system with recovery tracking
- **Titles** - Championship tracking and title changes
- **Heat** - Wrestler momentum/popularity tracking
- **Rivalries** - Enhanced heat for feuding wrestlers
- **Seasons** - Multi-week campaign tracking
- **Persistent Modifiers** - Long-term rating adjustments

**Configuration:**
```python
AdvancedRulesConfig(
    enabled=True,
    enable_injuries=True,
    enable_titles=True,
    enable_rivalries=True,
    enable_heat=True,
    enable_seasons=True,
    injury_chance=0.15,
    injury_penalty=-100,
    clean_win_bonus=20,
    clean_loss_penalty=-25
)
```

### 5. Repository Layer (`src/engine/repository.py`)

Provides data access abstraction for all JSON files.

**Key Functions:**
- Wrestler Management: `load_wrestlers()`, `create_wrestler()`, `update_wrestler()`, `delete_wrestler()`
- Belt Management: `load_belts()`, `create_belt()`, `update_belt()`, `delete_belt()`, `assign_belt()`, `vacate_belt()`
- Game Data: `load_game_data()`
- Events: Via booking module

**Data Integrity:**
- Atomic writes via `safe_write_json()` (temp file + atomic replace)
- Data normalization via `normalize_game_data()`

## Data Models

### Game Data Structure (`data/game_data.json`)

```json
{
  "match_modifiers": [
    {"roll": 0-9, "modifier": "Size|Normal|Strength|Speed|..."}
  ],
  "pre_match_chart": [
    {"roll": 0-9, "result": "Face|Heel"}
  ],
  "pre_match_events": {
    "Face": [{"roll": "01-02", "event": "...", "effect": {...}}],
    "Heel": [...]
  },
  "result_chart": [
    {"difference": "0-50", "roll": "01-50", "result": "High-Rated Wins"},
    ...
  ],
  "win_charts": {
    "TV Taping": {
      "Heel Wins": [...],
      "Face Wins": [...]
    },
    "PPV": {...},
    "Cage Match": {...},
    ...
  },
  "tag_win_charts": {
    "Tag Team Match": {...}
  },
  "unusual_results": [...]
}
```

### Wrestler Data Structure (`data/wrestlers.json`)

```json
{
  "wrestlers": [
    {
      "name": "Wrestler Name",
      "persona": "Face|Heel",
      "finisher": "Finishing Move",
      "overall": 2500,
      "attributes": {
        "strength": 50,
        "speed": 100,
        "savvy": 75,
        "technical": 80,
        "cheating": -50,
        "size": 0,
        "heat": 5,
        "cage": 0,
        "object": 50,
        "brawling": 25,
        "ladder": 0,
        "table": 0,
        "tag": 100
      },
      "overall_modifier": 0,
      "heat_modifier": 0,
      "injured": false,
      "injury_duration": 0,
      "titles": []
    }
  ]
}
```

## Match Simulation Flow

### Singles Match

```
1. Initialize Match(wrestler_a, wrestler_b, match_type, game_data, roles)
2. simulate():
   a. Roll Match Modifier (d10)
      → Determines attribute bonus (e.g., Cheating, Speed)
   
   b. Roll Pre-Match Chart (d10)
      → Targets Face or Heel for pre-match event
   
   c. Roll Pre-Match Event (d100)
      → Apply temporary modifiers (this match)
      → Apply permanent changes (career)
      → Advanced Rules: injuries, heat, etc.
   
   d. Calculate Match Ratings
      Face Rating = Overall + Modifier Attribute + Adjustments
      Heel Rating = Overall + Modifier Attribute + Adjustments
   
   e. Determine Difference & Winner Probability
      Difference = |Face Rating - Heel Rating|
      → Look up win probability on result_chart
   
   f. Roll Result (d100)
      → Determines if high-rated or low-rated wins
   
   g. Roll Win Chart (d100)
      → Consult match_type win chart (TV/PPV/Cage/etc.)
      → Face Wins or Heel Wins table
      → Get finish description
   
   h. Process Unusual Results (if triggered)
      → Roll on unusual_results table
   
   i. Apply Post-Match Effects
      → Advanced Rules: title changes, injuries, heat updates
      → Update wrestler stats
      → Save changes
   
3. Return result_log (narrated match flow)
```

### Tag Team Match

Same as singles, but:
- Each side is a `TagTeam` object with multiple members
- Team Overall = Average of member overalls
- Tag Bonus = Average of member tag ratings
- Match Rating = Team Overall + Tag Bonus + Modifier Attribute + Adjustments
- Win charts can use tag-specific tables if available

## GUI Architecture (`src/gui/app.py`)

Tkinter-based application with multi-tab interface.

**Main Components:**
- `DataStore` - Centralized data management
- `UltraQuickWrestlingApp` - Main application window
- Tab Controllers:
  - `RosterTab` - Wrestler CRUD operations
  - `MatchTab` - Quick match simulation
  - `BookingTab` - Event scheduling and storylines
  - `SeasonTab` - Campaign/season management

**Data Flow:**
1. User action in GUI
2. DataStore methods called
3. Repository/Booking functions invoked
4. JSON files updated atomically
5. DataStore.reload() refreshes in-memory state
6. GUI refreshes to show updates

## Testing Strategy

**Test Coverage:**
- `test_match_modifiers.py` - Match modifier application
- `test_tag_match.py` - Tag team match mechanics
- `test_advanced_rules.py` - Optional rules features
- `test_booking.py` - Event and storyline management
- `test_repository.py` - Data access layer
- `test_game_data.py` - Data normalization
- `test_main_cli.py` - CLI argument parsing

**Test Approach:**
- Unit tests with mocked dice rolls for deterministic results
- Integration tests with real JSON data
- Temporary file fixtures for data isolation

## Extension Points

### Adding New Match Types

1. Add match type to `game_data.json` win_charts
2. Define win chart with Face/Heel result tables
3. Optionally add match-specific modifiers
4. Update GUI match type dropdown

### Adding New Wrestler Attributes

1. Add attribute to wrestler data model
2. Update `Wrestler.normalize_attribute_name()` if needed
3. Add to match modifiers chart if applicable
4. Update GUI wrestler editor

### Adding New Advanced Rules

1. Extend `AdvancedRulesConfig` dataclass
2. Implement logic in `AdvancedRulesEngine`
3. Hook into `apply_pre_match()` or `apply_post_match()`
4. Add configuration to GUI settings

## Design Principles

1. **Separation of Concerns** - Engine, UI, and data layers are distinct
2. **Data-Driven** - Game rules live in JSON, not hardcoded
3. **Atomic Operations** - File writes use temp files + atomic replace
4. **Extensibility** - Advanced rules are optional and configurable
5. **Testing** - Comprehensive test coverage for core logic
6. **Backward Compatibility** - Legacy wrestler data formats supported

## Performance Considerations

- In-memory caching in `AdvancedRulesEngine` for roster data
- Batch saves in GUI operations
- Atomic file writes prevent corruption but add I/O overhead
- JSON parsing is fast enough for typical roster sizes (<1000 wrestlers)

## Future Architecture Improvements

- Database backend option (SQLite) for large rosters
- REST API for web-based front ends
- Async match simulation for GUI responsiveness
- Plugin system for custom rules modules
- Replay/undo system for match results
