# Skill Authoring — structure, taxonomy, confidentiality, editing rules

Load triggers: writing or substantially changing any skill file, setup work and new skills included; generalising an open-source observation's Principle (confidentiality layers); classifying a skill or observation as open-source or internal; propagating a cross-cutting principle; the upstream check for a third-party project; a skill target that resolves but may not be able to run; designing a routing or behavioural eval, or reading a verification result for a skill change

Load this before creating any skill or making substantial changes to one.

## Contents

- Taxonomy in full
- The Pre-Flight Principle
- Lean Content (including progressive disclosure — the default — and
  reference-file shape by trigger count)
- Configuration vs process — the three-container rule
- Documenting an external tool surface
- The description
- Confidentiality layers
- Timelessness — shared skills must not capture current state
- Editing skills — always start from the live file
- Declaring a block's scope mechanically
- Verifying relocations and restructures
- Trial design — measuring whether a behaviour fires unprompted
- New skills
- Runtime prerequisites — declare what the skill needs to be able to run
- Retiring skills — harvest before you retire
- Principle Propagation
- Reference-file ceilings — the growth barrier

## Taxonomy in full

**Open-source skills** are client-agnostic and methodology-driven.
Recognise one: the methodology works across clients and contexts; no
proprietary information is needed; other practitioners would find it
valuable; it captures a process, not personal preferences. Required
elements: tool-agnostic language (capabilities like "browser access", not
product names) and built-in enforcement (see Pre-Flight Principle).
Default to open-source when a skill could go either way — strip specifics
and generalise.

**Internal skills** contain user/client/project specifics, personal
preferences, or context only the user has. They identify themselves as
internal, need no attribution or licence, and can be shorter and less
formal. They're working documents — keep them current, don't over-engineer.

## The Pre-Flight Principle

Rules documented in a skill are not reliably followed during creative flow.
Every skill with explicit rules needs a verification step where the agent
re-reads the rules and checks its output against them before delivery. When
creating or improving any skill ask: "Does it have rules? Does it have a
mechanism to enforce them?" If not, add one.

**Embedded commands are pre-flight items too — execute before you ship.**
A prose rule is re-interpreted in context on every run, so ambiguity can
be caught at execution time; an embedded command runs verbatim,
unattended, forever, and a subtly wrong one reads as correct on every
re-read (`git log -1 --format=%cI --reverse` returns the NEWEST commit,
because `-1` applies before `--reverse`). Execute every command embedded
in a skill once against real data, inspect its output for plausibility,
and only then save the skill file: an unverified snippet ships bugs that
no re-read can catch.

**Run the literal string, from a clean shell.** Running something
*equivalent* verifies your paraphrase, not the artefact: copy the command
out of the skill file and execute that exact text from a separately
spawned shell, because a working session accumulates environment
variables, interpreter flags, security-policy overrides, PATH entries and
a working directory the eventual reader will not have. Where two shells
are available, pre-flight in the one NOT used for setup. **When the
command under test is a guard, assert on the mechanism, not the
outcome:** with several guards over one operation, "it was rejected" is
satisfied by any of them, so match the error text or exit code to the
guard under test, choose inputs clearly past the threshold, and test the
boundary value separately. **Confirm a dry-run path exists before
pre-flighting anything with side effects**; where none exists, add one
first — a test of a guard rail must not become the incident the guard
rail exists to prevent.

**A verification command that AGREES with you is the one to distrust.**
A check that contradicts a strong prior gets investigated; one that
confirms it never does, so a right answer from a wrong instrument teaches
you to trust the instrument. The usual form is an aggregated count,
because a count is not a listing and a tool that collapses output for
readability under-reports without saying so: `git status --porcelain
--ignored` prints one line for an ignored DIRECTORY, so a `grep -c` over
it reports "1" where five files are ignored, and only
`--untracked-files=all` expands it. Before shipping a verification step
that reports a number, confirm what the number's unit is, and enumerate
and read the set whenever enumeration is cheap.

**A list of sources is an embedded command too.** The rule governs
anything the skill instructs a future session to *use* unchecked — a
URL, an API endpoint, a database name, a file path, a tool invocation —
not only shell snippets. It is worse than a broken command, which fails
loudly: an unreachable source returns *something* — an empty result set,
a login page, a shell — and the natural reading of an empty result is
"nothing matched", so the skill teaches a future session to report
absence where there was only a blocked door. Execute every source once,
against real data, before the skill file is saved; record which ones were
tried and what they returned.

**A verification that cannot come out negative is not a verification.**
Before shipping any check, ask what it would look like if the thing being
checked had failed — and if the answer is "the same", the check is
decoration. The characteristic shape: the artefact being inspected was
produced or touched by the same session doing the inspection. What
distinguishes arrival from non-arrival is a **discriminator** — a value
only the far side can produce: a server-assigned identifier, an upstream
timestamp, a digest computed remotely, a field the local copy has no way
to fabricate. Hash-matching a published artefact against your own source
is not one, because both sides are yours. Name the discriminator when
writing the check, and if you cannot name one, say the step is unverified
rather than writing a check that always passes.

## Lean Content

A skill should contain only content that changes the agent's behaviour at
execution time. Move changelogs, credits beyond the author block, long
backstories, and maintainer notes to supporting docs. Do NOT cut examples,
anti-patterns, or worked scenarios — bare rules get violated more than
rules with context. Two tests per passage: would removing it change
behaviour, and does the agent already know it? A passage that explains
what a competent agent does unprompted (what a diff is, how YAML nests)
is trimmed; the skill carries only what is specific to its method. Keep
per-session rules in the skill body and episodic material in reference
files loaded on demand (progressive disclosure) — a skill loaded every
session is fixed overhead and should be audited like one.

**Declare your own core ceiling, and let it only fall.** A skill opts into
the size ratchet by naming its own bound — `core_max_lines: N` in SKILL.md
frontmatter, or a `.core-ceiling` file beside it — seeded at whatever the
core measures today: the point is not that every skill reaches some ideal
size, it is that no skill silently grows past where it already is.
`validate-skill-bundle.py` then fails when the core exceeds it, with the
instruction to move content to a reference file rather than raise the
number. **The ceiling follows trims down:** the validator also fails when
the declared ceiling sits more than 3 lines above the core's count, and
the fix is to lower `core_max_lines` (or `.core-ceiling`) to the current
count in the same commit as the trim — a check that only blocks growth
leaves each trim as open headroom that the next ordinary additions spend
without anyone deciding to. Every run reports `core N / ceiling M / slack S`.

