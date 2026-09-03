# AI Tells (forbidden patterns)

Signatures the model reaches for when it tries to "look designed". Hard bans unless the brief explicitly calls for one.

## Dashes (non-negotiable)

**Em-dash (`—`) is completely banned.** No "sparingly", no "fine in body copy". Banned in headlines, eyebrows, labels, pills, button text, body copy, quotes, attribution, captions, nav items, and alt text. En-dash (`–`) as a separator is banned too; ranges use a hyphen (`2018-2026`, `€40-80k`).

Permitted dash characters: the regular hyphen `-`, and the minus sign in math. One visible `—` or `–` fails pre-flight.

Restructure instead: two sentences with a period, a comma, parentheses, or a colon.

## Visual and CSS

- No neon or outer glows. Use inner borders or tinted shadows.
- No pure black `#000000`. Off-black, zinc-950, charcoal.
- No oversaturated accents, no gradient text on large headers.
- No custom mouse cursors.
- No crosshair or hairline grid lines drawn purely as decoration.
- No `border-t` **and** `border-b` on every row of a long list or spec table. Pick one, use it sparsely.
- No scoring/progress bars with filled background tracks as comparison visuals on a marketing page.

## Typography

- Inter as the automatic default. See SKILL.md typography rules.
- Oversized H1s used in place of real hierarchy.
- `<br>`-broken-and-italicized headlines as a default "design move".
- Vertical rotated text ("INDEX OF WORK, 2018 - 2026" at 90°) outside a genuinely experimental brief.
- Straight ASCII quotes. Use typographic quotes or none.

## Layout and spacing

- **Three identical feature cards in a row.** Use a 2-column zigzag, asymmetric grid, scroll-pinned section, or horizontal scroll instead.
- Centered hero over a dark mesh gradient.
- Glassmorphism applied to everything.
- Empty or filler cells in a bento grid.

## Content and data ("Jane Doe" effect)

- Generic names: "John Doe", "Sarah Chan". Use realistic, locale-appropriate names.
- Generic avatars: SVG eggs, user glyphs.
- Fake-perfect numbers: `99.99%`, `50%`, `1234567`. Prefer organic values.
- Startup-slop brand names: "Acme", "Nexus", "SmartFlow", "Cloudly".
- Filler verbs: "Elevate", "Seamless", "Unleash", "Next-Gen", "Revolutionize".

## Hero and top of page

- Version labels as eyebrows: `V0.6`, `BETA`, `EARLY ACCESS`, `INVITE-ONLY PREVIEW`, unless the brief is literally a launch.
- "Brand · No. 01" style sub-eyebrows.
- Div-based fake product UI (fake dashboard, fake terminal, fake task list) built from styled rectangles. This is the single most recognizable tell.
- Fake version footers inside fake screenshots (`v0.6.2-rc.1`, `last sync 4s ago · main`).
- Decoration text strips at the hero bottom: `BRAND. MOTION. SPATIAL.`, `TYPE / FORM / MOTION`, `DESIGN · BUILD · SHIP`.
- Trust logo walls stuffed inside the hero row. They belong in their own section below.

## Section labels and micro-meta

- Section-number eyebrows: `00 / INDEX`, `001 · Capabilities`, `06 · how it works`.
- `01 / 4` pagination stamps on images or bento tiles.
- Range labels as eyebrows: "Index of Work, 2018 - 2026".
- Micro-meta sentences under an eyebrow ("The list will stay short on purpose.").
- Poetic sidebar labels: "From the field", "Field notes", "Currently on the bench", "On our desks".
- Generic step labels: "Stage 1 / Stage 2", "Phase 01 / Phase 02". Use the verb itself ("Install", "Configure", "Ship").
- Floating top-right explainer paragraph in a section header.

## Separators and dots

- The middle dot `·` is rationed to at most one per metadata line. Not the default separator for everything.
- Decorative colored status dots before nav links, list rows, or badges. Only for real semantic state, sparingly.

## Images and captions

- Pills, tags, or labels overlaid on photos (`Plate · Brand`, `Field notes - journal`). Caption below the image instead, or nothing.
- Fake photo credits as decoration (`Field study no. 12 · Ines Caetano`, `Frame XII · 35mm`).
- Broken Unsplash links. Use generated assets or `picsum.photos/seed/...`.
- Hand-rolled decorative SVG illustrations as a substitute for real imagery.

## Marketing copy

- "Quietly in use at" / "Quietly trusted by". Use "Trusted by", "Used at", or no heading.
- Mock-humble industry asides ("We respect the French ones").
- Weather / locale / time strips (`LIS 14:23 · 18°C`, "Lisbon, working with founders") unless the brand is genuinely place- or timezone-defined.
- Version footers (`v1.4.2`, `Build 0048`) on marketing pages.
- Live-stock counters ("Reservation 412 of 800") without real data.
- Scroll cues: `Scroll`, `↓ scroll`, `Scroll to explore`, animated mouse-wheel icons.

## Components

- shadcn/ui shipped in its default state. Customize radii, color, shadow, and type to the project.
- Mixing icon families, or hand-drawn icon paths.
- Mixing two design systems in one tree.
