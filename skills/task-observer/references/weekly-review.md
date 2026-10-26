# Comprehensive Review (in-session)

Load triggers: a review runs (an opted-in fallback, or asked for); the start-up line counting open observations as distinct findings

Cross-checks all OPEN observations against all skills, propagates
cross-cutting principles, and applies the approved improvements directly
to the live skill files, one commit per round ("Applying changes" at the
end of this file). The review runs only with the user present: it is
offered at session start when `skill-observations/last-review-date.txt`
reads `never` or a date 7+ days old (the SKILL.md step 3 boundary, which
must match), and runs when the user opts in or asks for it — it never
gates the user's task. Its content scales with the backlog and its
frequency never does: a backlog nobody drains fails quietly, by becoming
too expensive to drain, so a bounded slice keeps the unit of work
constant as the backlog grows.

## Contents

- Approval policy
- Steps
  - Step 1 — load
  - Step 2 — inventory skills and classify each write target
  - Step 3 — cross-check observations
  - Step 4 — cross-check principles, and audit the families for drift
  - Step 5 — apply
  - Step 6 — re-scan, then mark ACTIONED
  - Step 7 — commit, record and summarise
  - Step 8 — timestamp
- Constraints
- Applying changes — direct edits and round commits

**One log per machine.** Several observation logs over the same globally
installed skills are a fork to consolidate (`references/environments.md`,
"Before creating a log, search for one"), never two queues to review
side by side.

## Approval policy