A skill that declares neither has not opted in. The count and the distance to
the 500-line target are still reported; nothing is gated. That is deliberate. **A tool one skill ships for the whole library must not carry
that skill's own constants.** Any threshold in a shared script is either read
from the subject being checked or is advisory — the tell is a gate that fails
on input its author never looked at.

**Progressive disclosure is the DEFAULT, not an option.** Loading happens
in three levels: frontmatter metadata is always in context, the SKILL.md
body loads whenever the skill triggers, and bundled resources load only
when something reads them. The body is therefore a per-invocation tax and
the reference files are not, so content belongs in the body only if it
changes behaviour every time the skill fires. **The split is the target
structure for every NEW or SUBSTANTIALLY REVISED skill, whatever its
size** — episodic material goes to `references/` from the first draft,
not once the body has grown too big to read, because a structure rule
that switches on a line count gives one skill two shapes. The ~500-line
figure survives in one role only: as the **retrofit trigger** for an
existing, not-yet-split skill — a body past roughly 500 lines is the
point at which retrofitting stops being optional. Concretely:

- **SKILL.md keeps** the mental model, the small number of rules that
  change behaviour on every invocation, and a pointer list to the
  reference files.
- **`references/` takes** tool inventories, recipes, taxonomies,
  per-variant detail and long gotcha catalogues — anything consulted
  during one kind of episode rather than on every trigger.
- **Each reference file gets a table of contents** once it passes roughly
  300 lines, so a reader can load it and jump rather than read it whole.
- **Every pointer states its load trigger explicitly** — "read before the
  first export", "read when choosing a tool", "read when a review
  triggers" — because a pointer without a trigger reads as optional and
  gets skipped. An unconditioned list of filenames is not progressive
  disclosure, it is a bibliography.
- **References stay one level deep.** A reference file points back to
  the core, not onward to another reference — a load that depends on a
  second load is the one that gets skipped — so a rule two episodes need
  is routed through the core's pointer list. Declared exception, not an
  escape clause: this skill's references cite `weekly-review.md` directly,
  because the review procedure is the one episode every other reference
  serves and the core's pointer to it is already mandatory.

Splitting also creates the edit seams a monolith lacks. Retrofitting
existing large skills is a separate, lower-priority job — the default
binds immediately for new work and for any revision substantial enough
that the body is being rewritten anyway.

**A reference file is shaped by its TRIGGERS, not its line count.** The
core is loaded in full every session, so a line there taxes every
consumer; a reference file loads only when its episode fires, so a long
file that loads rarely is cheap and the core's ceiling does not transfer.
The rule: a reference file serves one episode, or a set of episodes that
reliably co-occur. Splitting is indicated when the count of distinct load
triggers into one file grows, whatever its size — each trigger pays for
every other episode's content — and a long single-episode file is
correctly shaped and must not be split to satisfy a size rule. The
measurement for any bundle — lines and declared load triggers per file —
is the `reference shape` line the validator prints on every run; read it
there, never from a copy in prose, which is stale by the next round. On
this skill's own bundle the largest file carries few triggers and a
smaller one carries the most, which is the point.

A line ceiling flags the largest file first — the one that needs no
change, since a review loads it whole — and cannot tell it from the file
that twenty separate moments in a session each pull in. So
`scripts/validate-skill-bundle.py` prints the per-file trigger count on
every run, and gates growth only for a skill that opts in with per-file
ceilings ("Reference-file ceilings — the growth barrier", below): there
the declared count picks the remedy for a file that outgrows its ceiling,
split above 8 triggers, trim or a reasoned raise at 8 or fewer. A split
needs a load-observation test per moved episode (below), and never two
structural splits in one test period — a regression could not be
attributed to either.

**The load trigger is a new failure point the monolith did not have.** A
split delivers its saving only if the reference file is actually fetched
when its episode fires. When it isn't, the agent improvises the episode
from the lean core, behaviour degrades, and nothing errors — the content
is all still there, so no check on the content can catch it. So the trial
criteria for any split must test the LOADING, not just the content split:

1. Every pointer is an instruction carrying its trigger ("load X when Y"),
   not a description of what X contains.
2. During the trial, each episode is observed firing in a real session and
   the reference load confirmed — one criterion per episode, so an episode
   that never fired is visibly unproven rather than assumed fine.
3. A missed load is a blocking finding, not a note. The fix is structural
   enforcement — a checklist step the episode cannot complete without —
   rather than firmer wording, per this file's own pre-flight principle.

Add a runtime backstop: instruct the agent to log an observation whenever
it notices an episode was handled without its reference loaded, or the
negative case has no recording channel and the trial cannot distinguish
"not yet observed" from "not happening" (Trial design, below).

## Configuration vs process — the three-container rule

A skill that needs values specific to one person, team or installation —
an identity, an account name, a private blocklist, a set of local
exclusions — needs **three containers, not two**: in the skill the
specifics block publication and generalisation; in the prompt they keep
it fat and drifting. The third container resolves the tension:

1. **The skill** holds the process, and *reads* configuration.
2. **A private config file** holds the specifics. The skill names its
   expected location and never ships it.
3. **The invoking prompt** holds only the trigger.

State the precedence explicitly: config wins for *configuration*, the
skill wins for *process*, and config can never relax a rule. Give the
skill a first-run fallback that asks for the values and offers to write
the file when none exists — those few lines are what make the skill
usable by someone who is not its author. The test for whether a line
belongs in config rather than in the skill: **would a different person
running this skill need a different value here?** The extraction is
smaller than it looks — most identifying lines are a proper name where a
role noun ("the maintainer") reads identically.

**When a prompt or config duplicates a skill's rules for safety, replace
the copy with a stop condition, not a shorter copy.** Duplication
defended as insurance is the least audited kind — the argument for
copying it is also an argument against questioning the copy, so the
copies carrying the most important rules are the ones most likely to be
silently stale. A copy of a rule can drift out of agreement with its
source; a refusal to proceed without the source cannot. "If the skill did
not load, stop and report — do not proceed from this prompt" is one line
and has nothing to drift. Keep at most the irreversible invariants stated
in both places, and say in the prompt that it deliberately carries no
fallback copy, so a future editor does not helpfully re-add one.

## Documenting an external tool surface

