# Pre-flight check

Run every box before delivering. Not optional. A single failed box means the page is not done.

## Direction

- [ ] Design read declared in one line (page kind, audience, vibe, aesthetic family)?
- [ ] Dial values stated and reasoned from the brief, not silently left at baseline?
- [ ] Design system chosen from the official list, or the aesthetic labeled honestly as an approximation?
- [ ] One design system only, no Material + shadcn mixing?
- [ ] Redesign mode detected and audit performed, if files already existed?
- [ ] Every third-party import verified against `package.json`, install commands emitted for anything missing?

## Typography and color

- [ ] **Zero em-dashes (`—`) and zero en-dashes (`–`) anywhere visible.** Headlines, eyebrows, pills, body, quotes, attribution, captions, buttons, alt text.
- [ ] If a serif is used, it is justified by brand or genuinely editorial context, and it is not `Fraunces` or `Instrument_Serif`?
- [ ] Every italic display word containing `y g j p q` has `leading-[1.1]` minimum plus `pb-1` reserve?
- [ ] One accent color used identically across every section?
- [ ] Premium-consumer brief does not default to the beige + brass + oxblood + espresso palette?
- [ ] No pure `#000000` or `#ffffff`?
- [ ] Typographic quotes, not straight ASCII quotes?

## Layout

- [ ] Hero fits the viewport: headline max 2 lines, subtext max 20 words and 4 lines, CTA visible without scrolling?
- [ ] Hero top padding max `pt-24` at desktop?
- [ ] Hero has at most 4 text elements, no tagline under the CTAs, no trust strip inside the hero?
- [ ] Eyebrow count is at most `ceil(sectionCount / 3)`, hero included? (Count `uppercase tracking` micro-labels mechanically.)
- [ ] No split-header pattern (big headline left, small explainer paragraph floating right)?
- [ ] No three or more consecutive image+text split sections?
- [ ] At least four distinct layout families across eight sections?
- [ ] Bento grid has exactly N cells for N items, no filler tile, and 2-3 cells carry real visual variation?
- [ ] "Trusted by" logo wall sits under the hero, with real logo marks rather than plain text wordmarks?
- [ ] Navigation renders on one line at desktop, height 80px or less?
- [ ] Mobile collapse declared explicitly for every high-variance multi-column layout?
- [ ] `min-h-[100dvh]` used instead of `h-screen`?
- [ ] One corner-radius system applied consistently?

## Interaction and states

- [ ] Every CTA passes WCAG AA against its own background, ghost buttons over photos have a scrim or stroke?
- [ ] No CTA label wraps to a second line at desktop?
- [ ] No two CTAs share the same intent under different labels?
- [ ] Form inputs, placeholders, focus rings, labels, and error text all pass WCAG AA against the section background?
- [ ] Empty, loading, and error states provided, with skeletons shaped like the final content?
- [ ] Cards omitted wherever spacing or a divider would do the job?

## Motion

- [ ] Every animation justified in one sentence (hierarchy, storytelling, feedback, or state transition)?
- [ ] If `MOTION_INTENSITY > 4`, the page actually animates?
- [ ] Only `transform` and `opacity` animated?
- [ ] No `window.addEventListener('scroll')`, no `window.scrollY` in state, no rAF loop touching state?
- [ ] Everything above `MOTION_INTENSITY 3` wrapped for `prefers-reduced-motion`?
- [ ] `useEffect` animations have cleanup, motion isolated in `'use client'` leaves?
- [ ] At most one marquee on the page, z-index reserved for real layer contexts?

## Dark mode

- [ ] Both modes defined and actually opened during development?
- [ ] Hierarchy parity holds: what pops in light pops in dark?
- [ ] Page theme lock holds, no section flips to the opposite mode mid-scroll?
- [ ] Theme set once at the root, not overridden per section?

## Content and assets

- [ ] Copy self-audit done: every visible string re-read, nothing broken, cute-but-wrong, or performative shipped?
- [ ] No invented precise numbers presented as real specs?
- [ ] Quotes at most 3 lines, attribution is name plus role?
- [ ] Lists over 5 items use a real component, not a longer `<ul>` with hairlines under every row?
- [ ] Real images used, no div-based fake screenshots, no hand-rolled decorative SVG?
- [ ] Icons from one allowed family with a standardized stroke width?
- [ ] Nothing on the page matches `ai-tells.md`?

## Performance

- [ ] LCP under 2.5s (hero image prioritized or preloaded), INP under 200ms, CLS under 0.1?
- [ ] Grain/noise only on `fixed inset-0 pointer-events-none` layers?
- [ ] Heavy libraries lazy-loaded below the fold?
