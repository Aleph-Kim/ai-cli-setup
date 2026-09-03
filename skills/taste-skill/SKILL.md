---
name: taste-skill
description: Anti-slop design direction for landing pages, portfolios, marketing sites, and redesigns. Forces a deliberate design read (audience, vibe, aesthetic family) and overrides the LLM default look - AI-purple gradients, centered hero, three equal feature cards, Inter + slate, em-dashes, "Acme"/"Jane Doe" filler. Covers typography, color, spacing, motion depth, dark-mode integrity, and layout hierarchy. Trigger before writing any landing/marketing/portfolio UI, when the user asks for a page that should "not look AI-made", or on any visual redesign. Pair with web-design-guidelines (engineering/a11y checklist) and hyperui (HTML + Tailwind markup conventions).
---

# Taste Skill

Make the interface look like a person with taste designed it, not like a template. This skill governs **aesthetic direction**; the mechanical interaction/accessibility checklist lives in `web-design-guidelines`, and HTML + Tailwind markup conventions live in `hyperui`. Run all three on a real page.

Adapted from [tasteskill](https://www.tasteskill.dev/) by Leonxlnx ([github.com/Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), MIT).

## Scope

**Applies to:** landing pages (SaaS, consumer, agency, event), portfolios, marketing/about pages, editorial pages, visual redesigns.

**Does not apply to:** dashboards, dense admin UI, data tables, multi-step wizards, code editors, native mobile. If the brief is one of those, say so, point at the right foundation (Fluent / Carbon / Atlassian / Polaris / TanStack Table), and apply only the parts of this skill that touch marketing surfaces.

## Step 1 - Design read (before any code)

Read the brief for: page kind, vibe words the user actually used, reference URLs or products named, audience, existing brand assets, and hard constraints (accessibility-first, public sector, regulated, kids). Constraints override aesthetics.

Then state one line before generating:

> Reading this as: `<page kind>` for `<audience>`, with a `<vibe>` language, leaning toward `<design system or aesthetic family>`.

If the read genuinely diverges, ask **exactly one** clarifying question. If it can be inferred, do not ask.

## Step 2 - Set the three dials

| Dial | Range | Baseline |
|---|---|---|
| `DESIGN_VARIANCE` | 1 symmetric ... 10 asymmetric | 8 |
| `MOTION_INTENSITY` | 1 static ... 10 cinematic | 6 |
| `VISUAL_DENSITY` | 1 airy ... 10 packed | 4 |

Infer from the read: minimalist/Linear-style `5-6 / 3-4 / 2-3`, premium consumer `7-8 / 5-7 / 3-4`, agency/experimental `9-10 / 8-10 / 3-4`, trust-first/public-sector `3-4 / 2-3 / 4-5`. State the values and the reason; do not silently ship the baseline.

Dials gate the rest:
- `DESIGN_VARIANCE` 1-3 symmetric grid, 4-7 offsets and mixed aspect ratios, 8-10 masonry, fractional grid columns, large empty zones. Levels 4+ MUST collapse to a strict single column below 768px.
- `MOTION_INTENSITY` 1-3 hover/active only, 4-7 CSS transitions and delay cascades on `transform`/`opacity`, 8-10 scroll-driven choreography.
- `VISUAL_DENSITY` 1-3 `py-32`-`py-48` sections, 4-7 `py-16`-`py-24`, 8-10 tight padding, hairline separators instead of cards, mono numerals.

## Step 3 - Pick the foundation honestly

If the brief maps to a real design system, install the official package instead of recreating its CSS: Fluent (`@fluentui/react-components`), Material 3 (`@material/web`), Carbon (`@carbon/react`), Polaris (Shopify admin), Atlaskit, Primer, `govuk-frontend`, `uswds`, Bootstrap 5.3, `@radix-ui/themes`, shadcn/ui, or Tailwind v4 utilities for indie builds.

**One system per project.** Never mix Material with shadcn/ui, or Fluent with Carbon, in the same tree.

If the brief is an aesthetic rather than a system (glassmorphism, bento, brutalism, editorial, aurora, kinetic type), build it with native CSS + Tailwind and label it honestly as an approximation. There is no official `liquid-glass.css`.

**Verify dependencies before importing.** Check `package.json`; if the package is missing, output the install command first.

## Core rules

### Typography
- Display default `text-4xl md:text-6xl tracking-tighter leading-none`. Body default `text-base leading-relaxed max-w-[65ch]`.
- **Inter is discouraged as the default.** Prefer Geist, Outfit, Cabinet Grotesk, Satoshi, or a brand-appropriate face. Inter is fine when the user asks for neutral/Linear-style, or the brief is public-sector.
- **Serif is very discouraged as a default.** "Creative brief" is not a reason. Reach for serif only when the brand names one, or the family is genuinely editorial/luxury/heritage and the choice can be justified. `Fraunces` and `Instrument_Serif` are banned as defaults.
- Emphasize a word inside a headline with **italic or bold of the same family**. Never inject a serif word into a sans headline.
- Italic display words containing `y g j p q` need `leading-[1.1]` minimum plus `pb-1` reserve, or the descender clips.
- Control hierarchy with weight and color, not raw scale. No screaming H1s, no gradient text on large headers.

### Color
- Max one accent color, saturation under 80% by default. Neutral base (Zinc / Slate / Stone) plus one high-contrast accent.
- **No AI-purple.** No automatic violet button glows, neon outer glows, or random mesh gradients, unless the brand asks for them.
- **Color consistency lock:** the accent chosen for the page is used on the whole page. No blue CTA appearing in section 7 of a warm-grey site.
- **Premium-consumer palette ban:** for cookware / wellness / artisan / luxury / DTC-home briefs, do not default to warm cream backgrounds (`#f5f1ea`, `#faf7f1`, `#efeae0` family) + brass/clay/oxblood accents (`#b08947`, `#b6553a`, `#9a2436` family) + espresso near-black text. Rotate instead: cold luxury (silver/chrome/smoke), forest (deep green + bone + amber), black and tan, cobalt + cream, terracotta + slate, or monochrome + one saturated pop.
- No pure `#000000` or `#ffffff`. Off-black and off-white keep depth.
- One palette per project. Do not drift between warm and cool greys.

### Layout hierarchy
- **Anti-center bias:** when `DESIGN_VARIANCE > 4`, avoid the centered hero. Use split screen, left content / right asset, asymmetric whitespace, or scroll-pinned structure. Centered is fine for editorial or manifesto briefs.
- **Hero fits the initial viewport:** headline max 2 lines, subtext max 20 words and 4 lines, CTAs visible without scrolling. Hero top padding max `pt-24` at desktop. A 4-line hero headline is a font-size error, not a copy-length error.
- **Hero stack max 4 text elements:** (eyebrow OR brand strip OR neither), headline, subtext, CTAs (1 primary + max 1 secondary). Trust strips, pricing teasers, feature bullets, and taglines under the CTA move to their own section below.
- **Eyebrow restraint:** max 1 small uppercase tracking label per 3 sections, hero counts as one. Usually just drop it; the headline is enough.
- **Section-layout-repetition ban:** each layout family appears at most once. Eight sections need at least four different families. Max 2 consecutive image+text split (zigzag) sections; the third is a failure.
- **Split-header ban:** no "left big headline + small explainer paragraph floating right" as a section header. Stack them vertically at `max-w-[65ch]`.
- **Bento grids:** exactly as many cells as there is content for, no blank filler tile, and 2-3 cells carry real visual variation (image, pattern, tinted background), not six white text cards.
- Navigation renders on one line at desktop, height 64-72px, 80px cap.
- Use `min-h-[100dvh]`, never `h-screen`. Use CSS Grid, not flexbox percentage math. Contain pages with `max-w-7xl mx-auto` or `max-w-[1400px]`.
- Declare the sub-768px collapse explicitly per multi-column section.

### Materiality and states
- Cards only when elevation communicates real hierarchy; otherwise group with `border-t`, `divide-y`, or negative space.
- **Shape consistency lock:** one corner-radius system per page (all-sharp, all-soft 12-16px, or all-pill), or a documented rule followed everywhere.
- Tint shadows toward the background hue. No pure-black drop shadows on light backgrounds.
- Ship the full state cycle: skeletal loaders shaped like the final content (not spinners), composed empty states, inline errors.
- `:active` gets tactile feedback (`-translate-y-[1px]` or `scale-[0.98]`).
- Every CTA passes WCAG AA against its own background (4.5:1 body, 3:1 for 18px+). Ghost buttons over photos need a scrim or stroke.
- CTA labels fit one line at desktop, 3 words max for primary CTAs. **One label per intent** across the whole page - "Get in touch" and "Let's talk" on the same page is a failure.
- Labels above inputs, errors below, `gap-2`. Never placeholder-as-label.

### Motion and depth
- **Motion must be motivated.** Each animation communicates hierarchy, storytelling, feedback, or state transition. If the reason cannot be said in one sentence, drop it.
- **Motion claimed is motion shown.** `MOTION_INTENSITY > 4` means the page actually moves. If working motion cannot be shipped in scope, lower the dial to 3 and ship a clean static page.
- Animate only `transform` and `opacity`. Never `top`, `left`, `width`, `height`. `will-change` sparingly.
- `window.addEventListener("scroll", ...)`, `window.scrollY` in React state, and `requestAnimationFrame` loops touching state are **banned**. Use `useScroll()` / `useMotionValue` / `useTransform`, GSAP ScrollTrigger, IntersectionObserver, or CSS `animation-timeline: view()`.
- Spring physics (`type: "spring", stiffness: 100, damping: 20`) over linear easing. Not every card needs an infinite loop.
- Anything above `MOTION_INTENSITY 3` honors `prefers-reduced-motion`; infinite loops, parallax, and magnetic physics collapse to static.
- Grain/noise filters live only on `fixed inset-0 pointer-events-none` pseudo-elements, never on scrolling containers.
- `useEffect` animations have strict cleanup. Motion components are `'use client'` leaves.
- Max one marquee per page. Use z-index only for real layer contexts (sticky nav, modal, overlay, grain), never sprayed `z-50`.

### Dark mode integrity
- **Dual mode by default.** Never ship light-only or dark-only without explicit instruction. Respect `prefers-color-scheme`.
- Pick one token strategy per project: Tailwind `dark:` variants, or CSS variables (`--surface`, `--text-primary`, `--accent`) swapped under `[data-theme="dark"]`.
- **Hierarchy parity:** what pops in light pops in dark. Brand color stays recognizable, not desaturated into the background. WCAG AA minimum for body, AAA target for hero copy.
- **Page theme lock:** the page has one theme. No warm-paper section sandwiched between dark sections. Section-level tints within the same family (`bg-zinc-950` beside `bg-zinc-900`) are fine.
- Set the theme once at the page/layout root; individual sections never override it.
- Open the page in both modes before calling it done.

### Content and assets
- Per section: headline under 8 words, sub-paragraph under 25 words, plus one asset or one CTA.
- Lists over 5 items need a different component (2-column grouping, card grid, tabs, scroll-snap pills, carousel, marquee), not a longer `<ul>` with a hairline under every row.
- Quotes max 3 lines, attribution is name + role, never name only.
- **Copy self-audit before shipping:** re-read every visible string. Rewrite anything grammatically broken, with unclear referents, or performatively poetic. Plain functional copy beats cute AI copy.
- Invented precise numbers (`92%`, `5.8 mm`) are banned unless real or explicitly marked as mock.
- Real images: generated assets first, then `https://picsum.photos/seed/{descriptive-seed}/{w}/{h}`. Never build a fake product screenshot out of styled `<div>`s.
- Icons from `@phosphor-icons/react`, `hugeicons-react`, `@radix-ui/react-icons`, or `@tabler/icons-react`, one family per project, standardized `strokeWidth`. Never hand-roll icon SVG paths. Emoji discouraged in UI text.

## Redesign mode

If files already exist, audit before touching anything: inventory the current palette, type, spacing, components, and what the brand clearly owns. Preserve brand identity, working information architecture, and content. Modernize in priority order (spacing and rhythm, then type scale, then color calibration, then motion, then layout family). Never silently change logo, brand colors, product naming, or legal copy.

## Before shipping

Read `references/ai-tells.md` and confirm nothing on the page matches it. Then run `references/preflight.md` box by box. A single failed box means the page is not done.

The one absolute: **zero em-dashes (`—`) and zero en-dashes (`–`) anywhere visible** - headlines, eyebrows, pills, body, quotes, attribution, captions, button labels, alt text. Use a regular hyphen or restructure the sentence. This is the single most-violated tell.
