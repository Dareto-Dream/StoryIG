# AGENTS.md

## VN Engine & Minigame Engine: Purpose and Architecture

---

### Purpose

This project is a hybrid **visual novel (VN) engine** with an embedded, modular **FNF-inspired rhythm minigame engine**.  
It’s designed for:

- Narrative-driven games (visual novels, interactive stories)
- Seamless integration of advanced minigames (not just FNF, but also possible StepMania/Osu/etc)
- Flexible story scripting (branching, dynamic, or act-based VNs)
- Highly modular minigame system: supports multiple sides, AI/bot play, advanced opponent “puppeteer” logic, and custom charts.

---

### Philosophy

- **Decouple** narrative and minigame logic—each is a “core agent” in the system.
- **Legacy loader** handles all chart/data quirks so the engine stays clean and future-proof.
- Everything should be **data-driven**: all game logic, minigames, and content are loaded from JSON or external files.
- Designed to be extensible—easy to add new minigame types, chart formats, AI behaviors, or story logic.

---

## Core Agents/Modules

### 1. Visual Novel Agent
- Handles: story progression, page/script parsing, user input for choices, character dialogue, and branching logic.
- On reaching a story event of type `"game"`, pauses the VN and launches a minigame.

### 2. Minigame Conductor
- Entry point for minigame sessions.
- Loads charts, music, and modular side configs.
- Spawns and manages LaneManagers for each “side” (player, opponents, AI bots).
- Delegates input, update, and rendering to each LaneManager.
- Handles music sync and global song time.

### 3. LaneManager
- Owns all state for one lane group (player or opponent).
- Tracks its own chart, current notes, animator, arrows, and input mapping.
- Spawns notes using ChartHandler and manages their lifecycle via NoteHandler.
- Handles per-section rendering using FNF-style 2-section scroll math.
- Receives and processes player or AI input for judgments/animations.

### 4. ChartHandler
- Handles procedural spawning of notes from the chart for each LaneManager.
- Supports per-note and per-section BPM, scroll speed, and timing.
- Works with the Legacy Loader to accept normalized note data.

### 5. NoteHandler
- Manages all active notes (by lane/direction).
- Handles note hits, releases, misses, and passes data to judgment module.

### 6. Legacy Loader
- Handles all chart format quirks (FNF JSON, StepMania, etc).
- Splits charts into per-side notes, assigns per-section BPM/speed, and builds section timing tables.
- Outputs standardized data to the engine (notes, bpm, song speed, section table, etc).

### 7. Opponent Renderer / AI (if applicable)
- Handles “bot” play or puppeteer mechanics (where the game or another character hits notes).
- Supports modular multi-opponent duets, puppeteer, or “band” setups.

---

## Technical Highlights

- **Section-based rendering:** Accurate FNF-style two-section scroll for perfect sync with per-section BPM/scroll speed changes.
- **Legacy compatibility:** Loader ensures any chart format (old or new) is rendered and played back correctly.
- **Extensible input:** Side configs in Conductor allow easy changes to keymaps, side layouts, and AI controllers.
- **Real modularity:** Each LaneManager operates independently (supporting duets, bands, advanced AIs).

---

## Typical Flow

1. **VN engine runs story script**
2. When a `"game"` event is reached, VN pauses and launches minigame
3. **Conductor** loads chart/audio via Legacy Loader, sets up LaneManagers (player/opponents)
4. Each **LaneManager** runs update/render/handle_input using accurate timing/scroll logic from section table
5. **NoteHandlers** manage active notes, **ChartHandlers** spawn them per timing
6. **Legacy Loader** ensures chart quirks are handled
7. Minigame ends, returns control to VN

---

## File Map / Core Modules

- `conductor.py`: Entry for minigame, manages LaneManagers, song timing, music.
- `lane_manager.py`: Per-side logic, chart spawning, input, rendering.
- `chart_handler.py`: Note spawn logic, timing, prebuffer.
- `note_handler.py`: Handles active notes, by direction.
- `note.py`: Note object logic, per-note timing/scroll, draw.
- `legacy_loader.py`: Chart format parser, chart/section splitter, returns normalized data.
- `character_animations.py`: Handles all character animation logic.
- `opponent_renderer.py`: Handles AI/bot play and special opponent modes.

---

## Adding New Minigames or Features

- **To add new chart formats:** Update `legacy_loader.py` to parse and normalize.
- **To add new opponents/AIs:** Create new LaneManagers or AI modules and add to `side_configs`.
- **To add new VN/game features:** Update story parser and event triggers; minigame agent is fully modular.

---

## Vision

This engine is designed for **total creative freedom** and **maximum technical flexibility** for narrative rhythm games and VN/minigame hybrids,  
from standard FNF to duets, multi-character, or experimental rhythm scenes.

---

*(For architecture diagrams, tech breakdowns, or usage guides, expand this file or add subpages!)*