**Interactive (user present):** always present observations grouped by
skill (number, title, one-sentence summary), flag judgment calls as "needs
your input", and wait for blanket or selective approval before applying.
The grouped list lives in the review record and chat carries at most
three next steps with a link to it (Step 3); the approval it asks for is
still over the whole list.
**Classify before you ask.** Any *disposition* option offered to the user
(fold in, decline, revive, route to skill X) must be derived from the
entries' bodies, never from their titles and `skill:` fields — a
title-level summary is exactly what can be produced without reading, and
it licenses the wrong split. Read and bucket first, then present the
routing decision with the real counts attached ("15 → skill A, 25 → skill
B, 2 dead"). The trigger to watch for is a target skill that no longer
exists: "revive / fold in / decline" looks like a disposition question and
is really a classification task, because a corpus filed against one dead
skill routinely splits across several live ones. Where a bulk question
genuinely must come first (very large backlog, a session budget that will
not cover reading everything), say so in the question, mark the proposed
split as provisional, and re-present it if the contents disagree. The
order is `read → bucket → present counts → ask`, never `ask → read`.
Reading the bodies is necessary but not sufficient: a body can itself
assert a checkable premise ("the target is foreign-maintained, so it
cannot be edited in place"), and an option built on it inherits the
claim unverified. Settle such a premise BEFORE presenting the option,
from what is already local — the checkout or copy the skill was
installed from, `forked-skills.txt`, the file's own source line (or its
frontmatter `metadata.source`, `author:` and `license:`), and the tool
that generates it, if one does. Where the premise is genuinely remote,
the review must not depend on reaching the network: present the option
with that half named as unverified.
A declined or dismissed approval prompt is NOT approval — and it is not a
request to skip the asking and proceed either. Treat it as a stop signal
for the gated actions: halt, then ask in plain chat text what the user
wants. Only an explicit go (blanket or per-item) authorizes applying;
"apply the observations" as the review's trigger phrase still gates each
application on this policy, it does not pre-approve the changes.
**An approved step the tool layer refuses is not attempted again.** The
user's approval and a harness's permission classifier are two gates, and
the second judges by its own rules. When an approved action on the user's
own files outside the workspace — a deletion, a move to the trash,
removing a section from an instruction file — is refused at the tool
layer, retry it in no form (the one identical retry in SKILL.md, How to
Log, is for the skill's own workspace writes); record the item as pending
with the refusal's words, hand it to the user in the closing summary as a
step with exact paths, and continue the rest of the apply phase. Run
preparatory work (anchors, backups) in calls of its own, never in the
call that carries such an action, so one refusal does not take it down.

**Separate the recommendation from the choice before counting agreement
as evidence.** A decision that is SUBSTANTIVE — it changes a rule, retires
a prior decision or sets a value — is presented as unlabelled options in a
neutral order, and the recommendation is stated only after the pick is
recorded, or in a separate line the user can skip; a status-quo
confirmation (keep what is installed, keep the ceiling where it landed)
stays recommendation-first, where the label costs nothing. The record
notes per decision whether it was status-quo or substantive and whether
the pick matched the recommendation; only the substantive, unlabelled
picks feed the acceptance rate, and the tier moves only after a handful
of reviews. The failure shape: every decision presented
recommendation-first and labelled is accepted, and the loop cannot tell
good recommendations from anchoring — yet reads the number as grounds to
loosen.

**A decision the user already made is applied, not re-asked.** Where an
observation records a removal or restructure as DECIDED by the user AND
carries a complete specification — it names what replaces what, in
enough detail to apply without inventing anything — present it as
decided (one line, flagged as the first diff to read) rather than as a
fresh question. Where the spec is partial ("something like…", "the old
rules should probably go"), it is a question like any other. Re-asking a
decision the user already made returns their answer as a question and
costs a cycle in which the skill stays knowingly wrong.

Escalate one decision per cluster (Step 3).

## Steps

**Step 1 — load.** First, the activation regression check — the one
half of "is activation in place?" a review can reach: a review only runs
when the skill loaded, so it cannot detect an install that never
activated, but it can detect a tier that WAS in place and is no longer
(a rewritten CLAUDE.md, a hooks file replaced by a settings sync). Read
the activation config named in `references/environments.md` — the
instruction block in CLAUDE.md or its equivalent, and the session-start
hook where the harness has one — and if a tier that a previous review
recorded as present is missing, say so in the summary's first line and
re-suggest the block; record the tiers found in
`skill-observations/activation-tiers.txt` so the next review has a
baseline to compare against.

One more read belongs to the same pass. **Does the pre-skill tier's line
name the batch content, or only the probe?** Where a tier read before any
skill is in place — a preferences block, a user-level instruction file, a
session-start hook's injected text — its line must name the complete
first batch: the workspace probe AND the session-start skill loads, in one
batched call (`references/environments.md`, "The probe rides inside the
first batched call"). Flag a line that names only the probe; it fires the
probe and leaves the loads to a config that may arrive late.

A second read belongs to the same pass: **did each skill load carry its
lookup in the same batch?** Where session transcripts are available, match
the `loaded <skill>` lines in `checkpoints.log` (written by
`scripts/skill-load.sh`) against the Skill invocations. Two mismatches are
detectable failures, each a Log integrity finding: a `loaded` line with no
Skill invocation in the same batch, and an invocation with no `loaded`
line from its batch. Without transcripts, compare each session's `loaded`
lines against the skills that session reports loading, and flag a skill
with no line. The failure shape: a late lookup
looks compliant from every later batch, and the record is the one place
the mismatch shows.

Then archive observation files resolved in
*previous* sessions — with the sweep as shipped (the sweep block of the id
snippet, run on its own; see Archival on Write in SKILL.md), never an
improvised bulk move; where one is unavoidable, read the set once and
verify by conservation (`observation-log.md`, Archival). Read only the frontmatter of
each file in `observation-log/` — not the bodies — to build the work queue;
load a body only when you actually action that observation in Step 5. This
frontmatter-first pass is what keeps the review cheap as the backlog grows.

Build the work queue from the files themselves, not from a status filter.
The OPEN set is defined as: **`status` is literally `open`, OR the file has
no `status` field at all.** Concretely:

1. Enumerate every file in `observation-log/` — the directory listing is the
   authoritative list of entries.
2. For each file, read the `status` field from its frontmatter. Treat a
   missing, blank, or any status other than `actioned`, `declined`,
   `superseded` or `parked` as OPEN.
3. Never derive the work queue from a `grep 'status: open'` alone. Derive
   it from the file list minus the resolved (`actioned` / `declined` /
   `superseded`) and the `parked` files. A grep on an optional field
   silently drops every file missing
   that field — the review then confidently reports a clean backlog while
   untriaged observations are skipped.

**Reconciliation guard:** before proceeding, assert that
`count(files in observation-log/) == count(status-classified files)`. If the
counts differ, the delta is statusless files — surface and triage them (as
OPEN) rather than proceeding as if the backlog were clean. **This is a
point-in-time assertion, not a standing guarantee:** the log is
multi-writer and a long review is exactly when other sessions are logging,
so the result decays for the duration of the run. Keep the Step 1 file list ON DISK — never in a shell variable,
which does not survive the next tool call and is not word-split under zsh
(`observation-log.md`, "Under zsh…") — so Step 6 can re-scan against it
before anything is marked:

```bash
d="[ABSOLUTE PATH]/skill-observations/observation-log"
l="[ABSOLUTE PATH]/skill-observations/review-step1-list.txt"
find "$d" -maxdepth 1 -name '*.md' | sed 's|.*/||' | LC_ALL=C sort > "$l"
```

Both list files are overwritten by the next review's Steps 1 and 6 and
need no cleanup at Step 8; a Step 6 run against a list Step 1 failed to
refresh shows as a delta of dozens, not as a quiet pass.

**Duplicate-id check — nothing else in the process looks for one.** The id
rules say a collision is "left for the next review to renumber", and
without this check a duplicate could sit indefinitely — and silently
destroy review work: any pass that merges per-entry results **keyed by
id** collapses the pair into one, and the entry that loses is dropped
from the review it was waiting for, with no error.

```bash
d="[ABSOLUTE PATH]/skill-observations/observation-log"
find "$d" "$d/archive" -maxdepth 1 -name '*.md' | sed 's|.*/||' \
  | grep -oE '^[0-9]+' | sed 's/^0*\([0-9]\)/\1/' | sort -n | uniq -d
top=$(find "$d" "$d/archive" -maxdepth 1 -name '[0-9]*.md' | sed 's|.*/||' | grep -oE '^[0-9]+' | sort -n | tail -1); floor=$(sed '1!d; s/[^0-9]//g' "$d/archive/.id-floor" 2>/dev/null); [ "$((10#${floor:-0}))" -ge "$((10#${top:-0}))" ] || echo "FLOOR LAGS — .id-floor ${floor:-absent} < highest prefix $top: a writer bypassed the snippet"
```

The last line asserts `.id-floor >= highest prefix` across active and
archive. Every run of the snippet or `scripts/new-observation.sh` leaves
the floor at the id it issued, so a lagging floor means some writer
created files without running either — the earlier and cheaper signal of
the bypass, visible before any collision (`observation-log.md`, "Floor
staleness").

`grep -oE '^[0-9]+'`, not `sed 's/-.*//'`: the archive may hold legacy
`log-YYYY-MM-DD.md` files from a pre-3.0 migration, and stripping at the
first hyphen turns every one of them into `log`, a phantom duplicate. The
zero-padding strip is the same one the id snippet uses, so `0091` and `91`
are recognised as the same number.

Any output is a duplicate id across the active set and the archive. Fix it
now, before the work queue is built: keep the number on the **earlier**
entry (by `date`, then by the lower `.id-floor` era), renumber the later
one to a fresh id from the snippet, update its filename and its `id:`
field together, and note the renumber in its body so a citation of the old
number can still be traced. Then re-run the check until it prints nothing.
For each collision, and for the files above a lagging floor, record the
writing sessions — each file's `session_context` and `date` — in the Step 7
summary: the pair traces the bypass to an environment or write path, which
is where the fix goes, while a bare count blames a rule every writer that
ran the snippet obeyed.

**Per-entry header conformance — a count, not a gate.** The scan's
suspect count catches YAML that will not parse; it cannot see a header
that parses and is still wrong: an `id` that disagrees with the filename
prefix, a `status` outside the five values, a missing or blank
`siblings_checked`, or a near-miss field name (`skills:`,
`proposed_skill:`, `sibling_checked:`) that every consumer silently
ignores. Run it after the duplicate-id check, over the active directory:

```bash
d="[ABSOLUTE PATH]/skill-observations/observation-log"
nonconf=$(LC_ALL=C find "$d" -maxdepth 1 -name '*.md' -exec awk '
  FNR==1 { sub(/^\357\273\277/, ""); fm=0; bad=""; idv=""; st=""; sc=""; f=FILENAME; sub(/.*\//,"",f); pre=(match(f,/^[0-9]+/) ? substr(f,1,RLENGTH)+0 : -1) }
  FNR==1 && /^---[[:space:]]*$/ { fm=1; next }
  fm && /^---[[:space:]]*$/ { fm=0
    if (idv !~ /^0*[1-9][0-9]*$/ || idv+0 != pre) bad=bad " id"
    if (st !~ /^(open|actioned|declined|superseded|parked)$/) bad=bad " status"
    if (sc == "") bad=bad " siblings_checked"
    if (bad != "") print FILENAME ":" bad; nextfile }
  fm && /^id:/ { idv=$2 }
  fm && /^status:/ { st=$2 }
  fm && /^siblings_checked:/ { sc=$0; sub(/^siblings_checked:[[:space:]]*/, "", sc) }
  fm && /^(skills|proposed_skill|proposed_skills|proposes_skills|sibling_checked|siblings_check|target_files|skill_qualifier):/ { bad=bad " near-miss:" $1 }
' {} +)
n_nc=$(printf '%s' "$nonconf" | grep -c .)
if [ "$n_nc" -gt 0 ]; then printf 'NOTE: %s non-conforming headers (id / status / siblings_checked / near-miss field):\n%s\n' "$n_nc" "$nonconf"; fi
```

It reports; it does not block the review. Its false-positive rate on a
real corpus is unmeasured, so record three numbers the first time it runs
over a live log — hits, true defects among them, and how many were
normalised — and decide from those whether it stays a report or becomes
a gate (`skill-authoring.md`, "a recommended check carries three
measured numbers"). A header with no closing `---` is not reported here;
the scan reports it, by name, when `parsed` (closed headers) is below
`files`. Fix a hit the way
the duplicate-id check fixes a renumber: one field in one file, with the
filename left alone unless the id is the field at fault.

**And key the merge on the filename, not the id**, wherever a review fans
reading out and merges results: the filename is unique by construction
(the noclobber create guarantees it), and a merge keyed on the one field
that can collide has no way to notice that it did.

**Parked entries: excluded from the queue, not from view.** `status: parked`
means the observation was judged sound but is blocked on an external
precondition recorded in `parked_until:` (SKILL.md, How to Log). It is a
decision, so it must NOT be re-escalated — but it is not resolved, so it also
never archives and stays in `observation-log/`. Two things happen to it in
every review, while the frontmatter is already in hand: (a) re-check each
`parked_until:` condition against the current state of the world, and where it
has been met, set the entry back to `status: open`, clear `parked_until:`, and
carry it into this review's queue; (b) list every still-parked entry in the
Step 7 summary in ONE LINE each — id, title, unpark condition — so a parked
backlog stays visible without re-entering the work queue. A condition
phrased on the state of a vehicle — a PR merged or closed, a ticket
resolved — is re-checked on the result it was meant to deliver, the text
of the target artefact, because the result routinely arrives by another
path (`observation-log.md`, "A park condition names the result, never
your own vehicle"); a refresh of an upstream-maintained skill is that
check for every entry parked on it.

Also read all active cross-cutting principles. If there are no OPEN
observations and no outstanding principles: report "no open observations
or outstanding principles", update the timestamp, and stop.

**Step 2 — inventory skills and classify each write target by whether
an edit SURVIVES, not by whether it succeeds.** List all skills (system
prompt `<available_skills>` or the skills directory) and put each into one
of three categories. Project-level skill directories (a project's
`.claude/skills/`, where the harness surfaces them) are listed and
classified too, and a project skill that duplicates an account skill is
named as such: two copies of one skill drift exactly like two copies of
one rule, and an inventory that reads one surface never sees the other.
The categories:

| Category | Detection | Action |
|---|---|---|
| (a) User-owned, no upstream | in the user's skills directory or the user's own repository (a symlinked skills entry resolves into it); not refreshed from anyone else's upstream; written by the user, not by a tool — or a fork recorded in `forked-skills.txt` | edited in place, one commit per round ("Applying changes") |
| (b) Writable but volatile, or foreign-maintained | path contains a plugin cache or version-pinned directory; or the skill is refreshed from an upstream by clone/copy or `git pull`; or **the file's own content declares a maintainer other than the user** — an attribution block naming another author, a canonical repository the user does not commit to, a `source:`/`upstream:` frontmatter field, or third-party `author:`/`license:`/`version:` frontmatter with no fork recorded in `forked-skills.txt` — wherever it is installed and however it got there, a hand-copied and hand-updated file included; or **the file is written by a tool that will rewrite it** (a scaffolder, a CLI's `init`/`agent`/`sync` command, a spec or template generator), which leaves no maintainer mark at all | never edit in place — the next update silently discards it, and no permission error ever fires |
| (c) No on-disk file, or read-only | built-in / harness-provided skills (e.g. docx, pdf, xlsx, pptx, skill-creator); a mount that rejects writes | cannot be edited |

Observations targeting (b) or (c) are NOT skipped — the destination must
be one that survives and that something actually loads. Offer both routes
and let the user choose: a complementary user-owned `{skill}-extras` skill
holding only the delta **plus** a routing entry in the user's instruction
file (state plainly that without the routing entry nothing ever loads the
companion — a fix routed somewhere nothing loads is not a fix); or routing
the content straight into the instruction file, which loads
unconditionally. Editing the file in place is not on the menu, however
writable it is. Provenance is a property of the artefact
and is stated in its first lines; install location says nothing about
who maintains the file, so read the block before the path. A generated
file is the exception that states nothing: its writer is a tool, not an
author, so before putting a skill in (a) ask what writes the file, not
only what refreshes its directory. Where the user has adopted a vendored
copy on purpose, record it once, one line per skill in
`skill-observations/forked-skills.txt` (name, date, reason): later
reviews read the decision instead of re-deriving it from the path, and a
recorded fork is (a). This skill is the standing example: wherever the
user is not its maintainer, `task-observer` is (b). Choosing the
companion route may mean creating the `{skill}-extras` skill in this
review, which the Constraints allow as the one exception to "no new
skills in a review". Grow the (c) list when an update fails for
permissions; grow the (b) list when a change you made has vanished — a
rule that fires after the damage, the backstop for the attribution read.

**Run the validator over the live set while the inventory is in hand.**
Step 5 validates what a round edited, so a skill no round touches is
never checked again while the validator's own checks tighten. Run
`scripts/validate-skill-bundle.py` over every category-(a) live skill
directory — seconds for a whole library — and list the failures in the
Step 7 summary under Log integrity ("N installed skills fail the
validator: …"). A failing skill with no observations in the queue gets a
one-line round that fixes only the gate failure.

**Step 3 — cross-check observations.** Evaluate every OPEN observation
against every skill — not just the skills named in its `skill:` list;
Principles often generalise. Build skill → [relevant observations], seeding
it from the frontmatter: every entry in an observation's `skill:` list puts
it in that skill's bucket (the first entry is primary), every entry in
`proposes_skill:` puts it under a new-skill candidate of that name, and
every entry in `target_file:` puts it under that file — a bucket the review
applies to by the file's owner (Applying changes, "Non-skill files are
split by owner": written directly when the review owns it, a round when
it lives in the user's repository, a patch handed over when another
process owns it), instead of remapping the entry onto the nearest
skill. An observation may appear in
more than one. Key each bucket on the skill's listed name, not the raw
string: a bare name that matches exactly one installed `plugin:name` joins
that bucket; a bare name matching several, or a descriptive form, is
resolved from the body, never by guess; and every normalisation is listed
under Log integrity in the Step 7 summary. Report there too the count of
entries whose `skill:` holds a plugin-qualified name (`plugin:name`) and
the count in bare form: a log carrying both spellings is the one in which
a lookup given either spelling silently misses the other. One skill written two ways is
otherwise two smaller clusters, and the family check misses that both
entries target the same member. Then, before anything is presented:

- **Routing check, before the presence check.** `skill:` is written
  mid-task by whoever noticed the symptom, so it names the symptom
  reliably and the location unreliably, and the write-time check asks
  only whether the name resolves. Open each target and confirm it
  performs the operation the Issue describes. If it does not, re-route —
  to the skill that does, or to the non-skill file that does (an
  instructions file, an agent definition, a scheduled prompt), which
  becomes a `target_file:` bucket whose output is a patch for that file,
  routed by its owner (Applying changes) — and note the move in the body ("routed
  from X to Y: X never performs the append"). A fix installed where it
  cannot fire closes the entry and leaves the defect standing.

- **Presence check, here, against the real target — and against the
  Issue, not only the suggestion.** Step 5 greps the live file for
  each improvement before writing; run that same already-applied /
  partially-applied / outstanding classification here too, before
  anything is presented, so the user is never asked to approve an
  applied entry. A phrase search over hard-wrapped Markdown matches
  within a block with whitespace normalised, never line by line
  (`observation-log.md`, "A park condition names the result, never your
  own vehicle"). Run it against the file the observation actually
  targets — its `skill:` entries, its `target_file:` entries, the code or
  register it names — never a proxy such as a routine's own `SKILL.md`
  when the entry asks for the register that routine declares. Close what
  is already applied, with a resolution naming where it was found.
  Search two surfaces, not one: the substance grep is worded by the
  reviewer and the fix by whoever applied it, so a zero there is a claim
  about the pattern (`observation-log.md`, "Every instrument gets the same
  guard"). Where the project cites observation ids in commit messages or
  code comments, also search the citation, for example
  `git log --since=<entry date> -E --grep='#0*<id>([^0-9]|$)'` and
  `git grep -nE '#0*<id>([^0-9]|$)'`, and treat a hit on either surface
  as an already-applied candidate, opened and read point by point. Record
  `outstanding` only when both surfaces are empty. Where commits also cite
  issue numbers, a `#<id>` hit may be an issue, so open it before counting
  it.

- **Fix the system that owns the problem.** Before adding a skill rule,
  check whether a code, configuration or CI change would remove the
  failure. If so, recommend that fix: name the file, the change and how to
  verify it. Keep a workaround instruction only while it is needed, and
  identify the fix that will let a later review remove it. Implementing
  that fix still follows the user's scope and the approval policy.
- **An entry about a recurring act names its check.** Where the Issue is
  an act a session repeats, confirm the Suggested improvement names the
  check that catches a violation (`observation-log.md`, "Commands inside
  an observation") and that the applied change carries it: a rule applied
  as prose alone is knowledge the next session may or may not hold at the
  moment of the act. An entry with no check is not declined for it —
  name one here, run it on the entry's instance, record the run, or route
  the entry to the instrument that can run it.

- **Consolidate new-skill candidates by the problem they solve, not by
  name.** Independently logged proposals for the same skill will not look
  alike, because each is named after the task that surfaced it. Present merged
  clusters with their constituent observation ids.
- **Existence check before any new-skill cluster is presented.** A
  `proposes_skill:` or a `siblings_checked: none` is an absence claim
  scoped to the session that wrote it. Search the scopes that session
  could not see — other projects' `.claude/skills/` and the generator
  sources they are rendered from — by the problem terms in the bodies,
  not only the proposed name, and run the presence check above against
  any skill found: an observation proposing a skill that already exists
  elsewhere is an improvement to that skill, and may already be applied
  there.
- **Supersession check.** Where a later observation's finding is that an
  earlier one's mitigation does not work, mark the earlier one
  `status: superseded`, `resolution: "by #N"`, and carry only the later
  one forward.
- **Family propagation.** An observation whose `skill:` list carries more
  than one entry is not actioned until every listed skill has been updated
  or explicitly dispositioned — partial application is the default failure
  and it is silent, because the observation gets marked `actioned` on the
  strength of the first skill it touched. Record the per-skill disposition
  in `resolution:` and carry it into the Family coherence block of the
  summary. Where a legitimate partial application exists (one session owns
  a subset of the listed skills), the carrier pattern in
  `observation-log.md` resolves it — and a carrier observation enters this
  queue as first-class, never deferred on account of its provenance. Also check `siblings_checked:` while the frontmatter is in
  hand: an entry with the field missing or blank was logged without the
  check, so before actioning it, do the check now (registry, tests and
  fallback in `observation-log.md`) and widen `skill:` if it was
  under-scoped. Count these — "N observations logged without a sibling
  check" is a health metric of the logging practice, not a per-entry
  nuisance. Count the `assumed` exclusions the same way, from the
  frontmatter alone, and open each such sibling before actioning the
  entry: an exclusion grounded on `assumed` is a review item, not a
  verdict (`observation-log.md`, "Record the verdict"). Check
  `commands_verified:` in the same pass: a body that quotes a command or
  proposes a predicate with the field missing or blank quotes one nobody
  ran — run it now, on the instance the entry describes, or record
  `NOT RUN` with why, before the entry is actioned or cited.
- **Confidentiality pass over the log itself.** For every OPEN
  `open-source` observation, check the Issue and Improvement fields for
  client-identifying specifics no longer needed for context and strip
  them. The log is the artefact most likely to be shared casually, and
  the authoring-time sweeps never see it.

Interactive: save the full decision list — grouped by skill, as the
Approval policy requires — in the review record (Step 7). In chat, show
at most three recommended next steps, ordered by impact. For each, state
**problem → concrete change → verification** in plain language; name
whether the change belongs in a skill, agent instructions, or tooling.
Link the full list and say how many decisions remain. Group duplicates
and exclude already-fixed items before choosing the three. Await
approval: the user may approve the three, the whole list in the record
in one step, or a selection from it; a short list does not authorize the
rest of the backlog.

**Cluster by decision BEFORE the escalation list is written.** An
append-only log accumulates convergent entries by construction: the same
underlying problem is rediscovered from different task contexts and filed
against different skills, so grouping by filing category asks the user
the same question more than once. Group the OPEN entries by the DECISION
they require, not by the skill they are filed against; escalate one
decision per cluster with the member observation numbers listed under
it; cross-reference rather than separately escalate any entry whose
decision duplicates another's. Cheap first pass: scan the Principle lines
— convergent observations usually have near-identical principles even
when their Issues describe unrelated tasks. Corollary for in-session
behaviour: if you notice the overlap strongly enough to offer "this is
the same as X" as an answer option, that is the answer — take it and tell
the user. **Across an ownership fence:** when the
backlog is split across parallel sessions and you defer an entry to a
cluster owned by the other session, the deferral is not complete until the
pointer exists on BOTH sides — relay it to that session directly, or
surface it to the user as a handoff item. A one-way note leaves the entry
pointing at a decision that may be settled without it.

**Step 4 — cross-check principles, and audit the families for drift.**
Flag every skill that doesn't yet comply with each active cross-cutting
principle. A missing `skill-observations/cross-cutting-principles.md` is
abnormal, not empty: Session Start step 1 creates it, and it is the one
artefact of that step nothing reads until this step, so its absence has
no observable consequence before it — a step that runs without
leaving a trace is indistinguishable from a step that was skipped. Create it from the template in
`references/skill-authoring.md` now, say so in the summary's first line,
and log the skipped step as an observation.

Then run the **family drift audit**: for each family in
`skill-observations/skill-families.md`, grep every member for each rule
listed as shared and surface the gaps. Grep where each rule can live: a
member Step 2 put in (b) or (c) carries only what its upstream wrote, so
for a rule written locally grep the destination Step 2 routed it to (the
`{skill}-extras` companion or the instruction-file entry), and say so in
the audit line. A zero over a population that cannot contain the rule is
a statement about the instrument, not drift (`observation-log.md`,
"Every instrument gets the same guard"). It is mechanical, takes minutes,
and is the only part of the family mechanism that catches drift predating
the rule or introduced by a skill authored outside the log. Two
disciplines make the output usable: judge each gap against the family's `Member-specific` column
before calling it drift (absence is sometimes correct), and resolve it
according to the family's coherence model — `synced-duplicates` means
editing every member, `shared-core` means editing the core and checking
the pointers. Where the audit finds a rule missing from members that need
it, log it as an observation naming all of them rather than fixing it
silently, so the correction is visible to the next review. If no registry
exists yet, build one from this pass: the audit's grouping IS the first
draft of the registry. Cadence is monthly rather than every review unless
the library has grown or a new family member was authored since the last
audit — a new member always warrants one (see `skill-authoring.md`, New
skills).

**Promotion pass — periodic, not weekly.** Monthly, or every Nth review:
extract the candidate rule statements from every installed skill
(headings and bolded rule sentences suffice), cluster them by substance,
and report any rule stated in three or more skills with no entry in
`cross-cutting-principles.md` as a promotion candidate — three independent
derivations is the operational definition of cross-cutting, countable
without judgement. Promotion stays the user's decision. Mine the skills,
not the observation bodies: the skills are the distilled layer, and
duplication there is already evidence that the review saw the same thing
more than once and filed it locally each time. Report the method's
negative control beside its hits — a vocabulary match such as a common
verb over-clusters, one word carrying opposite rules in two skills — or
the shortlist is noise with a confident count attached.

**Step 5 — apply.** Edit the live files directly, one round per skill
(or per non-skill file), following "Applying changes" at the end of this
file. Before the first edit of a round, read the live file fresh and make
sure the repository is current — the files the round touches carry no
change you did not make, and a repository shared across machines is
pulled first: a stale checkout looks exactly like a fresh one.

**Verify an observation's factual claims against the live system before
promoting them into a skill.** An observation records what one session
saw; a skill states what is true, and promoting the first into the second
verbatim launders a sample into a rule that outlives every chance to
notice. So before a factual claim about an external system enters a skill — a
schema, an enum, a field's behaviour, a transition rule, "X is always Y" —
re-run the smallest query that would falsify it, and widen the sample past
whatever state the original session happened to be looking at. Where the
system is unreachable at review time, promote the claim **with its
provenance** ("observed on N documents, all in `approved` status") rather
than as a fact, so the next reader knows what would have to be re-checked.
The provenance has two forms, by skill class: an internal skill carries
the date and the count; a published skill carries scope without a date and
without per-project counts ("observed on one tracker at last
verification"), because a dated first-party claim is forbidden there
(`references/skill-authoring.md`, Timelessness).
The cost is one query; the alternative is a rule that is wrong in exactly
the cases nobody sampled.
A command the entry quotes is a claim of this kind; its `commands_verified:`
clause (`observation-log.md`) says whether anyone has run it. A predicate
the entry proposes — a regex, a hook condition — is one too, and a
predicate never run at write time gets its first run here, on the
instance the entry describes. **When running a quoted command, flag or
predicate shows the suggested form is wrong, apply the form that ran and
record it:** append "applied form differs from the suggestion: <form>" to
the entry's `resolution:` (Step 6), and list the entry under "corrected
on apply" in the summary (Step 7). A trailer key the tool does not take
(`git commit --trailer "BREAKING CHANGE=…"`, which git writes as free
text) or a filter flag that does not exist is applied in the form that
works; left unrecorded, the entry, which later readers and any upstream
report quote, still carries the wrong command.

**Standing rule — a review opens a freeze on the artefact.** When the
user begins reviewing a round's diff or a changed file, stop
producing new state on it. Defects found during the review are reported,
not applied — "spotted X in what you are reading; fix now, or note for
after?" — because the cost of re-reviewing is the reviewer's, so the
choice is theirs. One artefact, one version, per review cycle: if
something must change, say explicitly that the previous version is
superseded and name what to re-read. Prefer an immutable review artefact
— a diff written to a file is reviewable at the reader's pace and cannot
be invalidated by later work — and offer it first, not as the recovery.
Batch corrections behind the review, never in front of it: work done
while someone is reviewing is contention for the same object, and every
revision spends the reviewer's attention again from the beginning.

**Presence check before writing anything:** grep
the live file for the substance of each suggested improvement — and
search the id citation as well, the two surfaces of Step 3 — and
classify it as already-applied / partially-applied / outstanding — an
`open` status is not evidence the work is outstanding, and applying an
already-applied observation over a section that has since been refined
regresses the skill in the name of improving it. The classification is
made per point of the body, naming the line that covers each: an entry
is already-applied only when every point has its line, and one point
without a line makes it partially-applied, whatever the title suggests;
a point that joins several conditions (A and B) counts as one point per
condition (`observation-log.md`, "Read the full body before resolving,
dismissing, fixing or citing"). Classify against the
**Issue** as well as the suggestion: `already-applied` needs both — the
suggestion's substance is present AND the failure the Issue describes
can no longer occur. Where the suggestion is present but the failure
can still occur, the entry is `partially-applied`, whatever the
suggestion asked for; for an observation about a manual step or a
missing automation the test is one question — after this change, does
anyone still have to do the step by hand, and if an automation exists,
what calls it? An observation closes on its
problem, not on its proposal. Mark already-applied entries `actioned`
with a resolution noting that a prior session applied them, and leave
the section alone. A `partially-applied` entry names the remainder in
`resolution:` ("suggestion applied; issue still open: <what can still
happen>") and logs that remainder as its own observation in the same
turn — the carrier pattern in `observation-log.md` — so it stays in the
queue after this one archives. When this run applies the remainder
itself, it adds only the points without a line, never restates the ones
that have one — a second copy of a present rule drifts from the first —
and names both in the resolution: the points a prior session applied and
the ones added now. Then
produce an updated SKILL.md: integrate insights into the sections where
they belong (never append an observations list at the bottom); preserve
structure, voice, and attribution; place new rules where they logically
live. Follow the editing rules in `references/skill-authoring.md` (live
file as base).

Rewrite additions for the skill's reader rather than copying observation
prose: put the rule first, use one idea per sentence and at most one example
per change (`references/skill-authoring.md`, Lean Content — the example
stays; bare rules get violated more than rules with context). Re-check the
draft against the observation so the shorter wording preserves every
required behaviour and verification step.

**Scaling note — fan out when the apply-phase is large.** When the
apply-phase spans more than ~3 skills or ~10 observations, delegate Step 5
to parallel subagents clustered by skill rather than applying everything
in the main session. Count partitions, not items: a batch whose edits all
land in one file has no partition and is applied inline; the observation
count is then a context-budget signal, and the merge-time checks still
run. Brief each subagent with: the observation ids (files) to read, the
live path of the one skill it owns (it edits nothing outside it), the
integration logic for observation interdependencies (which observation
supersedes, refines, or folds into which — the parent must state this per
cluster explicitly, or subagents applying observations sequentially
produce patch-on-patch instead of coherent final state), the
confidentiality rules for open-source skills, the instruction to read
`references/skill-authoring.md` in its own context before its first write
to a skill file (the parent's load does not carry over), the rule **never
introduce `: ` into an unquoted frontmatter value** (a subagent extending
a `description:` is the common way a skill's frontmatter stops parsing),
the rule that no Python check leaves bytecode in the skill tree — a
compile check runs as
`python3 -I -X pycache_prefix=<scratch dir outside the skill> -m py_compile <file>`,
because `py_compile` writes its `.pyc` whatever `PYTHONDONTWRITEBYTECODE`
says, and under `-I` settings go as `-X` options, not environment
variables — an explicit delete scope (only files it created, by path,
never a recursive delete of a directory it did not create), whether the
pass is a content pass or a reformat (never both in one edit), and an
explicit rule that subagents do not commit, do not change any
observation's status and do not write observations: a finding worth
logging goes in the subagent's final report and the parent writes it.
Every brief requires the final report to be written to a file in the
scratch area as well as returned, so a hand-back lost with an interrupted
conversation is recovered by reading the file. **A phase that will write
is briefed as a write phase from the start**, with the user's
authorisation for the writes quoted verbatim in the brief — never a
read-only brief later widened by a message from the parent: a permission
classifier reads that widening as laundering and refuses the write. The
parent runs `scripts/validate-skill-bundle.py` on EVERY changed skill
BEFORE any commit or status bookkeeping — a subagent's "done" is a claim
about its own edits, and the validator is the one check that sees the
file the edits produced — and then makes the round commits itself. The
principle: the apply-phase is embarrassingly parallel across skills but
the bookkeeping and the commits must have one owner — split the work
along that seam.

**A delegated adversarial review needs the unchanged files its central
claim depends on.** When a fix is sent to a second agent for review, the
natural brief is the changed files, the diff and a log. That is exactly
wrong when the fix's central claim is about something it did **not**
change: an assumption about how a caller behaves, what a default is, what
some other file guarantees.

So build the brief from **what the claim depends on**, not from what the
change touched: name the fix's load-bearing assumption in one line, and
include every file needed to confirm or refute it, changed or not. Ask the
reviewer to report an unverifiable central claim as a failure of the brief
rather than a finding — otherwise "not verifiable" is filed beside the
minor findings and reads as a completed review.

**The orchestrator owns a merge-time validation pass.** Splitting work
across parallel workers splits the verification surface with it, and the
split is not clean: local checks partition neatly, global invariants do
not partition at all — every subagent can return a provably clean batch
and the merged artefact still be wrong. Assume that everything the
workers could not see is exactly where the defects are. So after the
returns are in, and before anything is marked actioned or delivered,
re-verify globally over the combined result. Four checks, at minimum:

1. **Cross-slice duplicates and collisions** — two subagents handed the
   same source signal will independently produce near-identical output,
   and neither self-check can fire because neither can see the other.
   Here that includes the same rule landing in two skills' sections with
   divergent wording, and two slices editing one file.
2. **Vocabulary and convention consistency across slices** — where the
   brief was under-specified, each worker resolved it locally,
   defensibly, and differently. The inconsistency is invisible inside any
   one slice and obvious across the set.
3. **Conformance of the combined totals to the plan** — every observation
   routed, every skill in the plan edited, counts matching, no
   multi-skill observation applied to only some of its listed skills
   (Step 3, Family propagation).

4. **Characterisations, not just values** — the verification pass reads
   naturally as a rule about values (counts, fields, totals), and holds
   least where outputs are stated as judgements: a reported conflict,
   defect, risk or readiness verdict carries no unit to check against,
   and a wrong characterisation is consumed by being *agreed with*,
   leaving no trace. Any subagent claim that will reach the user as a
   finding is spot-checked against the source by the parent before it
   leaves the session — one grep is usually enough; the structural
   trigger is the moment you are about to attribute a problem to
   something you did not read yourself. Require subagents to return the
   evidence alongside the claim (the file, the line, the matched string)
   so the check is cheap; a claim without locatable evidence is a claim
   to verify, not to relay.

Corollary for the brief: require every delegated agent to close with a
"decisions the brief did not cover" section. That section is how brief
defects are discovered — an agent that silently resolves an ambiguity
converts a fixable specification bug into an invisible inconsistency. And
when two independent agents flag the same ambiguity, the brief is the
defect, not the agents: fix the brief and re-issue rather than
adjudicating the two outputs.

**Step 6 — re-scan, then mark ACTIONED.** Before any status is written,
re-enumerate `observation-log/` and compare the listing against the file
list built at Step 1. The queue is a snapshot of a shared, append-only
store, and every downstream count and consistency check in this procedure
is computed against the queue rather than the directory — so a stale queue
produces a summary that is coherent, confident and incomplete. Files in
the new listing that were not in the Step 1 list arrived during the run:
they are OPEN and were never triaged. Classify each rather than merely
counting them: (a) it targets a skill whose Step 5 round is still open
(not yet committed) in this run → fold it in and action it (the common
case, and the one where a miss costs most, because the next review then
starts from a commit whose scope nobody re-derived); (b) otherwise → leave
it OPEN for the next review and list it under the "arrived during this
run" line of the Step 7 summary. Never let the delta pass silently, and
never infer it from an id counter — a number above the scan's maximum is
a side effect, not a detection mechanism. The check is a line-oriented
set difference against the Step 1 list, with both paths re-derived in
this call and a count guard on the new listing:

```bash
d="[ABSOLUTE PATH]/skill-observations/observation-log"
l="[ABSOLUTE PATH]/skill-observations/review-step1-list.txt"
now="[ABSOLUTE PATH]/skill-observations/review-step6-list.txt"
find "$d" -maxdepth 1 -name '*.md' | sed 's|.*/||' | LC_ALL=C sort > "$now"
n_now=$(find "[ABSOLUTE PATH]/skill-observations/observation-log" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')
n_list=$(wc -l < "$now" | tr -d ' ')
[ "$n_now" -eq "$n_list" ] || { echo "RESCAN COMMAND BROKEN — $n_now files, $n_list listed"; exit 1; }
echo "arrived:"; LC_ALL=C comm -13 "$l" "$now"
echo "gone:";    LC_ALL=C comm -23 "$l" "$now"
```

Positive control before trusting it: create a throwaway `.md` in a copy of
the directory after the Step 1 list is written and confirm `comm -13`
names it — a broken comparison can invent or hide a delta without moving
any count. A file the review itself archived since Step 1 shows under
`gone:`; that is expected, and only an unexplained departure is a
finding.
Re-run the Step 1 duplicate-id check over the new listing as well: this
re-scan is not redundant with Step 1, because the collisions it exists to
catch are the ones created *during* the run.

Then, in each applied observation's frontmatter set
`status: actioned`, `resolved: YYYY-MM-DD` (today), and
`resolution: "Applied to [skill-name] in <commit hash> (weekly review)"`
— editing only those fields, in that one file. An entry whose quoted
command or predicate the Step 5 run disproved carries the correction in
the same field: `… (weekly review); applied form differs from the
suggestion: <form>`. An entry Step 5 classed
`partially-applied` is marked the same way, with the remainder named in
`resolution:` and its carrier observation already written (Step 5): a
resolved entry is the one thing no later step re-reads, so the
remainder must live in the queue, never in the resolved file. The
`resolved:` date is load-bearing: archival is
gated on it (files archive only when it's before today), so a dateless mark
breaks the cross-session grace period. Do NOT archive same-session — the
next write on a later day archives them.

**Step 7 — commit, record and summarise.** Each round is committed as
it completes ("Applying changes"). Save the complete record under
`[workspace folder]/skill-observations/reviews/[date]/REVIEW.md`, using the
template below. In chat, report what changed — one line per round with
its commit hash — and its verification, followed by at most three
remaining next steps in the Step 3 format. Link the record for the full
accounting; an observation count alone is not an outcome. Records are
kept: no step prunes `reviews/`, and old ones are the user's to delete.
The summary ends with the line **"N rounds committed: <hash> …"**, taken
from `git log` of this run, never from memory of having committed.

```markdown
## Weekly Skill Review Complete — [date]

Updated skills ([N] observations, [N] principles applied):

**[skill-name]** — [1-sentence change summary]; observations #[N], #[N]

**[workspace file written directly]** — [its diff] (Applying changes,
"Non-skill files are split by owner"); or "none"

### Observations Actioned
[numbers and titles]
[corrected on apply: #id — suggested form → form that ran; or "none"]

### Family coherence
[each multi-skill observation: applied to all listed skills, or partially
applied with the outstanding skill named — never left implicit]
[drift audit: gaps found per family, and how each was resolved]
[N observations logged without a sibling check]

### Parked
[one line each: #id — title — unparks when: [condition]; plus any entry
whose condition has been met and was returned to the queue this review]

### Arrived during this run
[from the Step 6 re-scan: #id — title — folded into [skill] / left OPEN
for the next review; or "none" — the line is never omitted]

### Log integrity
[duplicate ids renumbered and any floor lag (Step 1), each with the
writing sessions' session_context and date; `skill:` names normalised for
bucketing (Step 3), old → new; `skill:` entries in qualified and bare
form (Step 3), N / M; "N installed skills fail the validator: …"
(Step 2), each with its one-line round; or "none"]

### Skipped (needs manual review)
[items with reasons]

[N] rounds committed: [hash] [hash] …
```

Wait for the user to acknowledge before other work.

**Step 8 — timestamp.** Bound to the record: written only once Step 7's
`reviews/[date]/REVIEW.md` exists and is non-empty, by one guarded command
whose date is the one Step 7 saved the record under — never a fresh
`date`, so a run crossing midnight does not fail its own guard:

```bash
d="[DATE]"   # the [date] Step 7 saved the record under
w="[ABSOLUTE PATH]/skill-observations"; r="$w/reviews/$d/REVIEW.md"
[ -s "$r" ] || { echo "NO REVIEW RECORD — not timestamping"; exit 1; }
printf '%s\n' "$d" > "$w/last-review-date.txt"
printf 'completed %s\n' "$d" > "$w/review-started.txt"
```

A fired guard is reported as "review [date] left no record" and the date
file keeps its value; Session Start step 3 reads the same gap when a dated
`last-review-date.txt` has no `reviews/[date]/` beside it. A timestamp
write whose outcome is unknown — the call timed out, the device bridge
disconnected — is the run's to verify, never the user's: the Step 7
summary and any notification report it as "unconfirmed — verified at the
next reachable call or by the next session's start". Verify it with one
read of both files on the next call that reaches the workspace; where the
run ends first, Session Start step 3's read of the two files is that
verification.

## Constraints

- Don't modify observation files beyond their `status`, `parked_until`,
  `resolved`, and `resolution` frontmatter fields —
  **with one exception: correcting a target that was recorded wrongly.** `skill:` and
  `proposes_skill:` are validated at write time, and that validation can
  return the wrong answer: a session in a stale checkout, or one resolving
  against the wrong install, judges an existing skill absent and files the
  observation under `proposes_skill:` instead. Left alone, such entries sit under a new-skill candidate
  for a skill that already exists, and every later review re-reads them the
  same way. A review that establishes the target does exist may correct
  those two fields, and records the correction in `resolution:`. Nothing
  else in the body changes.
- Don't create new skills in a review — note candidates for the user to
  action via the skill-creator. The one exception is the `{skill}-extras`
  companion for a read-only or volatile target (Step 2): it is a routing
  container for approved deltas, not a candidate skill, and creating it
  when the user chooses that route is part of applying the observation.
  It is created and committed like any other round; and it still needs
  the routing entry, or nothing loads it.
- Unsure how to integrate an observation → skip it and say so in the
  summary.
- Treat internal observations with the same rigour as open-source.

## Applying changes — direct edits and round commits

**A message drafted ahead of a delayed send, or read after one, states
status that has since changed.** Where a delivery message, commit body or
summary is composed now and read later — a run gated behind a waiting
period, an automated send, a queued handover, or a session-end summary
the user reads hours on or pastes into another session — its *measured*
values are usually filled in correctly at send time from live output.
The prose is not: it goes out verbatim, with exactly the authority of the
measured figures beside it.

So in anything drafted for later sending or reading: **state only what is
measured at send time, or nothing.** Claims about the state of other
branches, commits, tickets or sessions either come from a value the run
computes as it sends, or come out — a sentence that was true when written
is the one part of the message nothing re-checks. A claim about state
other sessions or the user can change — a commit not yet pushed, a PR
open, a run pending — states when it was measured and the one command
that re-checks it ("as of 15:19, the round is committed and not pushed;
re-check: `git status -sb`");
a claim that cannot carry both comes out. The delay can sit in the
reading rather than the sending: a closing line that was true at 15:19
reads as current when pasted into a new session an hour later, and that
session spends its first calls disproving it.

Edit each approved change straight into the live file. A skills entry
that is a symlink into the user's repository is resolved first (`cd` into
it and `pwd -P`): the repository is where the edit lands and what git
tracks. **One round = one skill (or one non-skill file) = one commit.**
Within a round: read the live file fresh; make the edits; run
`scripts/validate-skill-bundle.py <skill directory>` on the changed skill
and fix every failure — description length, frontmatter parse, reference
paths, ceilings (a ceiling failure is fixed by trimming or lowering,
never by skipping the validator); then commit only that round's files,
with the message drafted by the user's commit-message convention where
one exists. Never sweep unrelated working-tree changes into a round's
commit: where the repository already holds uncommitted changes in a file
the round touches, stage only the round's hunks (its own diff, applied to
the index with `git apply --cached`) and leave the rest as it was. Do
not push unless the user asks. A skill in category (b) or (c) (Step 2) is
never edited in place, however writable it is.

**The commit is the baseline.** The diff a reviewer reads for a round is
`git show <hash>`; no copy of the previous state is kept beside it. Keep
whitespace passes out of content passes: a re-wrap moves every line, so
the diff reports total churn and the few lines that actually changed are
invisible in it — content first, reviewed; a reformat, if any, is its own
round.

**Executable artefacts go live when registered, not when written.** The
second-violation rule makes the review produce barriers — a hook, a lint
rule, a script a hook calls — and each refuses calls the moment the
harness runs it. Write and commit the script like any other round, but
leave the registration (the settings entry that makes the harness run it)
to the user, with the exact entry to add. Before handing it over, run the
script offline on payloads built from the real tool record (`signals.md`,
"Second violation — why a barrier, not a rewording"); after the user
registers it, the next session confirms it refuses the real command and
passes a legitimate one.

**Non-skill files are split by owner.** The files this skill's review
owns in the observation workspace — `cross-cutting-principles.md`,
`skill-families.md`, `forked-skills.txt`, `activation-tiers.txt`,
`checkpoints.log`, `last-review-date.txt` — have no repository and are
written directly: re-read the file immediately before the write and apply
the change as a patch to that read, never as a copy prepared earlier. An
instruction file that lives in the user's repository is a round like a
skill: edited and committed. A file another process owns outside any
repository is handed to the user as a patch (a unified diff against the
live file, `diff -u`), never as a snapshot to copy over: every run writes
such a file, so a snapshot goes stale with the next run and its copy
instruction becomes an overwrite that deletes everything written since.
The Step 7 summary lists each such file with its diff.

**Follow-up work becomes a parked observation, never a note.** Anything
a review recognises as "check next time" — a sibling to mirror, an audit
to run once a change has seen some use — is logged as its own observation
before the summary is written: created with `status: open`, as the
file-format rule requires of every new entry, and parked in the same turn
— `status: parked` plus a named `parked_until:` condition. That puts it in
the queue the next review reads by procedure (Step 1 re-checks every
parked condition; Step 7 lists every parked entry). A note in a commit
message, a chat summary or the review record cannot carry a follow-up:
nothing re-reads them by procedure.
