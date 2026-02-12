# Ultra Quick Wrestling - Feature Implementation Roadmap

## Current Status Summary

This document tracks the implementation status of all Ultra Quick Wrestling features from the official rulebook. It serves as a guide for understanding what's complete, in progress, and planned for future development.

**Last Updated:** February 12, 2026

---

## Core Match Engine ✅ Complete

### Basic Match Flow ✅
- [x] Match type selection (TV Taping, PPV, Cage, No DQ, Specialty)
- [x] Wrestler attribute system (Overall, Strength, Speed, Savvy, Technical, Cheating, Size, Heat)
- [x] Match modifier roll (d10 → determines which attribute affects rating)
- [x] Pre-match chart roll (d10 → targets Face or Heel)
- [x] Pre-match event roll (d100 → applies temporary and permanent effects)
- [x] Match rating calculation (Overall + Modifier + Adjustments)
- [x] Result chart lookup (rating differential → winner probability)
- [x] Win chart consultation (match type + winner → finish description)
- [x] Unusual results handling
- [x] Match narration/logging system

### Wrestler Attributes ✅
- [x] Core stats: Overall, Strength, Speed, Savvy, Technical, Cheating, Size, Heat
- [x] Specialty bonuses: Cage, Object, Brawling, Ladder, Table, Tag
- [x] Finisher moves
- [x] Face/Heel personas
- [x] Attribute normalization (handles variations in naming)
- [x] Dynamic modifiers (overall_modifier, heat_modifier)

### Match Types ✅
- [x] TV Taping
- [x] PPV Match
- [x] Cage Match
- [x] No DQ Match
- [x] Specialty Match
- [x] Custom match types (data-driven via game_data.json)

---

## Tag Team Matches ✅ Complete

- [x] Multi-wrestler team support
- [x] Tag attribute bonus calculation
- [x] Team overall averaging
- [x] Tag-specific win charts
- [x] Fallback to singles charts when tag charts unavailable
- [x] Face/Heel team assignment
- [x] Mixed persona team handling
- [x] CLI support (`--tag`, `--team-a`, `--team-b`, `--face-team`)
- [x] GUI support for tag team booking

---

## Advanced Rules System ✅ Complete (All Features)

### Injury System ✅
- [x] Random injury chance after matches (configurable %, default 15%)
- [x] Injury duration tracking (default 3 weeks)
- [x] Injury penalty to ratings (configurable, default -100)
- [x] Automatic recovery countdown
- [x] Injury status display in GUI

### Title/Championship System ✅
- [x] Belt creation and management
- [x] Champion tracking
- [x] Automatic title swaps on match results
- [x] Title-on-the-line match designation
- [x] Championship bonus to Overall rating (configurable, default +100 for world title, +50 for secondary)
- [x] Title lineage tracking
- [x] Belt data persistence (belts.json)

### Heat/Momentum System ✅
- [x] Heat attribute for wrestlers
- [x] Heat modifier tracking (persistent)
- [x] Heat changes on title wins/losses
- [x] Heat increases on clean wins
- [x] Heat decreases on clean losses
- [x] Configurable heat delta values
- [x] Heat affects match ratings

### Rivalry System ✅
- [x] Rivalry/feud tracking
- [x] Heat bonuses for rivals facing each other
- [x] Heat penalties when rivals lose
- [x] Integration with storyline system

### Season/Campaign Tracking ✅
- [x] Multi-week season structure
- [x] Week-by-week progression
- [x] Configurable season length (default 12 weeks)
- [x] Injury recovery countdown per week
- [x] Season state persistence

### Persistent Modifiers ✅
- [x] Overall rating adjustments (overall_modifier)
- [x] Heat modifiers (heat_modifier)
- [x] Clean win bonus (configurable, default +20)
- [x] Clean loss penalty (configurable, default -25)
- [x] Champion bonuses
- [x] Permanent pre-match event effects

---

## Booking & Event Management ✅ Complete

### Event System ✅
- [x] Event card creation
- [x] Match booking on cards
- [x] Event metadata (name, date, venue, notes)
- [x] Multi-match event support
- [x] Event persistence (events.json)
- [x] Event CRUD operations

### Storyline System ✅
- [x] Storyline/feud creation
- [x] Participant tracking
- [x] Story beat logging (timeline of events)
- [x] Storyline-to-match linking
- [x] Story progression tracking
- [x] Storyline CRUD operations

