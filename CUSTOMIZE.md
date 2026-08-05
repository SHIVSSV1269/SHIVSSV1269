# Customize in 5 minutes

Every visual is a hand-written SVG in `assets/` — no build step, no dependencies, no
third-party generator. Open a file, edit text, save, push. Animations are plain CSS
keyframes plus SMIL, which GitHub renders fine inside `<img>` tags.

Open `preview.html` in a browser to watch all of them animate locally before you push.

## Palette (used everywhere)

| Token | Hex | Where |
|---|---|---|
| ink | `#0b1016` / `#0d1117` | backgrounds (matches GitHub dark) |
| gold | `#e3b873` | headings, trigrams, seal ring |
| bright gold | `#f6e3b4` | text shine gradient |
| jade | `#63d2a5` | energy, progress fills, accents |
| cinnabar | `#e2513f` | seal, storm heading, danger accents |
| ivory | `#f4efe4` | the yang half, body highlights |
| slate | `#6f8697` | secondary labels |

Search-and-replace a hex across `assets/*.svg` to re-skin the whole profile.

## What to edit where

**`assets/banner.svg`** — the hero.
- Your name: the two `SHIVSSV1269` `<text>` lines (one draws the stroke, one fades in
  the gold fill — change both).
- Tagline: the line inside `clip-path="url(#typeClip)"`. If you change its length,
  adjust the caret's `values="62;532;532;62"` and the `type` keyframe `width` so the
  cursor stops where your text ends.
- Motto: the `THE WAY FOLLOWS NATURE` line. The red seal holds a miniature yin-yang;
  swap in your initials as `<text>` if you'd rather sign it.

**`assets/realms.svg`** — skills as cultivation realms.
Each `<!-- ROW n -->` block has four numbers to keep in sync:
- `<animate ... to="365">` — bar width in px. The track is **380px** wide, so
  `width = percent × 3.8`.
- the orb's `<animate attributeName="cx" ... to="745">` — that's `380 + width`.
- the number in `<text ...>96</text>` at the right.
Realm ladder, lowest to highest: Breath Gathering → Foundation Establishment →
Core Formation → Nascent Soul → Spirit Severing → Void Refinement → Integration →
Great Ascension. Gold rows read as "beyond mortal", jade rows sit below that.

**`assets/tribulation.svg`** — the "currently working on" list.
Four `<text>` lines in the `class="mo"` group. Keep them short; the lightning owns the
right half of the canvas.

**`assets/trigrams.svg`** — your stack, one technology per trigram.
Eight blocks, each named in a comment (`<!-- Heaven -->`). Change the technology label
in `<text y="52">`; the small gray word above it is the trigram's name. The three
`<path>` lines inside are the trigram itself: a full `M-13 -8 H13` is an unbroken
(yang) line, a split pair is a broken (yin) line. Reordering is just swapping labels —
the ring keeps spinning either way.

**`assets/yin-yang.svg`**, **`assets/divider.svg`** — reusable ornaments, no text.

**`README.md`** — the layout. The stats cards under *The Mountain Retreat* come from
third-party services (`github-readme-stats`, `streak-stats`); delete that block if you
want the profile to depend on nothing but this repo. Update the *Fellow Travelers*
badges with your real links.

## Notes

- Everything is English; no fonts are downloaded, so the art renders identically
  everywhere.
- Every file honours `prefers-reduced-motion` and freezes gracefully.
- No contribution snake. Deliberately.
