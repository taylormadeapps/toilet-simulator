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
  feet/shoes at the edges, and the toilet above.
- **Belly:** Large semi-ellipse at the bottom of the screen. The widest point
  sits on the screen edge, so only the top half is visible — a proper
  semicircle. The belly IS the character — it frames the viewport.
- **Moobs:** Two fleshy mounds at the top of the belly with underboob shadows,
  nipples, and scattered chest hair. Looking down past them at the toilet.
- **Genitals:** Not visible. The stream appears from beneath the belly.
  This keeps it silly rather than crude.
- **Movement:** The player character is stationary (standing at the toilet).
  What moves is the stream aim direction, controlled by pointer input.

---

## Core Mechanic — The Stream

The pee stream is the central game mechanic. Everything revolves around
controlling it.

### Stream Properties
- **Origin:** Fixed point above the belly (top-centre of belly sprite)
- **Direction:** Fires upward toward the toilet. Aimed at mouse X position.
- **Arc:** Gravity creates a natural arc — particles fly up, peak, fall back
- **Spread:** Slight random spread to simulate realism and add challenge
- **Pressure:** Controlled by mouse Y position (see Mouse-Y Pressure below).
  Pressure affects particle speed/reach. Bladder does NOT affect pressure —
  it is purely a timer.

### Mouse-Y Pressure Control
- **Mouse up (toward toilet):** Full pressure. Stream fires strong, arcs high,
  reaches the bowl.
- **Mouse mid-screen:** Half pressure. Stream just reaches the bowl rim.
- **Mouse down (toward belly):** Weak/no stream. Push right down = stops.
- **Push back up:** Stream resumes. Intuitive push-to-pee mechanic.
- **Bladder depletion:** Only drains while stream is actively flowing.
  Depletion rate scales with mouse pressure — gentle push = slow drain.

### Stream Interaction
- **Bowl hit:** Registered when particles descend into the bowl ellipse
- **Floor hit:** Registered when particles fall past the bowl without entering
- **Centre hit:** Bonus for landing in the inner 40% of the bowl
- **Object hit:** Applies force to movable objects (power-wash mechanic, future)
- **Collision model:** Particles fly freely on the way up. Only scored when
  descending (vy > 0). This lets the stream arc naturally through the bowl
  zone without premature kills.

---

## Bladder System

The bladder meter is the level timer. You don't control when the level ends —
your bladder does.

- **Volume:** Starts full at level begin, depletes as you pee
- **Depletion rate:** Proportional to mouse pressure. Pushing harder drains
  faster. Pulling back pauses drainage entirely.
- **Pressure independence:** Bladder volume does NOT affect stream pressure.
  A full bladder and a nearly-empty bladder produce the same stream at the
  same mouse position. Bladder is purely a timer.
- **Display:** Vertical meter on HUD (like a health bar but for piss)
- **Level end:** When bladder hits zero AND all remaining particles have
  landed/despawned, the results screen appears.
- **Urgency:** No urgency mechanic initially. The stream just flows until empty.

---

## Scoring

**Active model: Penalty**

### Penalty Model (Active)
- Start at 1000 points
- Lose 5 points per floor hit
- Gain 1 point per centre-zone hit (inner 40% of bowl)
- +200 clean finish bonus if zero floor hits
- Minimum score is 0 (cannot go negative)

### Results Screen
- Shows: final score, accuracy %, bowl hits, floor hits, centre hits
- Clean finish bonus displayed if earned
- Click or SPACE returns to splash screen

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
| 2026-02-25 | Penalty scoring model adopted | Start 1000, -5 floor, +1 centre, +200 clean |
| 2026-02-25 | Mouse-Y pressure control | Mouse position drives stream, not bladder volume |
| 2026-02-25 | Layout flipped | Belly at bottom (semi-ellipse), toilet at top |
| 2026-02-25 | iPhone portrait resolution | 390×844 (9:19.5 aspect ratio) |
| 2026-02-25 | Moobs added | Hairy chest/moobs on the belly for character |
| 2026-02-25 | Descending-only collision | Particles scored only when falling back down |