### Match Booking ✅
- [x] Face/Heel side designation
- [x] Match type selection
- [x] Belt assignment to matches
- [x] Storyline linkage
- [x] Tag team match booking
- [x] Match results integration with storylines

---

## Data Management ✅ Complete

### Repository Layer ✅
- [x] Wrestler CRUD operations
- [x] Belt CRUD operations
- [x] Game data loading
- [x] Atomic file writes (prevents data corruption)
- [x] Data normalization
- [x] Backward compatibility with legacy formats

### File Structure ✅
- [x] wrestlers.json
- [x] belts.json
- [x] game_data.json
- [x] events.json
- [x] Image asset organization (Male/Female wrestler images)

---

## User Interfaces

### Command-Line Interface (CLI) ✅ Complete
- [x] Wrestler selection by number
- [x] Match type selection
- [x] Tag team match support
- [x] Advanced rules configuration via CLI args
- [x] JSON/list input parsing for teams
- [x] Face/Heel assignment
- [x] Match narration output
- [x] Result logging

### Graphical User Interface (GUI) 🔄 Mostly Complete
- [x] Multi-tab interface
- [x] Roster management tab
  - [x] Wrestler CRUD
  - [x] Attribute editing
  - [x] Image management
- [x] Quick match tab
  - [x] Singles match simulation
  - [x] Tag match simulation
  - [x] Match type selection
  - [x] Result display
- [x] Booking tab
  - [x] Event creation/editing
  - [x] Match booking
  - [x] Storyline management
  - [x] Story beat logging
- [x] Season tab
  - [x] Week advancement
  - [x] Injury tracking
  - [x] Season statistics
- [ ] **Pending GUI Improvements:**
  - [ ] Batch wrestler import/export
  - [ ] Advanced search/filter in roster
  - [ ] Visual match result history
  - [ ] Storyline visualization/flowchart
  - [ ] Season calendar view

---

## Special Match Types

### Implemented ✅
- [x] Standard Singles
- [x] Tag Team (2v2, 3v3, any combination)
- [x] TV Taping (with increased unusual finish chance)
- [x] PPV (cleaner finishes)
- [x] Cage Match
- [x] No DQ Match
- [x] Specialty Match (ladder, table, etc.)

### Rulebook Special Matches - Pending ⏳

#### Battle Royal ⏳ Planned
- [ ] Multi-competitor match type
- [ ] Elimination tracking
- [ ] Brawling attribute focus
- [ ] Last wrestler standing wins
- [ ] Pairing logic for mini-battles
- [ ] Over-the-top-rope eliminations
- **Status:** Not yet implemented. Requires new match class.

#### Royal Rumble ⏳ Planned
- [ ] Timed entry system
- [ ] 30-wrestler support (or configurable)
- [ ] Elimination tracking
- [ ] Entry number strategy
- [ ] "Iron Man" performance tracking
- **Status:** Not yet implemented. Requires new match class and entry system.

#### Ladder Match ✅ Partial
- [x] Match type selection
- [x] Ladder attribute bonus
- [x] Specialty win chart
- [ ] Ladder-specific event tables (falling, climbing fails, etc.)
- **Status:** Basic support via specialty bonus. Could be enhanced with unique events.

#### Table Match ✅ Partial
- [x] Match type selection
- [x] Table attribute bonus
- [x] Specialty win chart
- [ ] Table-specific breaking mechanics
- **Status:** Basic support via specialty bonus.

#### Steel Cage Variations ⏳
- [x] Standard Cage Match
- [ ] Hell in a Cell (hardcore + cage)
- [ ] WarGames (multi-team cage)
- **Status:** Standard cage complete. Variations need unique rules.

---

## Optional Rules from Rulebook

### Implemented ✅
- [x] Championship tracking
- [x] Injury system
- [x] Heat/momentum
- [x] Rivalries affecting Heat
- [x] Season structure
- [x] Overall rating modifiers (clean win/loss)
- [x] Title bonuses to ratings

### Documented but Not Implemented ⏳

#### Manager/Valet System ⏳
- [ ] Manager attributes (Interference, Distraction)
- [ ] Manager-to-wrestler assignment
- [ ] Manager effects on match outcomes
- [ ] Manager interaction rolls
- **Status:** Mentioned in rulebook. Not implemented.

#### Referee Bias ⏳
- [ ] Referee stats (Fast Count, Slow Count, Corrupt)
- [ ] Ref assignment to matches
- [ ] Ref-specific event triggers
- **Status:** Not implemented.

