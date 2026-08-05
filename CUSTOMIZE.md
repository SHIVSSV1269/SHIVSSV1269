# 修改指南 · Customize in 5 minutes

Every visual is a hand-written SVG in `assets/` — no build step, no dependencies, no
third-party generator. Open a file, edit text, save, push. Animations are plain CSS
keyframes + SMIL, which GitHub renders fine inside `<img>` tags.

Open `preview.html` in a browser to see all of them animating locally before you push.

## Palette (used everywhere)

| Token | Hex | Where |
|---|---|---|
| ink | `#0b1016` / `#0d1117` | backgrounds (matches GitHub dark) |
| gold | `#e3b873` | headings, trigrams, seal ring |
| bright gold | `#f6e3b4` | text shine gradient |
| jade | `#63d2a5` | qi, progress fills, accents |
| cinnabar | `#e2513f` | seals, 天劫, danger accents |
| ivory | `#f4efe4` | yang half, body highlights |
| slate | `#6f8697` | secondary labels |

Search-and-replace a hex across `assets/*.svg` to re-skin the whole profile.

## What to edit where

**`assets/banner.svg`** — the hero.
- Your name: the two `SHIVSSV1269` `<text>` lines (one is the stroke-draw, one is the
  gold fill — change both).
- Tagline: the line under `clip-path="url(#typeClip)"`. If you change its length,
  adjust the caret's `values="62;532;532;62"` and the `type` keyframe `width` so the
  cursor stops at the end of your text.
- The four-character motto `道法自然` ("the Dao follows nature") and the seal glyph `道`.

**`assets/realms.svg`** — skills as cultivation realms.
Each `<!-- ROW n -->` block has four numbers to keep in sync:
- `<animate ... to="365">` — bar width in px. Bar track is **380px** wide, so
  `width = percent × 3.8`.
- the orb's `<animate attributeName="cx" ... to="745">` — that's `380 + width`.
- the `<text ...>96</text>` at the right.
Realm ladder, low to high: 炼气 Qi Condensation → 筑基 Foundation → 金丹 Core Formation →
元婴 Nascent Soul → 化神 Deity Transformation → 炼虚 Void Refinement → 合体 Integration →
大乘 Mahayana → 渡劫 Tribulation. Gold rows read as "higher than mortal", jade rows below.

**`assets/tribulation.svg`** — the "currently working on" list.
Four `<text>` lines in the `class="mo"` group. Keep them short; the lightning owns the
right half of the canvas.

**`assets/bagua-stack.svg`** — your stack, one tech per trigram.
Eight blocks, each labelled with a comment (`<!-- ☰ Python -->`). Change the label
`<text y="52">`. The three `<path>` lines inside are the trigram itself: a full
`M-13 -8 H13` is a solid (yang) line, a split pair is a broken (yin) line. Reordering
techs is just swapping the label text — the ring keeps spinning either way.

**`README.md`** — the layout. The stats cards in 洞府 come from third-party services
(`github-readme-stats`, `streak-stats`); delete that block if you want the profile to
depend on nothing but this repo. Update the 道友 badge links to your real profiles.

## Notes

- Chinese glyphs render with the viewer's system font (`Noto Serif SC`, `Songti SC`,
  `SimSun`, …). Nearly every OS ships one; nothing is downloaded.
- Every file honours `prefers-reduced-motion` and freezes gracefully.
- No contribution-snake. Deliberately.
