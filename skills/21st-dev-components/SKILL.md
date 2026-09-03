---
name: 21st-dev-components
description: Source React + Tailwind + shadcn/ui components and marketing blocks (hero sections, animated backgrounds, pricing tables, footers, shaders/gradients) from the 21st.dev catalog instead of hand-writing them, then own and adapt the code to the project's tokens. Trigger when a UI need matches a known component pattern, when the user says "21st에서 찾아줘", "컴포넌트 가져와", "히어로 섹션 만들어줘", or when a React/Tailwind project with `components.json` needs a new UI block. Pair with taste-skill (aesthetic direction) and web-design-guidelines (quality bar the pasted code must pass).
---

# 21st.dev Components

[21st.dev](https://21st.dev/) is a community catalog of React components, marketing blocks, templates, shadcn themes, shaders, and gradients built by design engineers. Everything is delivered as **source code you own**, following shadcn/ui conventions - not a runtime dependency.

Use it to skip rebuilding solved patterns, then adapt the code to the project. Component sourcing only: `taste-skill` decides the aesthetic direction, `web-design-guidelines` is the bar the resulting code must clear.

## When this applies

- **Applies:** React (or Next.js) project using Tailwind CSS, ideally with shadcn/ui already set up (`components.json` present). The need matches a known pattern: hero, pricing table, feature grid, testimonial wall, nav, footer, animated background, AI chat, card gallery, auth widget.
- **Does not apply:** non-React stacks, projects on a different design system (Material, Fluent, Carbon), or a component so project-specific that adapting a catalog item costs more than writing it. Say so and write it directly.

## Rules

1. **Search before hand-writing.** In a Tailwind + shadcn project, check the catalog before building a common pattern from scratch. A close match adapted is usually faster and better than a fresh build.
2. **Reuse project primitives first.** If the project already has a `Button`, `Card`, or `Dialog`, use them. Never install a catalog item that duplicates an existing primitive, and never end up with two parallel lookalike components.
3. **Never add a runtime dependency for a component.** The code is copied into the repo under `components/ui/`. Verify any npm packages the item pulls in against `package.json` and report what was added.
4. **Never ship a catalog component in its default state.** Adapt radii, colors, spacing, typography, and icon family to the project tokens before considering it done. Prefer existing design tokens over new arbitrary values. A page assembled from unmodified catalog blocks looks exactly like every other page assembled from them, which is the AI-slop failure `taste-skill` exists to prevent.
5. **One system per project.** Do not mix 21st/shadcn components into a Material or Carbon tree.
6. **Read what you install.** Catalog code is third-party source. Read it before wiring it in, and check it against `web-design-guidelines` - focus rings, 44px touch targets, 16px mobile inputs, no `transition: all`, `prefers-reduced-motion` on animated backgrounds. Fix violations in the copied code; that is now the project's code.
7. **State the source.** Report which catalog item was used and what was changed, so a reviewer can trace it.

## How to add a component

Preferred, when the `21st` CLI is available:

```bash
npx @21st-dev/cli search "pricing table" --limit 10   # metadata search is free
npx @21st-dev/cli get <id>                            # print the component's code + demo
npx @21st-dev/cli add <user>/<slug>                   # writes components/ui/<slug>.tsx, installs deps
```

`21st add` runs shadcn under the hood. For a public item, stock shadcn works with no CLI or account:

```bash
npx shadcn@latest add "https://21st.dev/r/<user>/<slug>"
```

If neither is available (no network, no shadcn setup), take the component page's source code, place it under the project's component directory by hand, and install its dependencies explicitly. Do not invent a slug or an ID - if the exact item is unknown, say so and either ask for the URL or write the component directly.

Retrieving component code and AI generation are metered per account; search and previews are free. Authentication is `npx @21st-dev/cli login`, or a `21st_sk_…` key from https://21st.dev/mcp passed as `--api-key` or `TWENTYFIRST_TOKEN`. There is also an MCP server (`npx @21st-dev/cli init --client claude`) - suggest it rather than configuring it unasked.

## Marketing blocks

The catalog's strongest category is marketing composition: animated heroes, shader and liquid/metal backgrounds, gradient meshes, logo walls, feature bentos, footers.

- **Match the motion budget.** An animated background is only appropriate at `MOTION_INTENSITY > 5` in `taste-skill` terms. A shader hero on a trust-first B2B page is wrong regardless of how good the shader is.
- **One statement effect per page.** A shader hero plus an animated gradient section plus a marquee is noise. Pick the one that carries the message.
- **Animated backgrounds are the most expensive thing on the page.** Check bundle size, keep them off the critical path, confirm they degrade to a static fill under `prefers-reduced-motion`, and verify they do not repaint on scroll or destroy mobile framerate.
- **Layout hierarchy still comes from `taste-skill`.** An imported hero block does not exempt the page from the hero rules - fits the viewport, max 2 headline lines, subtext under 20 words, one primary CTA.
- **Replace the demo content.** Catalog demos ship with placeholder copy, generic names, and stock logos. Every one of those is an AI tell if it survives to production.

## Checklist before calling it done

- [ ] Searched the catalog before hand-writing a common pattern?
- [ ] No duplicate of an existing project primitive introduced?
- [ ] New npm dependencies verified and reported?
- [ ] Component restyled to project tokens, not left in default state?
- [ ] Copied code read and passing `web-design-guidelines` non-negotiables?
- [ ] Animated backgrounds justified by the motion budget and reduced-motion safe?
- [ ] All demo copy, names, and logos replaced with real content?
- [ ] Source item named in the handoff?