#### Run-In System ⏳
- [ ] Enhanced run-in mechanics
- [ ] Inter-match interference
- [ ] Automatic storyline beat creation on run-ins
- **Status:** Run-ins exist in unusual results but not as a full system.

#### Promo/Interview Segments ⏳
- [ ] Non-match segments on cards
- [ ] Promo skill attribute
- [ ] Heat changes from promos
- [ ] Storyline advancement from promos
- **Status:** Not implemented as formal system.

#### Stable/Faction System ⏳
- [ ] Stable creation and management
- [ ] Stable member tracking
- [ ] Stable synergy bonuses
- [ ] Inter-stable feuds
- **Status:** Not implemented.

#### Tournament Mode ⏳
- [ ] Bracket generation
- [ ] Tournament round tracking
- [ ] Automatic advancement
- [ ] Tournament winner determination
- [ ] King of the Ring, etc.
- **Status:** Not implemented.

---

## Testing & Quality Assurance

### Test Coverage ✅
- [x] Core match simulation tests
- [x] Tag match tests
- [x] Match modifier tests
- [x] Advanced rules tests
- [x] Booking system tests
- [x] Repository/data layer tests
- [x] Game data normalization tests
- [x] CLI argument parsing tests

### Pending Testing ⏳
- [ ] GUI integration tests
- [ ] Performance benchmarks (large rosters)
- [ ] Data migration tests
- [ ] Stress tests (many matches, seasons)

---

## Documentation

### Completed ✅
- [x] README.md (setup and basic usage)
- [x] ARCHITECTURE.md (system design)
- [x] ROADMAP.md (this document)
- [x] Rules documentation (Markdown and PDF)
- [x] Code comments and docstrings

### Pending 📝
- [ ] API Reference (detailed function/class docs)
- [ ] Developer Guide (extending the system)
- [ ] User Manual (GUI walkthrough)
- [ ] Video tutorials/demos
- [ ] Example scenarios/campaigns

---

## Future Enhancements & Ideas 💡

### Short-Term (Next Release)
1. **Battle Royal Support** - Implement multi-competitor elimination matches
2. **GUI Polish** - Add missing features (batch import, visual history)
3. **Tournament Mode** - Bracket-based competition support
4. **Manager System** - Add manager/valet mechanics

### Medium-Term
1. **Stable/Faction System** - Group wrestler management
2. **Referee System** - Ref bias and effects
3. **Enhanced Promo System** - Non-match segments
4. **AI Booker** - Automated booking suggestions based on Heat, storylines
5. **Match Replays** - Save and replay match simulations

### Long-Term
1. **Web-Based UI** - Browser-based interface with REST API
2. **Database Backend** - SQLite/PostgreSQL for large federations
3. **Multiplayer/League Mode** - Multiple users booking same federation
4. **Historical Statistics** - Career records, hall of fame
5. **Scenario Editor** - Custom storylines and campaigns
6. **Steam Workshop Integration** - Share rosters and scenarios

---

## Implementation Priority Guide

### Priority 1 (High) - Core Gameplay 🔴
All core match types and basic features are **complete**.

### Priority 2 (Medium) - Enhanced Experience 🟡
- [ ] Battle Royal
- [ ] Tournament Mode
- [ ] GUI improvements
- [ ] Manager system

### Priority 3 (Low) - Nice-to-Have 🟢
- [ ] Referee system
- [ ] Stable system
- [ ] Advanced promo system
- [ ] AI Booker

### Priority 4 (Future) - Major Features 🔵
- [ ] Web interface
- [ ] Database backend
- [ ] Multiplayer support

---

## How to Contribute

If you're looking to add features from this roadmap:

1. **Pick a feature** from the "Pending" or "Planned" sections
2. **Review the architecture** in ARCHITECTURE.md
3. **Check existing tests** for similar features
4. **Implement incrementally** - start with data model, then engine logic, then UI
5. **Add tests** for your new feature
6. **Update documentation** (this roadmap and relevant docs)

---

## Version History

- **v1.0** (Current) - Core match engine, tag matches, advanced rules, GUI, booking system
- **v0.9** - Initial CLI implementation, basic matches
- **v0.5** - Prototype/concept phase

---

## Questions or Suggestions?

This roadmap is a living document. If you have ideas for features or improvements not listed here, consider:
- Opening a GitHub issue
- Discussing in the project's community channels
- Proposing a new feature in a pull request

**The goal:** A comprehensive, faithful recreation of Ultra Quick Wrestling with modern conveniences and extensibility!