Applies to any skill that documents a surface someone else owns — an MCP
server's tools, an API's endpoints, a platform's interface. Its value is
that its claims were OBSERVED rather than inferred from the vendor's own
descriptions, and the first version is almost always written after
exercising only part of the surface. Documenting the untested majority in
the same voice as the tested minority promotes vendor copy into apparent
field findings, and a later reader cannot tell which claims carry
evidence; dropping the untested items isn't the fix either — they still
need listing so the agent knows they exist.

1. **Mark every item, not just the exceptions.** Give each documented
   tool, endpoint or screen a visible per-item marker for verified-in-
   practice versus unexercised, and state the key near the top of the
   inventory. Marking only the unexercised ones fails: an unmarked item
   reads as absence of information rather than as evidence.
2. **Write unexercised items in a different voice.** What the vendor says,
   plus what can be safely inferred about risk — "the docs describe X";
   "assume this evicts current state" — never as observed behaviour. No
   worked examples, no timing or quota claims, no gotchas for something
   nobody has run.
3. **Make the marker a work queue.** Instruct the agent that when an
   unexercised item is used, it reports back what it actually did so the
   entry can be rewritten and its marker promoted; otherwise the markers
   ossify into a permanent disclaimer and the skill never converges.
4. **Promote on revision.** Any substantial edit to the skill re-checks
   the markers against what has been exercised since — promotion is part
   of the edit, not a separate project.
5. **Name each MCP tool in the `Server:tool` form** (`Analytics:report`),
   never bare: two servers can expose a `search`, and the qualified form
   is the one a reader can resolve to a tool list.

Principle: documentation that covers less but says which claims are tested
is more useful than documentation that blends the two, because the
reader's decision — trust it, or verify first — depends entirely on that
distinction, and it is unrecoverable once blurred.

## The description

**The description is written in the third person** — what the skill does
and when to load it ("Audits X whenever Y is mentioned"), never addressed
to "you": it sits beside every other installed description in the
system prompt, where a second-person sentence reads as an instruction.

**A description is routed among its neighbours, so it is only testable
against them.** Score it with the other skills installed beside it, never
in isolation: a trigger prompt that borrows a noun another skill owns
measures the noun, and a description that reads well alone still loses
its prompts to the sibling that owns one of its words. Before fixing
anything, run the no-case control — re-measure with the new skill present
and its own prompts removed: if the neighbours' prompts still route
correctly the problem is confined to this skill; if not, the description
is over-broad and is narrowed first. A negative control must be
positively owned: a prompt asserted not to reach this skill proves
nothing unless its declared owner demonstrably scores on it — an owner
that matches nothing turns the assertion into two misses. Choose the
name on meaning, then measure it against the neighbours' prompts too: a
lexical router weights the name double, so a common verb in it
("improve", "check", "review") steals every prompt that uses the word in
its ordinary sense — a regression visible only in the other skills'
prompts, never in the skill's own.

**House naming: a noun-phrase kebab-case name consistent with the
collection; the gerund form is not used here.** The name matches its
directory (editing rule 5). An existing skill keeps its name: a
rename is a migration (editing rule 7) that breaks every surface that
rule enumerates, from the repository URL to companion cross-references.

## Confidentiality layers

The open-source/internal boundary is a confidentiality boundary; enforce it
in layers so any one catches what others miss:

1. **Observation-level stripping** — open-source observations carry a fully
   generalised Principle (covered in SKILL.md).
2. **Pre-creation review** — before drafting/regenerating an open-source
   skill, scan all source material for client names, URLs, domains,
   internal terminology, identifiably-specific structures; replace with
   generic equivalents first.
3. **Post-draft sweep** — a separate re-read focused only on leakage.
   Read the examples, usage strings, default arguments and fixtures
   **first** (layer 8 says why), then proper nouns besides the author,
   domains/URLs/project identifiers, vertical details that narrow the
   client, examples traceable to a real project.
4. **Structural principle** — when in doubt, remove. Slightly more generic
   beats slightly leaky.
5. **Cross-product re-identifiability sweep** — the final pass before any
   public release. Individually-sanitised examples can combine to identify
   a client (enumerated counts matching a public client list; specific
   numbers in a thin vertical; thinly-disguised placeholder names in the
   same vertical as a real client). List every example and its fields
   (vertical, geography, numbers, timing, counts); ask whether a reader
   with the author's public client list could map them; mitigate by
   blurring counts, widening verticals, using illustrative ranges, or
   consolidating into composites. Run this mechanically — the author is the
   least reliable judge because they know the ground truth.
6. **Recipient-perspective pass (client-shared artifacts)** — the layers
   above guard one direction only: other parties' information leaking IN.
   An artifact prepared FOR a specific recipient also leaks the author's
   own workspace OUT: references to internal working files (analysis
   workbook filenames, private docs) the recipient never received are
   both confusing and factual errors (e.g. describing them as
   "delivered"). Check: every referenced file, document, or source is
   either included in the share or actually in the recipient's
   possession; replace internal-artifact citations with a plain
   description of the analysis they came from. Test: "can the recipient
   open or verify every reference in this document?"
