# Toilet Simulator — Game Design Bible

This is the creative source of truth. All game mechanics, level design, and
scoring decisions are documented here. When the design evolves, this doc evolves
with it.

---

## Concept

Toilet Simulator is an irreverent 2D top-down game where you play as a bloke
with a big belly who desperately needs a piss. The camera perspective is first
person — looking down past your gut at the toilet below. You can't see your
genitals (the belly blocks the view), just the stream arcing down toward the
bowl.

The aim: get it in the bowl. Don't piss on the floor.

Think PowerWash Simulator meets pub toilet on a Friday night.

---

## Player Character

- **Perspective:** Top-down, first person. The player sees their own belly,
  feet/shoes at the edges, and the toilet below.
- **Belly:** Large, round, partially obscures the view. The belly IS the
  character — it frames the entire game viewport.
- **Genitals:** Not visible. The stream appears from beneath the belly.
  This keeps it silly rather than crude.
- **Movement:** The player character is stationary (standing at the toilet).
  What moves is the stream aim direction, controlled by pointer input.

---

## Core Mechanic — The Stream

The pee stream is the central game mechanic. Everything revolves around
controlling it.

### Stream Properties
- **Origin:** Fixed point beneath the belly (bottom-centre of belly sprite)
- **Direction:** Controlled by pointer position (mouse now, touch later)
- **Arc:** The stream has a slight arc/gravity — it's not a laser beam
- **Spread:** Slight random spread to simulate realism and add challenge
- **Pressure:** Linked to bladder volume. Full bladder = strong stream,
  near-empty = weak dribble. Pressure affects reach and force.

### Stream Interaction
- **Bowl hit:** Scores points (or avoids penalty — see Scoring)
- **Floor hit:** Loses points (or triggers penalty)
- **Object hit:** Applies force to movable objects (power-wash mechanic)
- **Rim hit:** Could go either way — splash physics (stretch goal)

---

## Bladder System

The bladder meter is the level timer. You don't control when the level ends —
your bladder does.

- **Volume:** Starts full at level begin, depletes as you pee
- **Depletion rate:** Constant base rate, possibly modified by level
- **Display:** Vertical meter on HUD (like a health bar but for piss)
- **Level end:** When bladder hits zero, the level ends and score is tallied
- **Urgency:** No urgency mechanic initially. The stream just flows until empty.

---

## Scoring

**Status: TBD — iterating between two models.**

### Option A: Penalty Model
- Start with a perfect score
- Lose points for every unit of pee that hits the floor
- Bonus for hitting the bowl centre vs rim
- Clean finish bonus if zero floor hits

### Option B: Reward Model
- Start at zero
- Earn points for every unit of pee that lands in the bowl
- Multiplier for consecutive bowl hits (combo streak)
- Bonus for accuracy percentage at level end

### Decision Notes
- Both models will be prototyped in Level 1
- Whichever feels better in playtesting wins
- Log the decision here when made

**Active model:** _Not yet decided_

---

## Level Progression

Levels are unlocked linearly. Each level introduces a new challenge or gimmick.

### Level 1 — The Basics
- **Gimmick:** None. Standard toilet, standard controls.
- **Purpose:** Teach the player how to aim. Learn the stream physics.
- **Bowl:** Normal size
- **Modifiers:** None

### Level 2 — The Thimble
- **Gimmick:** Tiny toilet bowl
- **Purpose:** Precision challenge. The bowl is comically small.
- **Bowl:** Much smaller than standard
- **Modifiers:** None

### Level 3 — Earthquake
- **Gimmick:** The screen/world shakes periodically
- **Purpose:** Aim while the toilet moves beneath you
- **Bowl:** Normal size
- **Modifiers:** Screen shake (sinusoidal offset on the world position)

### Level 4 — Friday Night
- **Gimmick:** The player is drunk. Aim sways involuntarily.
- **Purpose:** Fight against your own input. The pointer has drift.
- **Bowl:** Normal size
- **Modifiers:** Sinusoidal drift applied to stream aim. Amplitude increases
  over the level (you're getting drunker).

### Level 5+ — Power Wash
- **Gimmick:** Objects are sitting on/around the bowl. Use stream pressure to
  clear them off before (or while) you pee.
- **Purpose:** Introduce the power-wash mechanic. Physics fun.
- **Bowl:** Normal size but obstructed
- **Modifiers:** Movable objects with mass and friction. Stream applies force.

### Future Level Ideas (Not Committed)
- Moving toilet (on a train, on a boat)
- Multiple toilets — pick the right one
- Dark room — toilet only visible in flashes
- Windy outdoor portaloo
- Boss battle: the unflushed toilet that fights back

---

## Power-Wash Mechanics

The stream exerts force on movable objects. This is a key differentiator from
a simple aim-and-score game.

- **Force:** Proportional to stream pressure (which links to bladder volume)
- **Objects:** Have mass and friction properties defined per-level
- **Interaction:** Stream pushes objects along surfaces. Heavier objects need
  more sustained pressure. Light objects fly off easily.
- **Examples:** Toilet paper rolls, rubber ducks, soap bars, mystery stains
- **Goal:** Clear the bowl area, then score normally

---

## Art Direction

- **Tone:** Silly, cartoonish, irreverent. Think Worms or Untitled Goose Game,
  not realistic gore.
- **Style:** Simple 2D sprites. Clean outlines. Bright colours for important
  elements (bowl = clearly visible, floor = clearly bad).
- **Belly:** The dominant visual. Round, shirt stretched, possibly with a
  beer-stained t-shirt. The belly IS the player avatar.
- **Toilet:** Exaggerated proportions for clarity. Bowl opening is the target
  zone and must read instantly.
- **Stream:** Visible arc, possibly with particle effects for splash on impact.
  Yellow (obviously). Maybe adjustable opacity for taste.
- **Floor:** Tiles or bathroom mat. Pee puddles accumulate as visual feedback
  for misses.

---

## Audio Direction

- **Stream SFX:** The sound of... well, you know. Pitch/volume linked to
  stream pressure.
- **Bowl hit:** Satisfying splash/tinkle sound
- **Floor hit:** Sad splat sound
- **Object hit:** Comic boing/thud depending on object
- **Background:** Ambient bathroom sounds (extractor fan hum, distant flush)
- **Level complete:** Triumphant jingle or disappointed trombone based on score
- **Menu music:** Something jaunty and daft

---

## Iteration Log

_Record design decisions and pivots here as they happen._

| Date | Decision | Notes |
|------|----------|-------|
| — | Project started | Initial design doc created |
