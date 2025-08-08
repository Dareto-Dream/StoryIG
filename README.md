# 🎵 Cadence Collapse

**Cadence Collapse** is a **visual novel + rhythm game hybrid** with heavy psychological horror elements.
It blends branching narrative, FNF-style minigame mechanics, and an emotional scoring system that changes the story based on player performance.

---

## 📖 Overview

You join a high school music club.
You think you’re here to make friends and play songs.
You’re wrong.

The closer you get to the members, the more their cracks show — and the more your actions in the music will shape their fate.
By the final act, your decisions and performance will determine who heals, who rots, and if the club survives at all.

---

## 🎮 Gameplay

* **Visual Novel** — Story-driven progression with branching dialogue and choices.
* **Rhythm Minigame** — Four-lane FNF-style input, duet/ensemble modes, AI opponent rendering.
* **Rot Score System** — Each major character has a score from *rot* (0) to *breakthrough* (7).
  Lower = emotional decay. Higher = emotional recovery.
* **Puppeteer Mode** — Late-game mechanic where control is split between characters, reflecting chaos in the narrative.
* **Multiple Endings** — Good, subpar, and bad routes determined by story choices and rhythm performance.

---

## 📂 Project Structure

```
/assets
    /characters   → Character sprites & animations
    /backgrounds  → VN backgrounds
    /music        → OST & rhythm tracks
    /charts       → JSON rhythm charts
/src
    conductor.py       → Game startup & timing manager
    note_handler.py    → Input + animation triggers
    arrow_handler.py   → Arrow rendering
    judgement.py       → Hit/miss scoring logic
    character_renderer.py
    chart_handler.py
/docs
    design_notes.md
    story_outline.md
```

---

## 🏛 Acts & Endings

### Acts

1. **Harmony** — Introduction & tutorial
2. **Syncopation** — Longest act; emotional center
3. **Reverberation** — Hanami’s disappearance
4. **Puppeteer** — Chaos and branching
5. **Cadence Collapse** — Final confrontation

### Endings

* **Good – Cadence Rewritten** — Two breakthroughs, no rots.
* **Subpar – Cadence Continues** — Mixed recovery; sudden tragedy.
* **Bad – Disbanded** — All characters in rot.

---

## 🛠 Tech Stack

* **Engine:** Python 3 + Pygame
* **Rendering:** Modular VN + rhythm subsystems
* **Data Format:** JSON (charts, story scripts)
* **Audio:** MP3 + OGG playback
* **Animation:** Frame-based sprite sheets

---

## 🚀 Availability

The game is currently in **active development**.
A **Windows Alpha** build is planned for release **soon**.
Once available, this section will include download links and installation instructions.

---

## 👥 Credits

* **Lead Developer / Writer:** DeltaV
* **Animation:** Melody (characters), placeholder art by DeltaV
* **Music:** Freelance composers + in-house tracks
* **Testing & Feedback:** Internal team & early playtesters

---

> *"You think you can save them?*
> *Play it again, and watch them break."*