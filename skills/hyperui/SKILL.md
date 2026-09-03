---
name: hyperui
description: Build UI as plain HTML5 + Tailwind CSS utility classes in the HyperUI (hyperui.dev) style - no React, no JSX, no component library. Covers marketing sections (hero, feature, CTA, stats, banner), form controls and inputs, navigation, cards, and tables as modular copy-paste markup, using semantic elements like `<details>`/`<summary>` for interaction so JavaScript stays optional. Trigger before writing any HTML, template-engine markup (Blade, ERB, Twig, Jinja, Handlebars, Go templates), or Tailwind-styled front-end component, and when the user asks for a HyperUI pattern, a "pure HTML" component, or markup for a non-React stack. Pair with taste-skill (aesthetic direction) and web-design-guidelines (interaction/a11y quality bar).
---

# HyperUI Components

[HyperUI](https://www.hyperui.dev/) is a collection of free, copy-paste UI built as **plain HTML with Tailwind CSS utility classes**. No runtime, no React, no component library - the markup is the deliverable. Use its patterns as the default shape for hand-written UI on any stack that renders HTML.

This skill governs **markup and Tailwind conventions**. `taste-skill` decides the aesthetic direction; `web-design-guidelines` is the interaction/accessibility bar the markup must clear. Run all three on a real page.

## When this applies

- **Applies:** any output that is ultimately HTML - static `.html`, a server-rendered template (Blade, ERB, Twig, Jinja/Django, Handlebars, Go `html/template`, Astro/Svelte markup), an email, a CMS block - styled with Tailwind CSS. The need matches a common pattern: hero, feature grid, CTA, stats band, announcement banner, navbar, form/input group, card, table, pagination, accordion/FAQ, dropdown.
- **Does not apply:** a React/Vue/Svelte-component codebase that already has its own design-system components (reuse those), or a project on a non-Tailwind system (Bootstrap, Bulma, plain CSS). Match the existing stack instead of importing HyperUI conventions.

## Rules

### 1. Standard HTML5, never React/JSX

- Attribute is `class`, never `className`. Also `for` (not `htmlFor`), `tabindex`, `maxlength`, `readonly`, `autocomplete` - all lowercase HTML spelling.
- Void elements are written unclosed HTML-style: `<br>`, `<hr>`, `<img ...>`, `<input ...>`, `<meta ...>` - no `/` before `>`, no self-closing non-void tags like `<div />`.
- No `{expression}` interpolation, no `on:click` / `onClick`, no component tags (`<Button>`, `<Card>`). Dynamic values use the target template engine's own syntax (`{{ }}`, `<%= %>`, `@{{ }}`, `{% %>`) - never JSX braces.
- Inline event handlers and `<script>` are a last resort. Reach for semantic HTML first (rule 3).

### 2. HyperUI markup patterns (modular structure)

Compose a page from self-contained blocks, each a single outer element with a scoped class list:

- **Marketing sections** - `hero`, `feature`, `cta`, `stats`, `banner`: wrap in `<section>`, constrain with a centered container (`mx-auto max-w-screen-xl px-4 py-16 sm:px-6 lg:px-8`), one `<h1>`/`<h2>` per section, one primary CTA.
- **Forms** - group each field as `<label>` + control + optional help/error text; use `<fieldset>`/`<legend>` for radio/checkbox sets; wire errors with `aria-describedby`.
- **Navigation** - `<header>` > `<nav aria-label="...">`; mobile menu via `<details>` (rule 3), not a JS toggle.
- **Cards** - `<article>` or `<a>` wrapper; predictable slots: media, eyebrow, title, body, meta/footer.
- **Tables** - real `<table>` / `<thead>` / `<tbody>` / `<th scope="col">`; wrap in `<div class="overflow-x-auto">` for horizontal scroll on small screens.

### 3. Prefer semantic HTML over JavaScript

- Accordion / FAQ / "show more" / disclosure: `<details>` + `<summary>`.
- Dropdown / mobile nav / filter panel: `<details>` with the trigger as `<summary>` and the panel as a positioned sibling, or a CSS-only `group`/`peer` pattern.
- Modal-like flows: native `<dialog>` where a small amount of JS is acceptable; otherwise a `:target` pattern.
- Only add JS when the interaction genuinely cannot be expressed semantically (e.g. focus trapping, async validation). Say so when you do.

### 4. Tailwind class conventions

- **Order classes by role** so lists stay scannable: Layout (`flex`, `grid`, `block`, position, `w-`, `h-`) -> Spacing (`m-`, `p-`, `gap-`) -> Typography (`text-`, `font-`, `leading-`, `tracking-`) -> Visual (`bg-`, `border`, `rounded-`, `shadow-`) -> State/variant (`hover:`, `focus-visible:`, `active:`, `disabled:`, `sm:`, `md:`, `lg:`) last.
- **Mobile-first responsive:** unprefixed = smallest; layer `sm:` / `md:` / `lg:` up. Don't write `lg:`-only components with no base style.
- **Explicit interaction states:** every interactive element declares `hover:`, `focus-visible:` (visible ring - `focus-visible:outline-none focus-visible:ring`), and `active:` where it makes sense; `disabled:` styles must pair with an actual `disabled` attribute.
- Prefer theme tokens (`text-gray-700`, `rounded-lg`) over arbitrary values (`text-[#374151]`, `rounded-[7px]`) unless the design system defines them.

### 5. Accessibility (non-negotiable)

- Every decorative/icon `<svg>` gets `aria-hidden="true"` and `focusable="false"`. An icon that is the only content of a control needs an adjacent `<span class="sr-only">` label or `aria-label` on the control.
- Provide an `.sr-only` utility (or Tailwind's `sr-only`) and use it for visually-hidden labels, "skip to content" links, and table caption context.
- Inputs are paired with a `<label for>`; placeholder is never the label. Group related controls with `<fieldset>`/`<legend>`.
- Landmark elements (`<header>`, `<nav>`, `<main>`, `<footer>`) once per page; multiple `<nav>` get distinguishing `aria-label`s.
- Interactive elements are real `<button>` / `<a href>` - never a `<div onclick>`. `<a>` without a real destination is a `<button>`.
- Color contrast >= 4.5:1 for text; state is never signalled by color alone.

## Checklist before calling it done

- [ ] Zero `className`, JSX braces, self-closing non-void tags, or component tags - it is valid HTML5?
- [ ] Page composed from modular `<section>`/`<article>`/`<nav>` blocks, one heading per section?
- [ ] Interaction done with `<details>`/`<summary>`/`<dialog>`/`:target` before any JS?
- [ ] Class lists ordered Layout -> Spacing -> Typography -> Visual -> State?
- [ ] Mobile-first base styles present, `sm:`/`md:`/`lg:` layered on top?
- [ ] `hover:` + visible `focus-visible:` ring + `active:` on every interactive element?
- [ ] Every icon `<svg>` has `aria-hidden="true"`; icon-only controls have an `sr-only` label?
- [ ] Every input has a real `<label for>`; radio/checkbox groups in a `<fieldset>`?
- [ ] Tables use real table markup inside an `overflow-x-auto` wrapper?
- [ ] Ran `taste-skill` (look) and `web-design-guidelines` (mechanics) on the result?