7. **Cross-skill reference scan (published skills)** — a skill written
   inside a personal library accumulates pointers into sibling skills
   ("see {other-skill}'s Hyperlink markers"); published, they dangle and
   leak the existence and naming of the author's internal tooling. A
   published skill must either work standalone or declare its dependency
   on a specific *published* open-source companion. Scan for references
   to other skills by name; each hit is (a) a declared published
   companion — keep, ideally with a repo link; (b) inlineable — pull the
   needed rule into the text; or (c) internal tooling — rephrase to
   capability language ("whatever presentation tooling the subagent
   runs"). Make it mechanical in any publishing workflow: grep the
   content against the list of installed-but-unpublished skill names.
   Every pointer in a published document must resolve in the reader's
   world, not the author's.

   Authoring-time corollary — sibling-sync and family notes. The family
   machinery legitimately writes sync notes into skill files so shared
   cores don't drift, and those notes are the expected shape of a
   violation of this layer: the sync rule and the standalone rule are
   each followed correctly and still jointly produce an unpublishable
   skill. When adding a sibling-sync or family note to an open-source
   skill that is published or a publication candidate, phrase the family
   reference in capability language from the start ("the sibling skills
   implementing this methodology for other platforms") or point
   generically at the private family registry — never name
   installed-but-unpublished skills, because the publishing workflow's
   standalone scan blocks those names and the only fix is rewording at
   the live skill. A maintenance mechanism that writes cross-references
   into an artefact respects the publication boundary of the artefact it
   writes into: internal registries can name internal things; public
   artefacts reference them by capability, not by name.

8. **Examples are synthetic by construction, not scrubbed afterwards** —
   examples, usage strings, default arguments, test fixtures and sample
   payloads are the highest-risk text in a skill and the least reviewed:
   an example is pasted from a working run precisely so that it works,
   so live data survives a scrub there more reliably than anywhere else.
   Write them synthetic at authoring time — a generic label and a round
   number in the shape the argument or payload actually takes, which
   still teaches the format. No term-based scan can back this layer up:
   a confidentiality scan matches names, domains and handles, and a
   **number** is not one of those, nor can it be keyed on a vertical or
   category noun without firing on nearly every file. A clean scan is
   therefore evidence about the listed terms only — the house rule that
   an empty result from an instrument that cannot see the object is not
   evidence of absence. So the sweep in layer 3 reads examples first,
   not last, and the pre-publication read includes a human pass over
   every example, usage string and fixture in the tree — the one check
   no script can do for the author. A selftest's constants and a
   scanner's own fixtures are examples in this sense: write them so the
   source does not carry the shape it scans for (a placeholder label
   where a real name would sit, a stock vertical), or the first self-scan
   reports the scanner, and a fixture borrowed from a real engagement
   passes every term scan while naming it.
9. **Justifications are failure shapes, and examples span verticals
   (skills published or queued for publication)** — a rule's
   justification is stated as a present-tense failure shape ("the failure
   shape: …"), never as the case it came from: no "observed once", no "in
   the case that produced this", no client complaint, no count from one
   project. Exempt: counts about the skill's own log and process
   (observations, reviews, skills, releases) — they trace to no engagement
   and are the evidence a rule exists for. Examples come from at least two unrelated verticals or from a
   neutral stock vertical, never from the vertical of the session that
   produced the rule. The failure shape this layer closes: a skill update
   written from an internal log carries the log's engagement narrative
   and its client's vertical into published text, and each example passes
   every term scan on its own while the set identifies the client. No
   script sees either class, so it is a named human read before the
   commit, over every section added since the last published tree.

## Timelessness — shared skills must not capture current state

Any skill leaving the author's own maintenance loop (published, or shared
with a client for ongoing use) has no update cadence — undated
present-tense claims become silently wrong, and an agent will act on
them. "A recommendation on how it should be is timeless; a capture of the
current state is not." Rules: (a) recommendations and rules — keep; (b)
dated historical facts ("in June 2026 the share was ~50%") — keep, they
stay true as history; (c) undated/present-tense current-state claims
("X is currently blocked", "the site now does Y") — replace with a check
instruction ("verify the current state of X before acting"). Sweep
pattern: grep for "currently", "right now", "as of", "now", and
present-tense state verbs near infrastructure nouns. (Internal client
dossiers are exempt: they live in a maintenance loop where current-state
capture is the point.)

**A superseded method is not kept as a dated `## History` section.**
State the current method undated and put the old shape, where a reader
may still meet it, in a collapsed `<details><summary>Old
patterns</summary>` block beneath it: a lookup, not a revision timeline.

**First-party observation dates: prefer verification-based phrasing in
published skills.** Rule (b) above — dated facts stay — holds for
third-party-published facts (vendor changelogs, API announcements,
calendar-date examples). It does NOT extend to dates that reveal when the
AUTHOR observed, verified or reviewed something ("as of April 2026", "a
June 2026 re-check"): in a published artefact those leak the internal
review cadence and read as staleness markers. Replace them with
verification-based phrasing — "at last verification", "a later re-check
found" — plus an explicit instruction for how to re-verify against the
live source; readers need to know how to re-check a claim, not when the
author last did. The same rule covers commit messages on published repos.

**The prohibition, stated by what it forbids: no dated first-party
verification claim in any public artefact, in ANY date format.** The
shapes are examples subordinate to that definition, never the definition:
`YYYY-MM-DD`, `DD/MM/YYYY`, `Mon YYYY`, `Month YYYY`, `QN YYYY`, the
bare-year "as of 2026", and the sentence-position forms "on <date>" and
"run on <date>". The list matters because a scan greps exactly the shapes
it was given, and a reviewer running the example has complied with the
rule as written. So make the check mechanical and auditable: any
publishing workflow scans public artefacts before committing — a scan,
not a reminder — with the pattern set in a script where it can be
extended in one place, and **the scan records WHICH patterns ran**; a
green result whose coverage is unstated is unauditable. A count produced
by an enumerated set of shapes is a **lower bound**, never a "corrected"
figure, and a check that has passed every run is evidence about the
check, not about the artefact — the instrument guard
(`observation-log.md`, "Every instrument gets the same guard") applies to
green results exactly as to empty ones. **One paired form is exempt
(maintainer decision):** a measured fact may carry "Last verified
YYYY-MM-DD · Re-test: `<one command>`" — the date plus a backticked
re-test command, together, because for a fact that drifts the age is the
useful part and the command keeps it from being a bare claim. Every other
dated first-party form stays forbidden, including the date without its
command; a publishing scan encodes the exemption as an exclusion in its
script, never as prose.

**The internal-document exemption assumes a maintenance loop that is only
prose.** Internal skills may legitimately name current state, on the
unstated assumption that someone re-checks it — but nothing fires when it
drifts, so "internal, therefore dated facts are fine" becomes "internal,
therefore permanently wrong". So an internal skill carries current state
only with a **named re-check**: what re-derives the value, and when.
"Version X (re-derive from `<command>` at each review)" is acceptable; a
bare number is not. Where no re-check exists, do not record the value —
record how to obtain it.

## Editing skills — always start from the live file

1. The live file is the authoritative source: in Claude Code,
   `~/.claude/skills/{skill}/SKILL.md`. **Resolve a symlinked entry
   first** (`cd` into it and `pwd -P`): where it points into the user's
   own repository, the repository file is what you edit and what the
   round commit records (`weekly-review.md`, "Applying changes"). A skill
   another party maintains, or one the harness provides (categories (b)
   and (c), `weekly-review.md` Step 2), is never edited in place, however
   writable the file is.
2. Always base edits on a fresh read of the live file — never a workspace
   copy, prior draft, or memory.
3. Before writing a file you prepared earlier in the session over the
   live one, diff it against the live file; if they differ, rebase your
   edits on the live version.
4. Before any cross-copy work (a second clone, a copy another tool loads),
   enumerate all copies of the artefact and establish freshness PER COPY
   from evidence — mtime, content probes, hashes, `git log` — never from
   role ("the repo", "the live version"); then pick the base explicitly.
5. **Validate before you commit.** Run `scripts/validate-skill-bundle.py
   <skill directory>` after the last edit of a round, and commit only once
   it passes. What it asserts: (1) every UNQUALIFIED `references/`,
   `scripts/`, `assets/` path in SKILL.md has its file — a path qualified
   with an owning skill name (`<skill-name>/references/<file>`) is a
   cross-reference, a file in the repository the skill operates on is
   cited repository-relative (`./scripts/<file>`), both exempt, and a path
   with a `<slot>` segment is matched as a glob; re-wording a genuine
   cross-reference until it no longer starts with the prefix is disguising
   it to satisfy a linter; (2) the folded `description` is at most 1024
   characters, with a soft warning above ~900 — tighten phrasing, never
   drop triggers; (3) `name` is kebab-case, matches the directory, and
   the frontmatter parses: a `description:` or `name:` value holding `: `
   or ` #`, or starting or ending with a YAML-special character, is
   double-quoted or reworded — an unquoted ` #` starts a comment and the
   value silently ends there, and "`name` missing" on a block that visibly
   has one is the signature of an unparseable block; (4) exactly one
   frontmatter block; (5) no edit residue outside code — a literal `\1`,
   merge-conflict markers, unresolved `{{slot}}` placeholders; (6) the
   skill's declared core and reference ceilings (Lean Content,
   "Reference-file ceilings") — fixed by trimming or lowering, never by
   skipping the validator. It also warns on every `$` followed by a digit
   in SKILL.md, which a loader passing skill arguments rewrites (write an
   awk field as `$ 2`). Before the commit, sweep the skill tree for build
   artefacts (`__pycache__/`, `*.pyc`, `.DS_Store`) left by in-session
   checks. **A recommended check carries three measured numbers.** When
   proposing an automated check or a new gate rule, run each candidate
   over the existing corpus first and record, per rule: (a) hits on
   today's corpus, (b) true defects among them, (c) the normalisation
   needed to remove the rest; a rule with an unmeasured false-positive
   rate is a proposal to make people ignore a test.
6. Match process rigour to the change: complex/open-source/uncertain design
   → use the skill-creator if available; internal skills with requirements
   already established in conversation → write directly, flagging
   substantial changes for review.
7. **Before a rewrite, enumerate the surfaces outside the skill directory
   that restate its rules.** A rule's home is a location; its reach is
   every artefact that paraphrases it, and those live in directories the
   owning skill cannot see, so a grep across the skill folder reports
   clean. The surfaces that matter execute independently of the skill:
   activation fragments in CLAUDE.md or its equivalent, hook messages,
   saved shortcuts and memory notes. Enumerate them, then either update
   each in the same round or replace the copy with a stop condition per
   "Configuration vs process" above — including the clause that says the
   omission is deliberate, or a later editor helpfully restores the
   summary. A stale copy never fails loudly: it runs, plausibly, doing
   the superseded thing, and the only witness is the user noticing an old
   behaviour reappear weeks after asking for it to stop; the source's
   rate of change predicts the drift, not the copy's age.

   **A rename is a migration, not an edit.** Where skills are hosted by an
   account or an app, a skill under a new name is a new skill, and a
   published one also loses its repository URL and install path. Before
   the rename, grep the old name across the `skill:` fields of the
   observation log (active and archive), `skill-families.md`, the
   cross-cutting principles, scheduled-task prompts and activation lines,
   sibling and companion paths (`../<old-name>/`), copied script headers
   and memory notes. Upload the renamed skill, verify that it loads,
   deactivate the old one in the same step, then update every surface the
   grep found. Deleting the old skill is the user's call.
8. **Inserting into an ordered structure is a splice, not a replacement.**
   String replacement edits text, but a list, a table, a `## Contents`
   index, a frontmatter block or a numbered sequence of steps is
   structure, and an anchor-relative insert is safe only if you know what
   is adjacent to the anchor — which `replace` gives no way to assert, and
   no validator, scan or review reads shape. So: parse to lines, locate the
   insertion point by a **structural predicate** (the last line matching
   `^- `, the last row before the blank, the key after which the new key sorts),
   splice, rejoin. Never anchor on the text of a neighbouring paragraph.
   Where a replacement is used anyway, assert the neighbour's shape first
   — that the line before the anchor is the last list item, that the blank
   you are about to add is not already there — and fail loudly if it
   differs. The repo-mode gate in `scripts/validate-skill-bundle.py`
   catches the list case after the fact; the predicate prevents it.

**Verifying an edit is a separate problem, and the loader works against
you.** Three things get conflated — the file on disk, the copy the loader
injected into this session, and what a fresh session would receive — and
they can all differ at once. Launching a subagent to simulate "a fresh
session" does not help: its context starts cold but its skills come from
the **same snapshot**, so it reports the same stale content with the
added authority of an independent-looking check. So: **verify an edit by
reading the file on disk**, never by asking the loaded skill what it says
and never by asking a subagent; and when the question is what a *future*
session will receive, only a genuinely new session answers it — the
installing session structurally cannot.

## Declaring a block's scope mechanically

A section of an instructions file, a skill, or a shared config often applies
to only some of the work done on a machine. Trusting the agent to notice
the irrelevance from context fails quietly, and in the direction that does
damage: advice written for one domain is applied confidently to another.
Instead, open the block with a **detectable condition** — something the
agent can check rather than infer:

> Applies ONLY when the project has a `package.json` with a `react`
> dependency. In every other project, ignore this section entirely.

**State the negative branch explicitly**, because it is the half that gets
left out: "Applies when X" leaves the agent to decide what happens
otherwise; "and in every other case ignore this entirely" is the sentence
that makes the block safe to carry. A condition with no stated negative is
a preference, not a scope. Prefer conditions the agent can test cheaply
and locally — a file's presence, a path segment, a declared dependency —
over ones needing judgement ("when working on frontend tasks").

## Verifying relocations and restructures

Two modes, and picking the wrong one is why a good move looks broken.
**Verbatim relocation** — the content moves unchanged — is verified line
by line, with the two-tier check below. **Merge or extraction** — several
overlapping sources are reconciled into one destination, wording is
rewritten, tool or client names are generalised into capability language
on the way — is verified section by section, because every moved line
legitimately fails an exact match and the line-grep tier reports total
loss on a perfect merge.

For a merge or extraction, replace the line-grep tier with a **mandatory
source-section → destination coverage table, one per mover**: every
heading of every source is accounted for as moved / merged-into /
left-in-companion / dropped-with-reason, alongside the content only one
source carried, the generic content deliberately left behind, and the
substitutions made. Keep the word-count sanity check per file — it is
cheap and catches wholesale omission. And **the mover of a split section
writes both destinations**: whoever moves material out of a skill also
writes that skill's remainder for the same sections, because
complementarity — nothing in both places, nothing fallen between them —
cannot be checked afterwards as cheaply as it can be produced, and two
authors guarantee the seam nobody owns. The coverage table is the
artefact a merge is admitted on; a diff is not.

For a verbatim relocation, "nothing was lost" is checkable mechanically —
but only with a two-tier check:

1. Enumerate every added/moved line via `diff` of the old base vs the new
   base.
2. Exact-match each non-empty line against the restructured file set:
   `grep -qF -- "$line" "$file"` — the `--` is required, because markdown
   lines starting with `-` are otherwise parsed as options, `grep` errors
   out, and the line is scored as missing (31 false losses beside 35 real
   ones in one run). The same applies to every embedded snippet that
   interpolates file content into an argument position.
3. For misses, substance-check via a distinctive mid-line substring before
   concluding loss — most misses are container artifacts (heading-level
   changes, list-to-prose adaptation, re-wrapped lines splitting a phrase
   across newlines), not real losses.
4. Word-count sanity check per file.
5. Normalise line endings before any of the above. A checkout made with
   `core.autocrlf=true`, or a download that kept LF beside a clone that
   rewrote to CRLF, makes `diff -rq` report every text file changed and
   `grep -qF` score every line as missing — while the two PNGs in the
   same bundle compare identical, which is the tell. Compare with
   `diff --strip-trailing-cr` (or `dos2unix` / `tr -d '\r'` into temp
   copies) and strip the `\r` from each `$line` before grepping; a
   verification whose only difference is the line terminator has found
   nothing.

**Cross-reference-dense monoliths: keep section numbers global, add a
map.** When the document being split is dense with internal
cross-references (§13.6, §8.3.3b …) that will span the new file set, do
NOT renumber per file — renumbering breaks every reference or forces a
risky rewrite pass. The verified pattern (a ~5k-line skill split into a
core + 8 reference files with zero content loss): keep the original
section numbers global across the whole file set; move content by
verbatim line-range extraction so nothing is retouched; add a "Section
map" table to the core resolving §N → file; give each reference file a
one-line header pointing back to the map — the identifier space is an
interface, kept stable with a resolution layer added. The map's load
triggers are phrased as mandatory ("read X before running Y"), and a
core-size overshoot past the ~500-line guideline is acceptable when the
overage is genuinely per-invocation principle content — record that
reasoning where the next editor will see it.

One tier alone either misses losses (substance-only) or cries wolf
(exact-only). **The checker is code too, and the least-tested code in the
pipeline** — written once, for one run, never exercised against a fixture.
Count record headers by matching per line (split, then anchor), not with a
`^`-anchored regex over whole-file text, whose multiline-flag semantics
vary by language and fail silently to "1". Before trusting any checker's
verdict, calibrate it: assert that it reproduces a KNOWN count on the
untouched original. A checker that fails calibration is a false alarm
today and a silent pass tomorrow. Additionally, inventory the original's enforcement
mechanisms (checkpoints, assertions, invariants, mandatory-write rules,
defaults) as an explicit checklist — compression preferentially destroys
enforcement machinery because it reads as redundancy — and sweep any "pure
restructuring" change for net-new behaviour, which hides well in a large
rewording diff.

**Build a relocation as a re-runnable derivation, not a one-off patch.** A
relocation verified against the base as it stood at build time is correct
only for that base: if a concurrent edit lands on the live file before
delivery, inside the very block being moved, laying the finished target
files over the new tip **silently reverts it, with no conflict reported**
— the relocation is a set of whole files, not a patch, so git has nothing
to conflict. So express it as something **re-derivable from whatever the
live base currently is** — a script, or a procedure precise enough to
re-run — and re-derive immediately before delivery. Where a manual patch
is the only option, diff the moved regions against the live tip at
delivery time and stop on any difference. The verification that matters
is the one against the state you are landing on, not the state you
started from.

## Trial design — measuring whether a behaviour fires unprompted

When a change is on trial and what's being measured is whether the agent
does something ORGANICALLY (loads a reference file because the work called
for it, applies a rule without being told), record the trial's trigger
condition somewhere the agent under test does not read — a maintainer note
or the review report, never a task file, CLAUDE.md, or a handoff prompt.
Add an explicit invalidation clause: any session whose priming text names
the trigger condition, or instructs the behaviour directly, is discarded
rather than counted either way. And instrument the negative case
deliberately — log "substantive work in scope, no organic load" as its own
data point. Principle: an instruction that names what is being measured is
an intervention, not a description; priming text and measurement apparatus
must live in separate channels, or the trial measures compliance with the
prompt. Corollary: null results need active recording, or the trial cannot
distinguish "not yet observed" from "not happening".

**A behavioural eval is measured against a control arm:** the same
fixture and the same prompt with no skill loaded. An expectation the
control also satisfies is marked as such, not counted as evidence. The
prompt withholds the skill's own judgement — if the skill's job is to
decide that something is a pattern, the prompt does not say it is one;
if its job is to decide that a fix should be durable, the prompt asks
only for the immediate fix — since a stated conclusion is reached by
every arm. At least one case argues against the skill (a deadline, a
sunk cost, an authority saying it is fine): a discipline measured only
when nothing pushes against it has not been measured. Record the null
results: an expectation with zero delta says where the skill is redundant.

**A verification measures the thing the change touched.** A routing
metric moves with the frontmatter `description` and the name, so it is
evidence for a description change and for nothing else. A body change is
demonstrated against the failure it was written for: the behavioural
case where a fixture is feasible, otherwise the reported failure
reproduced against the edited text, showing the step that now fires.
Where neither is possible, state the gap — the measurement not run, and
why — rather than tick a box that always passes; the tell is that the
agent can say why the number could not have moved.

**Before trusting a null from a comparison arm, name the path from the
trigger to the changed bytes:** which user turn, routed by what, loading
which file, reaching which line — written out, not assumed. A control
proves the instrument reads the baseline; only the trace proves the
treatment arm lies on the path the instrument exercises, and a flat
result from a file nobody opened carries the same number as a real
non-effect. Where mirrors of a file are hardlinked, diff the arms by
inode, not by path, or a one-line change shows as several files and a
zero-line change hides among them. An untraced null is unreported, not a null.

## New skills

**Building next to siblings: separate the inherited steps from the
necessary ones.** A new member of a family inherits its siblings' shape,
and consistency with the family is a legitimate design value — which is
precisely why the inherited-but-unnecessary step survives review: it does
not read as wrong; it reads as belonging, and the person who detects it
is the one who has to answer an inherited question, by which time it has
shipped. So, for each step copied from a sibling, state **what this
skill's output would lose if the step were removed**. A step whose answer
is "consistency" is inherited, not necessary — drop it, or demote it to
an optional branch.

**Before authoring a skill for a library, tool or project, check whether
the project already ships one.** Many projects carry their own agent
skill in-repo — commonly under `agent-skill/`, `.claude/skills/`,
`skills/`, or named in the README — and hand-authoring beside it
duplicates work, drifts from the maintainers' version and misses their
updates. One search of the upstream repository (those paths, plus "skill"
in the README and release notes) settles it — the one network use this
skill permits, and only once the user has asked for the skill. If an
official skill exists, install it and put only the local delta into a
companion, exactly as for any other upstream-maintained skill
(weekly-review.md, Step 2); if it does not, author, and consider offering
the result upstream. Where the skill-creator is used (editing rule 6),
pass the observation(s) as its brief.

**A new skill ships three evaluation scenarios, written before its
documentation and re-run after every substantial change:** a positive trigger (a
realistic prompt that must route to it), a negative trigger with its
declared owner (a prompt a named neighbour must win), and a behavioural
case with a control arm (Trial design, above) — written first, because a
description drafted to pass them is the narrower one.

**First decide whether the skill joins a family, and if it does, read the
siblings before drafting.** Intent → interview → draft is right for a
genuinely new skill and wrong for one joining an existing family (the
registry is `skill-observations/skill-families.md`; see
`observation-log.md`), because the family already contains most of the
answer, distributed unevenly across its members; drafting from the
current session's experience produces a third divergent member. The cost
is asymmetric and front-loaded — reading two siblings first is minutes;
reconciling three divergent skills afterwards means re-reading all of
them, deciding per rule whether each divergence is intentional, and
editing in three places, with the divergences hardest to spot precisely
because each skill reads as coherent on its own.

Read every sibling in full, draft against them, and produce a short
**reconciliation note** as part of the deliverable, not as optional
homework: (a) content taken from the siblings; (b) content the new skill
adds that the siblings should also get — logged as observations naming
those siblings, never silently absorbed; (c) sibling content deliberately
omitted, with the reason. The note is what converts a new family member
from a source of drift into a correction of it. Then update the registry
with the new member.

Two corollaries. Where the family's shared material is substantial, the
pre-draft read is the natural moment to ask whether it should be extracted
into a core skill the members load (`shared-core`) rather than restated a
third time — the question is cheapest to answer before the third copy
exists. And the general form, which reaches well past skills: **a new
instance is the best available audit of the existing set.** Drafting it
forces the shared material to be restated from scratch, and every place
the fresh statement differs from a sibling's is either an improvement or a
gap — it is the only moment when the differences between all of them are
being actively thought about by anyone, so skipping the comparison wastes
the audit and creates the divergence.

**When the extraction does happen, work brief-first.** Write the split
rule once, before any file is touched — the test that decides where a
sentence goes (*could this sentence survive having the platform's name
removed?* → core; otherwise → companion), the confidentiality rules, the
generalisation substitutions, and any global numbering rule — and hand
that one brief to every mover, rather than letting each rediscover the
rule from the material in front of them. Then give each destination file
one mover, and require that mover to produce **both** halves of every
section it splits (the core text and the companion's remainder) plus the
coverage table from "Verifying relocations and restructures". The
reconciliation notes, not the diffs, are the deliverable the maintainer
reviews.

**A script that ships with a skill is verified by a hostile test, not a
normal run.** Each of these failure shapes passes an ordinary run and is
caught only by a test built to break it.

1. A script that rewrites part of a file reads and writes bytes, or keeps
   each line's own ending: text-mode I/O rewrites every line ending of a
   CRLF file while the edited values come out right. Test with CRLF, a
   BOM and no trailing newline, and assert byte-identity outside the
   edited region.
2. A negative requirement ("never opens the private names file") needs a
   runtime observation mechanism, an assertion that the mechanism
   recorded something at all, and one run against a deliberately broken
   version that turns the test red, or a mis-wired check passes vacuously.
3. An acceptance fixture ships with its runner (this skill's is
   `scripts/validate-skill-bundle.py --selftest`), or it decays into a
   one-off that nobody re-runs after the next change.
4. The first smoke run of a script that writes points it at a throw-away
   directory and asserts that the default location was not touched: a
   subcommand that re-declares a global option can clobber it, and the
   smoke test then writes into the real home folder.
5. A mutation run first proves the baseline green with the harness's own
   command, and each test asserts which guard rejected the input, not
   only that something did. A mutant that dies by an exception or an
   import error is investigated, not counted as killed; a surviving
   mutant means harden the fixture or delete the redundant condition.

## Runtime prerequisites — declare what the skill needs to be able to run

A skill that drives something outside itself — a CLI binary, a daemon, an
API key, a container runtime — is only as installed as the thing it
drives: the listing says the files are there, not that they can run. The
agent reads a full, confident description, selects the skill for the task
it names, and discovers the missing prerequisite partway through the work,
where it reads as the agent's error rather than the inventory's. Failure
shape: listed skills that cannot run are indistinguishable from working
ones, and the adopter's only defence is a hand-written prohibition — a
rule that has to be read and obeyed, rather than a fact the system knows;
left optional, a family drifts.

**Required for any skill that drives an external tool.** Declare the
prerequisites as *checkable facts*, so that something other than a human
reader can evaluate them, in ONE string under `metadata` — the Agent
Skills spec types `metadata` as string→string, and a top-level key of
our own fails its validators as an unexpected key:

```yaml
metadata:
  requires: "binary:docker; binary:ffmpeg -version; binary:python>=3.9; env:OPENAI_API_KEY; service:http://localhost:11434"
```

Entries are separated by `;`, each `kind:value`. Three kinds cover
nearly everything: `binary:NAME` is a binary that starts (its version
flag exits 0; a flag after the name replaces `--version`, and
`>=VERSION` after the name is the least its output may report),
`env:NAME` is an environment variable that is set and non-empty, and
`service:URL` is an endpoint that answers. Each is one cheap command, and
locating the binary is the presence check one level down — a shim or
launcher on `PATH` that aborts at load is found and cannot run. Anything
that cannot be reduced to one of those is a prose note in the skill body,
not a declaration — a check nobody can run is worse than an honest
sentence, because it looks like a guarantee.

**What consumes it.** Session Start step 6 resolves `skill:` targets and
reports the ones that do not resolve; with this string it can also report the
ones that resolve *and cannot run*. A dead target and a deleted target both
mean "observations are accumulating against something that will never act on
them", and for any skill driving an external tool the dead one is the
commoner case.

## Retiring skills — harvest before you retire

An ending engagement is a harvest trigger, not only a cleanup trigger.
Before retiring any operational skill tied to that engagement, assess each
section as either transferable methodology or client-specific
configuration. If the transferable share is substantial, extract a
client-agnostic skill FIRST and retire the original afterwards, keeping the
client dossier for reference: keep the platform mechanics concrete — real
interface quirks, DOM patterns, layered diagnostics, everything earned
through real runs and real corrections — and replace the client's answers
(account IDs, domains, source rosters, criteria) with the intake questions
that produced them, so the resulting skill tells the next agent what to
ask, rather than what the previous client happened to say. The
methodology and the client configuration wrapped around it have very
different shelf lives; retiring them together discards the durable half
at the moment its cost is already sunk, and the loss is invisible because
nothing errors.

## Principle Propagation

When an observation's Principle applies to skills in general, log it with
`skill: []` and `target_file: [skill-observations/cross-cutting-principles.md]`
and surface it; if the user approves, add it to
`[workspace folder]/skill-observations/cross-cutting-principles.md`, a
mandatory checklist during any skill creation or regeneration. The user
chooses propagation timing: immediate (update all skills now — for things
like confidentiality rules) or opportunistic (apply at each skill's next
update).

```markdown
# Cross-Cutting Principles

Principles that apply to all skills. Read as a mandatory checklist during
any skill creation or regeneration.

---

## Active Principles

### 1. [Principle title]
**Added:** [date]
**Applies to:** [all skills | all open-source skills | all skills with rules]
**Requirement:** [what it requires]
**Propagation:** [immediate | opportunistic]
**Status:** [active]
```

## Reference-file ceilings — the growth barrier

The trigger count the validator prints on every run becomes a gate for a
skill that opts in. Opting in is one file, `references/ceilings.txt`, with a
line per reference file — `<file.md> <ceiling>`, seeded at each file's
current count — and one `Load triggers: a; b; c` line in each reference
file's header (before its first `## ` heading), one entry per distinct
episode that loads it: a pointer scan cannot count episodes exactly.

**A declared trigger is an episode — a reason to load the file — not a
pointer.** One episode may be cited from several places in the core and
may cover several sections of the file; a file a run walks once (every
step of a cycle) has one episode and declares one trigger, however many
of its sections the core names. The validator cross-checks the
self-declared count against something the declarer does not control: it
prints, beside each file's declared count, the number of distinct `## `
sections of the core that cite the file — the cheapest lower bound on its
episodes, since a once-per-run file is cited from the one core section
that runs it — and notes `UNDER-DECLARED` when the declaration falls more
than two below that bound. A note, not a gate: the failure shape is a file
kept under the split threshold by declaring less than it is loaded for.
With the sidecar present, `validate-skill-bundle.py` fails when:

- a file exceeds its ceiling. The remedy follows its declared trigger
  count: more than 8, split it by episode — proposed with its per-run
  load effect named (an edit seam, a ceiling ratchet, or a token saving;
  episodes that fire with every trigger save no tokens); 8 or fewer,
  trim it, or raise
  the ceiling with a dated one-line reason beside the number
  (`<file.md> <lines> YYYY-MM-DD <why>`). The reason names the change
  that added the lines, in words a reader without the repository
  understands — the file ships inside the skill — never an issue, PR or
  observation number. The threshold comes from the measured distribution
  over one library at last measurement, not from intuition: one to eight
  triggers almost everywhere, three files above eight, and the two files
  just under the earlier threshold of 12 were the ones readers described
  as overloaded — a threshold that never fires on the files everyone
  agrees are overloaded is set too high;
- a ceiling sits more than 3 lines above its file: lower it in the commit
  that trimmed;
- a file has no ceiling line or no `Load triggers:` line.

A file above the threshold whose split is decided but not yet made carries
`split_pending: <file.md> YYYY-MM-DD <why>` in the sidecar: the validator
then prints the split remedies as notes and applies the trim-or-raise
remedy until the split lands, so a decided restructure does not block the
round before it. The line is read bare or behind `# `, so a round can
write it while the installed validator still predates the marker. In this
skill's own bundle, `observation-log.md` (20 triggers) is the next split
candidate, pending a later round.

Size alone never forces a split, so a single-episode file is still never
split to meet a size rule. Without the sidecar nothing is gated, which is
why it has a plain name: an install route that drops dotfiles would switch
the gate off without a word. Change a file's `Load triggers:` line in the
same edit as any core pointer into it.

**The ceiling is declared at the count after every pass of the round.**
The gate holds in both directions, so a round that trims and then adds
cannot declare the trimmed count; the manifest entry reports both
numbers (trimmed, declared) so the trim stays visible. At slack 0 every
added line costs a compression, and the policy names the trade rather
than leaving it to each editor: where paying would rewrite more than a
handful of paragraphs, raise the ceiling with a descriptive reason, or
schedule the trim as its own observation — a ceiling is a ratchet on
growth, not a tax on every rule. A compression that does pay for an
addition is listed in the report as a payment hunk, so a reviewer can
tell rationale trimmed from rules changed. All of this holds for
`core_max_lines` as for the reference ceilings.
