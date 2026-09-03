---
name: web-design-guidelines
description: Production-grade web interface engineering checklist (Vercel Web Interface Guidelines). Enforces the mechanical rules that separate a demo from a shipped product - 16px mobile inputs to stop iOS Safari zoom, 44px touch targets, no `transition: all`, never disabling submit before input, never blocking paste, visible `:focus-visible` rings, WAI-ARIA keyboard flows, `tabular-nums` for comparable numbers, `prefers-reduced-motion`. Trigger before writing or reviewing any web UI component, form, modal, animation, or interactive element, and when the user asks for an accessibility, interaction, or frontend-quality pass. Pair with taste-skill (aesthetic direction) and 21st-dev-components (component sourcing).
---

# Web Interface Guidelines

The mechanical quality bar for shipped web UI. `taste-skill` decides how it should look; this decides whether it actually works. Apply while writing the component, not as a cleanup pass afterwards.

Source: [Vercel Web Interface Guidelines](https://vercel.com/design/guidelines) ([vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)).

## When this fires

- Writing or editing any interactive element: button, link, input, form, modal, drawer, menu, tooltip, toast, table, list.
- Adding any animation or transition.
- Any accessibility, interaction-quality, or frontend-review request.
- Reviewing a diff that touches web UI.

Not every rule applies to every component. Run the sections that match what is being built, and treat the **Non-negotiables** as always-on.

## Non-negotiables

These are the rules most often broken and most visibly wrong in production.

1. **Mobile input font size is at least 16px.** Anything smaller triggers iOS Safari auto-zoom on focus. (Alternative: viewport `maximum-scale=1`, but never disable zoom outright.)
2. **Touch targets: 24px minimum, 44px on mobile.** Expand the hit area rather than the visual box when the design calls for a small control.
3. **Never `transition: all`.** List the exact properties (`transition: opacity 150ms, transform 150ms`). `transition: all` animates properties added later by accident and forces unnecessary layout work.
4. **Never pre-disable submit.** Keep the submit button enabled until submission starts, so an incomplete form surfaces validation feedback instead of a dead button. Disable only during the in-flight request, with a spinner.
5. **Never block paste** in `<input>` or `<textarea>`. This includes password and one-time-code fields.
6. **Every focusable element has a visible, unobscured focus ring.** Use `:focus-visible`, not `:focus`. Never `outline: none` without a replacement.
7. **Links are `<a>`/`<Link>`, buttons are `<button>`.** Never a `<div>` with an onClick for navigation.
8. **Honor `prefers-reduced-motion`** with a real reduced variant, not just a disabled animation.

## Interaction

- All flows are keyboard-operable, following the WAI-ARIA Authoring Patterns.
- Manage focus deliberately: trap it in modals, return it to the trigger on close.
- Loading buttons keep their original label visible alongside the indicator.
- Loading states get a show-delay of ~150-300ms and a minimum visible time of ~300-500ms, to avoid flicker.
- Persist state in the URL so share, refresh, and Back/Forward work. Deep-link filters, tabs, pagination, and expanded panels. Audit every `useState` for whether it belongs in the URL.
- Optimistic updates for likely-successful actions, reconciled against the server response.
- Actions requiring further input end with an ellipsis: "Rename…", "Loading…", "Saving…". Use the `…` character, not three periods.
- Destructive actions need confirmation or an Undo with a safe window.
- `touch-action: manipulation` to prevent double-tap zoom on controls; set `-webkit-tap-highlight-color` to match the design.
- Tooltips delay on first appearance, then peers show without delay.
- `overscroll-behavior: contain` on modals and drawers.
- Restore scroll position on Back/Forward.
- Autofocus the single primary input on desktop; rarely on mobile.
- No dead zones: anything that looks interactive is interactive.
- While dragging, disable text selection and apply `inert`. Every drag, swipe, and pinch has a tap/click and keyboard alternative.
- Announce async updates with polite `aria-live` (toasts, inline validation).
- Internationalize keyboard shortcuts for non-QWERTY layouts.

## Forms

- Every control has a `<label>` or an associated accessible label, and clicking the label focuses the control.
- Checkboxes and radios share one generous hit target with their label.
- Enter submits when a text input is focused. In a textarea, Enter inserts a newline and Cmd/Ctrl+Enter submits.
- Never block typing, even in number-only fields. Accept the input, then show validation feedback.
- Errors render next to their field. On submit, focus the first error.
- Set `autocomplete` and a meaningful `name` so autofill works. Disable spellcheck for emails, codes, and usernames.
- Correct `type` and `inputmode` so mobile keyboards match the field.
- Placeholders signal emptiness and end with an ellipsis, or show an example value (`+1 (123) 456-7890`). A placeholder is never a substitute for a label.
- Warn before navigation when unsaved changes would be lost.
- Stay compatible with password managers and 2FA; allow pasting one-time codes. Use `autocomplete="off"` or a specific token on non-auth fields so password managers do not fire.
- Trim input values to survive text replacement and expansion.
- Explicitly set `background-color` and `color` on `<select>` to avoid the Windows dark-mode rendering bug.

## Animation

- Prefer CSS, then the Web Animations API, then a JS library.
- Animate compositor-friendly properties (`transform`, `opacity`). Avoid `width`, `height`, `top`, `left`.
- Animate only to clarify cause and effect or to add intentional delight.
- Choose easing that fits what is changing; anchor `transform-origin` where the motion physically starts.
- Animations are interruptible and cancelable by user input.
- Input-driven, not autoplaying, except muted non-essential loops.
- For SVG, apply transforms to a `<g>` wrapper with `transform-box: fill-box` for cross-browser consistency.

## Layout

- Optical alignment beats geometric alignment; adjust by 1px when perception says so.
- Every element aligns intentionally. No accidental positioning.
- Balance weight, size, and spacing when text and icons sit together in a lockup.
- Verify on mobile, laptop, and ultra-wide (zoom out to 50%).
- Respect safe areas with the `env(safe-area-inset-*)` variables.
- Render only useful scrollbars; fix the overflow rather than hiding it.
- Let the browser size things with flex, grid, and intrinsic sizing rather than measuring in JS.

## Content and accessibility

- Semantics before ARIA. Reach for a native element before an `aria-*` attribute.
- Hierarchical `<h1>`-`<h6>` plus a "Skip to content" link.
- Icon-only buttons get a descriptive `aria-label`. Icons that carry meaning also carry text.
- Decorative elements are hidden from the accessibility tree; verify names in the tree, not just in the markup.
- `<title>` reflects the current context.
- Never rely on color alone for status. Add a text label or shape.
- `font-variant-numeric: tabular-nums` for numbers meant to be compared or that update in place.
- Curly typographic quotes, the `…` character, `&nbsp;` for glued terms (`10&nbsp;MB`).
- Avoid widows and orphans; tidy the rag.
- Skeletons mirror the final content exactly so nothing shifts.
- Every screen has a next step or a recovery path. Design the empty, sparse, dense, and error states.
- Layouts survive short, average, and very long user-generated content.
- `scroll-margin-top` on headings that can be linked to, so anchors clear the sticky header.
- Locale-aware dates, times, numbers, delimiters, and currencies. Detect from `Accept-Language` and `navigator.languages` rather than location.
- `translate="no"` on brand names and code that must not be machine-translated.
- Caption speech, provide transcripts, describe essential visuals.

## Visual detail

- Layered shadows: at least two layers, mimicking ambient plus direct light.
- Combine borders with shadows; semi-transparent borders read more cleanly across backgrounds.
- Nested radii are concentric: child radius is less than or equal to parent radius.
- On a non-neutral background, tint borders, shadows, and text toward the same hue.
- Interactive states increase contrast: `:hover`, `:active`, and `:focus` are all more contrasted than rest.
- Prefer APCA over WCAG 2 for perceptual contrast judgment; keep WCAG AA as the floor.
- Color-blind-friendly chart palettes.
- Set `<meta name="theme-color">` and `color-scheme` on `<html>` so browser UI matches the page.
- Animate a wrapper rather than the text node itself to avoid anti-aliasing shifts.
- Avoid gradient banding by using a background image instead of a CSS mask fade.

## Performance

- Budget `POST`/`PATCH`/`DELETE` round trips under 500ms.
- Prefer uncontrolled inputs; keep controlled input loops cheap.
- Virtualize large lists, or use `content-visibility: auto`.
- Preload only above-the-fold images; lazy-load the rest. Set explicit image dimensions so images never cause CLS.
- `<link rel="preconnect">` for asset and CDN origins. Preload and subset fonts (`unicode-range`) for critical text.
- Move long tasks off the main thread; batch DOM reads and writes to avoid reflow thrash.
- Prefer `<video autoplay muted loop playsinline>` over animated GIF. Add an H.264 MP4 source in `<picture>` for short loops in Safari.
- Profile with CPU and network throttling, extensions disabled, and check iOS Low Power Mode and macOS Safari. Track and minimize re-renders.

## Review mode

When reviewing rather than writing, report findings as `file:line` plus the rule violated and the concrete fix. Lead with the Non-negotiables, then keyboard and focus, then forms, then motion, then everything else. Do not report rules the code has no occasion to violate.
