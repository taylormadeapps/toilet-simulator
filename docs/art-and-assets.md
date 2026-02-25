# Toilet Simulator — Art & Assets

How assets are organised, named, formatted, and loaded. Placeholder art is
welcome — missing gameplay is not.

---

## Directory Structure

```
assets/
├── sprites/
│   ├── player/          # Belly, feet, shirt variations
│   ├── toilet/          # Bowl, rim, base, lid variations
│   ├── stream/          # Stream particles, splash effects
│   ├── objects/         # Movable objects (rubber duck, toilet roll, etc.)
│   ├── floor/           # Tile textures, puddle overlays
│   └── ui/              # HUD elements, buttons, icons
├── audio/
│   ├── sfx/             # Sound effects (splash, splat, boing, flush)
│   └── music/           # Background music, menu music, jingles
├── fonts/               # Game fonts (TTF/OTF)
└── maps/                # Level config files (JSON or Python dicts)
```

---

## Naming Conventions

### Sprites
Pattern: `entity_variant_frame.png`

Examples:
- `belly_default_idle.png`
- `toilet_standard.png`
- `toilet_thimble.png`
- `stream_particle_01.png`
- `splash_bowl_01.png`
- `splash_floor_01.png`
- `puddle_small.png`
- `puddle_large.png`
- `object_rubberduck.png`
- `object_toiletroll.png`
- `floor_tile_white.png`

### Audio
Pattern: `category_description.ext`

Examples:
- `sfx_stream_loop.wav`
- `sfx_splash_bowl.wav`
- `sfx_splat_floor.wav`
- `sfx_object_hit.wav`
- `sfx_flush.wav`
- `music_menu.ogg`
- `music_gameplay.ogg`
- `jingle_level_complete.ogg`
- `jingle_level_fail.ogg`

---

## Format Standards

### Images
- **Format:** PNG (transparency required for all sprites)
- **Transparency:** Alpha channel, not colour-key transparency
- **Resolution:** Design at native target resolution. Define in `settings.py`.
  Do not scale at load time unless explicitly needed.
- **Colour space:** sRGB

### Audio
- **SFX:** WAV (44.1kHz, 16-bit). WAV for zero-latency playback.
- **Music:** OGG Vorbis. Smaller file size, Pygame decodes on the fly.
- **Sample rate:** 44100 Hz for all audio
- **Channels:** Mono for SFX (spatial mixing later if needed). Stereo for music.

### Fonts
- **Format:** TTF or OTF
- **Licensing:** Only use fonts with licences that allow game distribution.
  Record licence in `assets/fonts/LICENCES.txt`.

---

## Placeholder Policy

Placeholder art is valid and expected during development.

- **Sprites:** Coloured rectangles with text labels are fine. A green rect
  labelled "BOWL" is a perfectly good toilet until real art exists.
- **Audio:** Silent stubs or simple beeps are fine. A `print("SFX: splash")`
  is acceptable until real audio is integrated.
- **Fonts:** System default font (`pygame.font.SysFont`) is fine for dev.

**The rule:** Missing gameplay is a bug. Missing art is a task on the backlog.
Never let art block a playable build.

---

## Asset Loading

All assets are loaded during scene initialisation, never during the game loop.

```python
# Pattern: load once, use many times
class AssetManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self._cache: dict[str, pygame.Surface] = {}

    def load_image(self, relative_path: str) -> pygame.Surface:
        if relative_path not in self._cache:
            full_path = self.base_path / relative_path
            self._cache[relative_path] = pygame.image.load(
                str(full_path)
            ).convert_alpha()
        return self._cache[relative_path]
```

- **Images:** Always `.convert_alpha()` after loading.
- **Fonts:** Create `pygame.font.Font` at init, store in cache.
- **Audio:** Load with `pygame.mixer.Sound` at init. Music loaded with
  `pygame.mixer.music.load` at scene transition.

---

## Attribution

If any third-party assets are used (free sprites, CC-licensed audio, etc.),
record them in `assets/ATTRIBUTION.md` with:

- Asset name and file path
- Source URL
- Author/creator
- Licence type
- Any conditions (attribution required, no derivatives, etc.)
