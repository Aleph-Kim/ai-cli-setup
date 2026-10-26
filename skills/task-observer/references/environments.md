# Environments and Activation Setup

Load triggers: anchoring, pinning, re-pinning or diagnosing a shard of the workspace; setting up or diagnosing activation (instruction block, hooks, activation config); placing the session-start probe in the first batched call; a permission or classifier denial of a log write; a mode that forbids every write by design; after a compaction or resume; the first-run backfill

Load this for setup questions or compaction/resume behaviour.

## Contents

- Recommended activation setup
  - The activation block
  - Anchoring the workspace
  - A session-start hook (Claude Code and similar harnesses)
  - A stop hook — the per-task backstop as a harness event
  - A pre-tool hook — the only write path as a barrier
  - A skill-file write gate — the skill-authoring load as a harness event
  - Verify activation in a NEW session — the installing session cannot prove it
  - Activation config — late, intermittent, and why the guard cannot live inside it
  - The probe rides inside the first batched call
  - Install-layout hazards — three ways a skill silently stops existing
  - Other agent tools that read the same skills folder
  - Two harness behaviours that block the protocol rather than break it
  - If CLAUDE.md (or the equivalent config) is governance-protected
  - A third denial class: an automated content classifier
  - A mode that forbids every write by design
  - A delegated setup step is not done until you have observed it
- A skills directory managed by a repository or dotfile tool
- First-run backfill
- Skill files
- Compaction behaviour
- User-facing documentation

## Recommended activation setup

Four activation tiers exist, and only the strongest is enforced. Pick
knowingly; do not assume any of the middle ones is a guarantee.

1. **Description matching** (weakest). The skill's frontmatter description
   competes with every other skill's for relevance to the opening message.
   It loses most often on short, tool-using requests that read like
   questions ("list the files in this repo"), on sessions that open small
   and grow, and whenever a domain skill matches the opening message
   strongly. This is the only tier that survives an unreadable config
   file without a hook, which is why the description itself carries a
   session-start trigger.
2. **User-level instructions** (folder-independent, still probabilistic).
   The user-level instruction file every session loads, whichever folder
   it starts in — in Claude Code, `~/.claude/CLAUDE.md`. This is the
   right home for a one-line probe-then-load trigger — "the session's
   first tool call is one batched call that contains an `ls` of the
   workspace path AND the loads of <the session-start skills, by name:
   task-observer, …>; never state whether the workspace exists without
   that probe" (why the wording is about the call's content, not its
   order: "The probe rides inside the first batched call" below) —
   because a project config file cannot fire in a session started
   outside the project. Verify the channel once by asking a session
   started elsewhere to quote it; a line that does not reach the agent is
   not a tier.
3. **Configuration instruction** (better, still probabilistic). A project
   CLAUDE.md or project-instruction block, shown below. Empirically
   skippable under the same conditions as tier 1, and silently absent
   when the file it lives in is not in context (a session started
   outside the project). An environment flag saying a folder is in place
   is a hint; only a probe of the path in the same turn is evidence.
4. **Harness hook** (the only enforced option). A session-start hook that
   injects the instruction — and ideally the log state — into context on
   every session, e.g. Claude Code's `SessionStart` hook returning
   `hookSpecificOutput.additionalContext`. Even a hook can only inject a
   prompt; choosing to invoke a skill remains a model decision.

**Porting this skill to another host asks the inverse question first:
what is the destination's activation model, and can it express an
always-on artefact?** This skill is ambient — present before the failure
it watches for, with no moment at which a user asks for it — and a pack
that routes purely on description cannot express that: there is no
occasion to request a skill whose job is to notice that the skill in use
was wrong, and a description written for one collides with the router's
own. The artefact is then carried by whatever is already ambient there —
a hook, an injected meta-document, a config file — or not carried at all;
a port that sends the content and leaves the activation to the host has
sent half of it, and the half left behind is the half that made it work.

**Word the trigger mechanically, not judgementally.** "Task-oriented
session" asks the agent to classify the session at its first turn, before
it knows how the session will develop, and short factual-looking requests
get classified out. The block below keys on tool use instead: any turn
that will involve a tool call counts. And activation must precede
*planning*, not merely execution — where a workflow proposes a plan for
approval first, a plan written without the relevant skills carries
uninformed decisions past the review gate, and approval locks them in.
Load skills before exploring, researching or drafting the plan: both,
skill first.

**The block has a per-session cost, paid knowingly.** Every session it
covers loads SKILL.md in full (bounded by `core_max_lines` in its
frontmatter; the references load on demand) and runs the Session Start
Protocol, whether or not the session logs anything. Narrowing that scope
is the adopter's trade, made in their own config, never the agent's
judgement of an opening message. A narrowed rule carries its re-trigger
or it loses coverage exactly where coverage matters: *if a skipped session
turns into multi-step work, or the user corrects how you work, invoke the
skill at that moment, before the next write.*

**Select on the decision, not on the artefact.** Selection and loading are
separate steps, and the selection step fails in its own way: it runs
against what the user handed over — files to read, a link, a screenshot —
so every skill whose description names a *subject* is missed whenever the
request's surface form is an activity no skill claims. Before answering,
name the DECISION the user is making and match the installed descriptions
against that ("the deliverable is advice about X" → load the skill whose
description names X), even though the request arrived as a document to
review. The high-risk shape is an attachment plus an open question — "here
are two files, what do you think?" — which presents as a reading task and
hides its own domain while the session-start skills load correctly: the
mechanism works and still selects the wrong set, silently, because a
skill that never loads cannot announce that it was relevant.

### The activation block

```text
(task-observer activation block — template of v3.8.0-local.1)
Before the first tool call of any session — and before writing or
proposing a plan, not merely before executing one — invoke the
task-observer skill AND execute its Session Start Protocol (storage
check, frontmatter scan, review trigger). Loading the skill and running
the protocol are separate steps; a session that loads the file and stops
has activated nothing. Any turn that will involve a tool call counts; do
not classify the session as "too simple" from its opening message.
A step you did not run is reported before the answer, in one line — never
after it, where it reads as a suggestion. If the skill does not resolve on
this turn, say which probe told you so (the skill listing, or the skill
directory on disk), re-check the listing on every later turn that makes a
tool call, and run the protocol the first time it resolves — a "not
installed" verdict holds for one turn.

Select skills on the DECISION the request is about, not on the artefact it
arrived as. Name what the user is deciding, then match the installed skill
descriptions against that — a request handed over as a file to review
still needs the skill whose description names its subject.

After completing each task, list the observation records written this
session in the same turn and report a one-line summary from that listing
(ids and titles, or "none logged and why") — never from memory of
writing them. This is the activation backstop: it forces a look at the log,
so a session that silently skipped the protocol is discovered at the
first task boundary instead of never.

Loading a skill is not complete until you have queried the observation
log for OPEN observations naming it and read their bodies:
  find "[ABSOLUTE PATH]/skill-observations/observation-log" -maxdepth 1 \
    -name '*.md' -exec grep -l -E "^(skill|target_file):.*<skill-name>" {} +
(<skill-name> is the bare name: drop a plugin: prefix, up to the last
colon. A qualified pattern misses every entry filed under the bare name
and reports a clean zero; the bare one matches both spellings. For an
agent definition or instructions file it is the file name, which the
target_file: field carries by any path.)
(Use find, not a bare *.md glob: under zsh an unmatched glob aborts the
whole block, and on an empty log it is unmatched in every session.)
Apply their insights to the current work — meaning: let them change what
you do in THIS task. Editing the skill file, or writing the rule into any
other file a later session reads, is acting on the observation and waits
for the review. See "Log, don't act" in SKILL.md: the test is whether the
action leaves a durable change outside the observation log. Run this at every skill load, however many skills load
in one session. The session-start scan does not cover it: that is a
frontmatter sweep over every observation at session start, this is a
body-level lookup for one skill at the moment its rules are applied.

The converse holds too: the grep, and any checkpoint line recording the
load, run only in the same batch as the Skill invocation, and take the
skill name from a load that has actually happened — never from a list of
skills you built to load. A checkpoint line written without the load is a
false record. Before writing to any file a skill reads at run time (a
state file), load that skill: a state file that describes itself is not a
substitute for the skill that owns it.

Where scripts run, the lookup and its checkpoint line are one command:
  bash "<skill directory>/scripts/skill-load.sh" "[ABSOLUTE PATH]" <skill-name>
The Skill invocation and that call are ONE batch — emit them together,
one call per skill loaded, never the call in a later batch. On a first
run the log does not exist yet (step 1 creates it): the call says so and
exits 0 with no checkpoint line; re-run it once per skill loaded in that
batch after the Workspace creation command.

The task-observer workspace for this project is:
  [ABSOLUTE PATH]
It does not exist until the first session creates it: a failed probe whose
parent resolves and is writable is a first run — run Workspace creation,
then re-run the lookup above once per skill loaded in that batch (on the
first batch it finds no log and writes no checkpoint line; that is expected).
Every path the skill uses derives from that root and nothing else:
  [ABSOLUTE PATH]/skill-observations/observation-log/   (the log)
  [ABSOLUTE PATH]/skill-observations/cross-cutting-principles.md
Never resolve any of them from the current working
directory — a cwd inside an ephemeral checkout (a git worktree, a temporary
clone) is torn down and takes the log with it. Never place the workspace
inside a skills-discovery directory or any path linked into one. If this
environment mints a separate project identity per checkout, or more than
one agent works this project, the pinned path above is the single shared
location; do not derive one per session, tool or project.

The user's repositories live under:
  [PROJECTS ROOT]
(the root the sibling check sweeps before declaring a skill absent;
observation-log.md, "Skill families and the sibling check").

A subagent dispatched by a session that already runs this protocol does
not run it again and does not write to the log. The controller observes,
because only it sees the whole task and its review; a subagent that
notices something worth logging says so in its final report, and the
controller writes it, running the id snippet per write. A start-up rule
in a project file reaches every agent the project ever dispatches.
Before briefing a delegate under an agent definition or instructions
file, run the lookup for that file's name; its open entries shape the
brief.

An observation file comes into being only through
  bash "<skill directory>/scripts/new-observation.sh" <slug> "[ABSOLUTE PATH]"
which prints the path to write into. Never by copying another file's
header or counting a listing — including on the turn after a
compaction, when the skill body is out of context.
```

`<skill directory>` is the installed skill's own directory (the one
holding `SKILL.md`), substituted at install exactly like
`[ABSOLUTE PATH]`; where the harness cannot run a script, drop the two
script paragraphs and keep the rest — the inline id snippet in SKILL.md is
then the write path, and the `find … grep` above is the lookup, with its
checkpoint line written by hand in the same batch.

**The first line is the template's stamp, and an upgrade does not move
it.** The block lives in the user's instruction file, outside the skill
directory, so upgrading the skill in place leaves it on whatever template it was
copied from, and a presence check cannot tell a current block from an old
one: every paragraph added since is missing from that install without any
signal. The stamp and the frontmatter `version:` change together whenever the
block's text changes, since two texts under one stamp read as the same
block to step 4. Session Start
step 4 compares the stamp with this version's: a block whose stamp
is older, or has none, is reported in one line with the paragraphs it
lacks, and the current block is offered whole — the file is never
rewritten unasked. On every upgrade, diff the installed block against
this template; a block copied without its stamp line is read as unstamped.

### Anchoring the workspace

SKILL.md's `[workspace folder]` definition states the rule; this is where
to pin it, how a stable anchor still goes plural, and which plural case is
legitimate.

Fill in the path when installing. Pinning turns anchoring into a one-time
decision instead of one the agent re-litigates every session with a fresh
chance to get it wrong. Pin the ROOT, and list the derived paths: a pin
that names only the observation-log directory — the place split-brain was
first noticed — leaves the principles file and the review records to be
re-derived by every session, and parallel sessions resolve
them plausibly and differently. Where the environment provides a managed persistence directory
under the project identity (a memory directory it loads every session),
that directory and the identity root are both "stable"; anchor inside the
managed directory when one exists, otherwise on the identity root — never
both.

**Scope matches installation scope** (SKILL.md, `[workspace folder]`). A
stable anchor can still be plural — in Claude Code the identity is derived from the
directory the session starts in, so per-subfolder habits shard the log
into several stable anchors that each look like the only one. Decide the
scope once, at install, and pin it. Several logs over the same installed skills are shards:
consolidate them ("Before creating a log, search for one", below).

**Stable is not the same as always available.** A folder in a synced or
network drive passes every test above — absolute, outside any checkout,
the same path every day — and still fails the one a session start needs:
when the drive is not mounted, the log is unreadable and a hook script
stored there does not resolve, so a hook registered to fail quietly
starts the session with no activation and no error. Before pinning, ask
two questions. Is this storage mounted every time a session starts on
this machine, offline and before the sync client has started included?
Is it the user's own, rather than an organisation's that can unmount,
retain or audit it? Unless both answers are yes, propose a local folder
under the user's home directory, and carry the log between machines by
an explicit copy to the user's own storage or a repository
(`observation-log.md`, "When the workspace is under version control",
for the two-install case), not through a live-synced directory. The user decides; the
questions are asked before the pin is written, not after the first
missed session.

**A session started without a project folder has no stable project
identity.** In a desktop app that runs such a session in a per-session
scratch directory (the tell is `scratch-workspaces/` or
`scratch-<date>-<hash>` in the cwd), the project identity derived from
that directory is new every session, so a log anchored on
`~/.claude/projects/<project-id>/` survives on disk and is never read
again: its open entries are never applied at session start and never
reach a review. Treat the scratch directory as an ephemeral path
(SKILL.md, Session Start step 1): anchor on the pinned path if one
exists, otherwise on the user-scope workspace
(`~/.claude/skill-observations/`, the path skills installed at user scope
need anyway), and name the anchor in the start-up lines. Logs already
written under scratch-derived identities are shards: consolidate their
open entries as below.

**The fork rule as usually stated describes the harmless case.** "A second
**empty** log beside a populated one is a silent fork" — but an empty log
announces itself: the first scan returns nothing, and nobody trusts a
backlog of zero. The damaging fork is the one that has accumulated its own
entries. From inside it looks exactly like a working log: the scan returns
files, the review finds work, every instrument reports health. Nothing in
it can reveal that it is a shard.

Pinning does not settle it: a pin governs the sessions that read it, not
one that resolved its anchor before the pin or by another route.

So the detection has to be positive, and it is nearly free: at the end of
the session-start scan the agent is already holding the `skill:` values of
every entry. A log whose targets are overwhelmingly **user-scope** skills,
while the log itself sits under a **per-project** path, has already
declared the mismatch — two `ls` and a comparison. Run it when the anchor
is per-project and the targets are not; report the candidate shard to the user
rather than consolidating on your own judgement.

**The session-start scan lists the neighbours on every run.** One line of
the scan (`scripts/session-start-scan.sh`) finds every
`skill-observations/observation-log/` up to three levels under the
pinned root's parent and prints each with its file count — `logs under
the parent (…): /a/proj=157  /a/other=19`. One entry is the ordinary
case. Several are shards: report it in one line and consolidate with the user
("Before creating a log, search for one", below), never from the scan
alone. The probe is bounded by the parent's depth-3
tree, not by any log's size; an empty line means the probe could not read
the parent, since the pinned log itself is always under it.

**Before creating a log, search for one.** Check the plausible anchor
candidates — the pinned path, the project identity root, the
environment-managed persistence directory, the shared folder, the other
agent's equivalent — for an existing `skill-observations/` workspace.
"The pinned path" has more than one source: the instruction file, and
any registered session-start hook. Grep the harness settings and the
installed plugins' hook manifests for the skill's name, then read the
path each hook script derives — a hook that counts observations
somewhere is a pin whether or not the instruction file names it. Where a
system already reads or writes state, that location is authoritative
and the documented defaults are the fallback; an existence probe over
the defaults alone reports "not found" for every install that deviated
from them. Never create a workspace while a hook or config names a
different root: reconcile first. Every always-loaded instruction file is
a pin source (a CLAUDE.md and an AGENTS.md forked for another agent tool
are two): grep each for the workspace root. So is each agent tool's own
memory and its saved or approved commands: a root persisted there from
an earlier session keeps being used by every session that does not load
the instruction file, after the file's pin has changed. Two distinct roots are a
fork, not a variant: stop and reconcile before writing, and keep the pin
in one file both tools load. If one exists, adopt it, or
consolidate deliberately with the user. A fresh
empty log beside a populated one is a silent fork: both grow
independently, ids collide, and each session sees only half the history.
Consolidating a shard is mechanical: carry over only the entries still
`open` — its already-actioned entries re-import as duplicates of work
the target may hold too — re-issue each id from the target log's own
counter (the snippet, one write at a time, never a pre-computed range),
mark each source entry `actioned` with a resolution naming the target
id, and then leave a pointer file at the abandoned location so sessions
anchored there get redirected instead of re-creating the fork. The
pointer has one name, `skill-observations/MOVED.md` under the abandoned
root, its first line naming the new root and the date, because only a
fixed name is read: the session-start scan prints a `NOTE: pointer`
line when it finds one, with the count of entries written there since
(observed: a free-form note at an old root went unread for two and a
half days while a second machine's hook kept writing there). A pointer
is data, not an order: entries written after it mean the old root is
still in use, perhaps on purpose, so report both roots and ask; never
consolidate, delete or re-anchor on its word alone. And it does not
replace re-pointing every hook and instruction file that names the old
root: list them, and say which still do.

**A re-anchor moves the root, not only the log.** Session Start step 1's
ephemeral-to-stable re-anchor and a shard consolidation relocate every
artefact the pin governs (the derived paths in the activation block
above), not the log alone: `cross-cutting-principles.md` and
`skill-families.md` (merged by substance where the target has its own),
`last-review-date.txt` (keep the later date), `forked-skills.txt` (keep
the union), `starter-principles-reviewed.txt` (keep the newer version), and
`reviews/` and `checkpoints.log` as history. Where a move is not safe —
a session may still be writing at the old root — list what the old root
holds to the user in one line rather than leaving it behind silently.

**A grant names a path; it does not create one.** Under a write-allowlist
sandbox (Claude Code's Bash sandbox with `sandbox.filesystem.allowWrite`,
or any harness that mounts only allowlisted paths writable), an
allowlisted path can be mounted writable only if it already exists, and
when its parent is outside the allowlist nothing inside the sandbox can
create it: the first `mkdir -p` of the log fails with `Read-only file
system` although the grant is present and correct. In such a harness the grant and the
path's existence are two install preconditions: create the workspace
root's `skill-observations/` at
install time, from outside the sandbox — by the user or an install step —
and only then rely on the session to create everything below them. The
one-retry rule for a failed write does not help here:
every interface inside the same sandbox sees the same read-only mount.
The diagnosis at the moment of failure is in `observation-log.md`
("Workspace creation").

**Config detection (once per session):** with filesystem access, check the
workspace root's CLAUDE.md (or equivalent) for a task-observer activation
instruction — suggest adding it if absent. **Suggest; do not create.** If
no config file exists at all, offer to add one and let the user say yes:
creating a tracked project file changes every future session's behaviour,
and the governance-protected fallback below exists precisely because
writing to a shared config is not a free action.
Without filesystem access, check the system prompt / project
instructions and suggest the user add the instruction there. Keep the
suggestion to a sentence or two. The block above is the propagated
artefact: suggest it whole, including the anchoring paragraph, because
constraints that live only in SKILL.md arrive after the decision they were
meant to govern.

**Load is not activation.** The failure the block's wording guards
against: the agent loads the skill per the
config instruction, then stops — the Session Start Protocol (log files,
scan, review trigger) never runs, and nothing surfaces the omission
because a loaded-but-inert skill looks identical to an active one from
the user's side. Hence the two belts above: the
instruction demands the protocol by name, not just the load, and the
post-task summary line makes silent inactivity visible at the first
task boundary. If you adopt only one line of the block, adopt the
post-task check.

That check is prose in the same file as the rule it guards, and it fails
with it: whatever made a session skip the block's first paragraph makes it
skip the third. A backstop written in the medium of the rule it
guards is one layer, not two. The second layer has to hang on an event
the harness raises, not on the agent re-reading its instructions: where
the harness offers a stop or turn-end hook, the objective check is cheap —
the session used tools, and nothing under `observation-log/` or
`checkpoints.log` has been written since it started — block once, with a
one-line instruction, and stay silent otherwise. Classify each
enforcement layer by what it needs in order to function: a filesystem
write survives into any session type, a prose reminder survives only
while the prose is being acted on.

A third belt: the scan's `checkpoints.log` line (`observation-log.md`,
"The scan ends in a write, not only a print").
Treat *loaded but not run* as a distinct failure cause, alongside the
skill being absent, truncated, or present and skipped: it is the likeliest
of the four, precisely because the load's visible success stands in for
the protocol's invisible omission, and the aggravating condition is the
same one that produces a skipped load — an opening message small enough
that a full startup protocol feels disproportionate to it.

**Anti-pattern:** don't chain activation through another skill — load
task-observer and related skills independently from configuration; a broken
chain silences all observation activity.

### A session-start hook (Claude Code and similar harnesses)

Capture is hard-enforced by checkpoints hooked onto tool calls; the review
trigger in the Session Start Protocol is a soft step — read a file, compare
a date — and it is skipped the same way activation is, self-concealingly:
the log looks healthy and growing, and the only artefact recording the
miss is a file reading `never` that nobody reads. Treat "is the review
trigger structurally enforced?" as an install-completeness check, and
where the harness offers a session-start hook, have it compute the state
and inject it rather than asking the agent to go and look:

```bash
#!/bin/sh
# SessionStart hook: inject activation + review state as additionalContext.
d="$OBS_WORKSPACE/skill-observations"      # the pinned absolute path
open=$(find "$d/observation-log" -maxdepth 1 -name '*.md' -exec grep -l '^status: open$' {} + 2>/dev/null | wc -l | tr -d ' ')
last=$(tr -d '\r' 2>/dev/null < "$d/last-review-date.txt"); last=${last:-never}   # a CRLF file must not carry \r into the JSON
msg="Make the first tool call of this session one batched call that both lists the task-observer workspace ($OBS_WORKSPACE) and invokes the task-observer skill; then run its Session Start Protocol. Observation files are created only by scripts/new-observation.sh in the skill directory, never by copying a header."
msg="$msg $open open observations in $d; last review: $last."   # always, zero included: a mispinned path reads 0 too
if [ "$open" -gt 0 ]; then
  cutoff=$(date -d '7 days ago' +%F 2>/dev/null || date -v-7d +%F)   # GNU, then BSD/macOS
  case "$last" in
    (never) msg="$msg Offer the review." ;;
    (*) [ "$(printf '%s\n%s\n' "$last" "$cutoff" | sort | head -1)" = "$last" ] && msg="$msg Offer the review." ;;
  esac
fi
msg=$(printf '%s' "$msg" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\000-\037')   # JSON string: escape \ and ", drop control characters
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$msg"
```

The message names the resolved workspace and the whole first batch,
because it is the one pre-skill text the harness delivers on turn 1
("The probe rides inside the first batched call", below): a message that
only says "invoke the skill" leaves the probe to a skill not yet read,
and a tool whose sessions resolve the root another way keeps writing to
its own log while the injected count, read from the shared one, looks
healthy. A count of zero is printed, never suppressed, with the path it
was read from: the hook is an instrument over the log and gets the same
guard as every scan, and a message that drops the count at zero makes a
mispinned workspace and a clean backlog read the same. Only the offer is
gated on the count. The path is interpolated into a JSON string, so the
last step escapes the whole message: a backslash or a `"` in a folder
name otherwise produces output that does not parse, and a
hook whose output does not parse injects nothing.

The count is of files whose `status` field reads `open` — not of files
in the directory. Resolved entries deliberately stay in `observation-log/`
until the day after they were resolved (the grace period lives in the
file, not in session memory), and parked entries are decided and out of
the work queue, so a raw file count overstates the backlog by every entry
the last review just closed, for a day, in every session. Compare dates
without `<` in `[ ]`: ISO dates sort lexically, so
`[ "$(printf '%s\n%s\n' "$last" "$cutoff" | sort | head -1)" = "$last" ]`
is true when `$last` is not later than `$cutoff`, in every POSIX shell
(`\<` is a bash/ksh extension that zsh rejects and `sh` does not know).
Two details that matter when building one: `grep -c` exits 1
on zero matches while still printing `0`, so `$(grep -c … || echo 0)`
yields two values — capture the output and ignore the exit code; and prove
the reminder branch fires by running the hook against fixtures at `never`,
30 days stale, 2 days stale and an empty log, confirming the third stays
silent and the fourth still prints "0 open observations in <path>" — a
nag that never fires and one correctly silent look identical otherwise.

### A stop hook — the per-task backstop as a harness event

The per-task backstop fails with the block it lives in (above): a session
that skipped the protocol skipped the backstop at every task boundary too.
Where the harness has a stop event, run the check there instead: *has this session
used tools, and has anything under `observation-log/` or `checkpoints.log`
been written since it started?* If not, block the stop once per session
with a one-line instruction; stay silent for conversation, for a session
that already wrote, for a second block in a row, and when the log cannot
be read. Node, no dependencies; substitute `[ABSOLUTE PATH]` as elsewhere:

```js
// Stop hook: the per-task backstop as a harness event instead of prose.
const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const MIN_TOOL_USES = 3; // below this the turn is conversation, not work
const base = path.join('[ABSOLUTE PATH]', 'skill-observations'); // the pinned workspace
const block = (reason) => { fs.writeFileSync(marker, new Date().toISOString()); console.log(JSON.stringify({ decision: 'block', reason })); process.exit(0); };

let input = {};
try { input = JSON.parse(fs.readFileSync(0, 'utf8') || '{}'); } catch { process.exit(0); }
if (input.stop_hook_active) process.exit(0);            // never chain a second block
const session = String(input.session_id || '').replace(/[^A-Za-z0-9_-]/g, '');
const transcript = input.transcript_path;
if (!session || !transcript) process.exit(0);

const marker = path.join(os.tmpdir(), `task-observer-backstop-${session}`);
if (fs.existsSync(marker)) process.exit(0);             // once per session

let started = 0, toolUses;
try {
  const st = fs.statSync(transcript), text = fs.readFileSync(transcript, 'utf8');
  toolUses = (text.match(/"type":\s*"tool_use"/g) || []).length;
  // Birth time is 0 where the filesystem has none and equals ctime where the
  // platform substitutes it; either would make every file read as untouched
  // or touched. Fall back to the transcript's first timestamp.
  if (st.birthtimeMs > 0 && st.birthtimeMs < st.ctimeMs) started = st.birthtimeMs;
  else { const m = text.match(/"timestamp":\s*"([^"]+)"/); if (m) started = Date.parse(m[1]) || 0; }
} catch { process.exit(0); }
if (toolUses < MIN_TOOL_USES) process.exit(0);

if (!(started > 0)) block('task-observer backstop: cannot tell when this session started (no birth time, no ' +
  'transcript timestamp), so it cannot check the log. Check by hand that this session wrote an observation ' +
  'or a checkpoints.log line, and report the one-line summary. Fires once per session.');

const files = [path.join(base, 'checkpoints.log')];
try {
  for (const n of fs.readdirSync(path.join(base, 'observation-log')))
    if (n.endsWith('.md')) files.push(path.join(base, 'observation-log', n));
} catch { process.exit(0); }                             // unreachable log: stay silent
const touched = files.some((f) => { try { return fs.statSync(f).mtimeMs > started; } catch { return false; } });
if (touched) process.exit(0);

block('task-observer backstop: this session used tools but wrote no observation file and no checkpoint line. ' +
  'If the skill was never invoked, invoke it now; then write pending observations or append a ' +
  '"no observations" line to checkpoints.log, and report the one-line summary. Fires once per session.');
```

**The session's start time is the fragile input.** A transcript's birth
time is `0` on filesystems that do not record one, and some platforms
return the change time in its place, which moves on every append; either
makes the comparison meaningless, and the first makes the hook
permanently silent. So birth time counts only when it is non-zero and
earlier than the change time; otherwise the hook reads the first
`"timestamp"` in the transcript, and where neither exists it blocks once
with a request to check by hand rather than falling silent.

Its known limits: it compares modification times, so a parallel session
writing to the same log reads as this session's write (a missed block,
never a false one); it fires for the main agent only, so a subagent —
which by the activation block writes nothing — is never blocked; and
like every trigger, it is armed only once it has matched the
real event — run it against a transcript with tool calls and no write,
then against the same with a checkpoint line appended and the transcript
appended to after it (a start time read from the change time blocks that
one), before trusting either outcome.

### A pre-tool hook — the only write path as a barrier

"Where a helper can run, `scripts/new-observation.sh` is the only write
path" is a rule, and a rule broken twice needs a barrier (SKILL.md, the
second-violation rule): a direct create with the editing tool skips the
id derivation and the prefix collision guard, and two ids each used twice
are what that looks like afterwards. The helper creates the file — a
frontmatter skeleton carrying the id — with a `noclobber` create before
any body is written, so a pre-tool hook can refuse every editing-tool
write that would CREATE a Markdown file in the log, and the fill of the
skeleton the helper made passes untouched. Node, no dependencies; substitute `[ABSOLUTE PATH]` as
elsewhere, and register it for the editing tool's write call (in Claude
Code, matcher `Write`) with the interpreter in the command, as above:

```js
// PreToolUse hook (matcher "Write"): refuse an editing-tool write that would
// CREATE a Markdown file in the observation log. The helper's noclobber create
// makes the path exist before the body is written, so its own write passes.
const fs = require('node:fs'), path = require('node:path');
let log;
try { log = fs.realpathSync(path.join('[ABSOLUTE PATH]', 'skill-observations', 'observation-log')); } catch { process.exit(0); }
let input = {};
try { input = JSON.parse(fs.readFileSync(0, 'utf8') || '{}'); } catch { process.exit(0); }
const p = input.tool_input && input.tool_input.file_path;
if (typeof p !== 'string' || !p.endsWith('.md') || fs.existsSync(p)) process.exit(0); // existing: the helper's create, or an edit
let dir;
try { dir = fs.realpathSync(path.dirname(path.resolve(p))); } catch { process.exit(0); }
if (dir !== log && dir !== path.join(log, 'archive')) process.exit(0);
process.stderr.write('task-observer: observation files are created only by scripts/new-observation.sh, ' +
  'which derives the id and refuses a collision. Run it, then write the body into the path it prints.\n');
process.exit(2);
```

Exit status 2 refuses the call and hands the message to the agent; every
other path exits 0, so an unreadable log or malformed input fails open
rather than blocking ordinary work. Its known limit: it sees the editing
tool only, so a shell redirect (`cat > …/0013-x.md`) still bypasses it,
and a command-text guard for that has the false positives described under
"Two harness behaviours that block the protocol rather than break it".
Arm it like any trigger: a direct create of a new `NNNN-slug.md` must be
refused, and a write into the path the helper just printed must pass.

### A skill-file write gate — the skill-authoring load as a harness event

The pointer to `references/skill-authoring.md` fires on an episode the
agent has to recognise, and setup or documentation work produces a
`SKILL.md` without feeling like skill creation. The file being written is
checkable where the episode is not. Where the harness has pre- and
post-tool events, refuse a write to a skill file until the reference has
been read in the same session; a context-only pre-tool hook is not enough,
because its text reaches the model after the write it was meant to steer.
Node, no dependencies; one script wired twice — PreToolUse on
`Write|Edit|MultiEdit`, PostToolUse on `Read`:

```js
// Skill-file write gate: deny a write to a skill file until the skill-authoring
// reference has been read in this session. One script, two hook entries:
// PreToolUse on Write|Edit|MultiEdit, PostToolUse on Read.
const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
let input = {};
try { input = JSON.parse(fs.readFileSync(0, 'utf8') || '{}'); } catch { process.exit(0); }
const session = String(input.session_id || '').replace(/[^A-Za-z0-9_-]/g, '');
const file = String((input.tool_input || {}).file_path || '').replace(/\\/g, '/');
if (!session || !file) process.exit(0);
const marker = path.join(os.tmpdir(), `task-observer-authoring-${session}`);
if (input.hook_event_name === 'PostToolUse') {          // the Read half: record the read
  if (/\/references\/skill-authoring\.md$/.test(file)) fs.writeFileSync(marker, file);
  process.exit(0);
}
const skillFile = /(^|\/)SKILL\.md$/.test(file) || /\/skills\/[^/]+\//.test(file)
  || /\/skill-updates\/[^/]+\/[^/]+\//.test(file);     // a staged copy, not PENDING.md
if (!skillFile || fs.existsSync(marker)) process.exit(0);
console.log(JSON.stringify({ hookSpecificOutput: { hookEventName: 'PreToolUse', permissionDecision: 'deny',
  permissionDecisionReason: 'Read references/skill-authoring.md (task-observer skill) in this session ' +
    'before writing a skill file; this write is allowed once that Read has run.' } }));
```

Its limits: it sees the file tools only, so a skill file written through
a shell command passes; the marker outlives a compaction that drops the
reference from context (re-read it after one, as the Session Start
Protocol already says); and like every trigger it is armed only once it
has matched the real event — run a `SKILL.md` write before the read
(denied), then a read of the reference and the same write (allowed).

### Verify activation in a NEW session — the installing session cannot prove it

The config file is read at session start, so an instruction written
mid-session takes effect only on the next one; and in a harness that
hot-loads a newly installed skill, the skill being callable right after
install proves nothing about activation — it was invoked by hand. The
installing session therefore sees everything pass (files complete, skill
listed, protocol ran, hook emits valid JSON) while the one thing that
matters is untested, and the tempting close is "installed and tested".
Report the install as **activation unverified** until a fresh session has
been seen invoking the skill on its own, and name the check: the next
session opens with ordinary work that names neither the skill, the log
nor the check, and only afterwards is the skill confirmed invoked (not
merely listed) with the Session Start Protocol run — by evidence of
invocation, not by a side effect that a hand invocation would also
produce. If the environment offers no way to start a fresh session from
the installing one (a GUI-only harness, no CLI), hand the check to the
user: start the next session with unrelated work, then look at the
`session-start scan` line in `checkpoints.log` or at the transcript; an
unverifiable step never closes silently as "tested". A pass from a
session whose first request named the skill is a hand invocation and is
discarded, not counted (`skill-authoring.md`, "Trial design").

The runtime cannot diagnose its own absence — Session Start step 4 only
runs once activation has already succeeded — so the external diagnostic
is the one that catches a skipped install step: **if
`skill-observations/observation-log/` does not exist after a few sessions
of tool-using work, activation never happened**; check the activation
block in the config, or install the hook. The directory existing proves
only that one session ran: a first session loaded by hand, or by a lucky
description match, writes entries and the trace, and the install then
goes quiet. So the diagnostic has a second half: **the last
`session-start scan` line in `skill-observations/checkpoints.log` is the
last session that ran the protocol** — days old while work went on means
activation is not running, whatever the log holds. The scan prints a
`GAP:` line when that date is 7 or more days old, which helps only the
session that is activated after the gap; the dated line is the check
anyone can run from outside. The README carries the same diagnostic for
users who never read this file.

**Another skill's session-start output is a false positive for
activation.** A harness that injects a different always-on skill's
content at session start makes the session look skill-governed while
this skill's activation does not exist (observed: a full working day of
real work with the skill installed beside four others, no log and no
activation block). Count only evidence of THIS skill: its own
invocation, the protocol's trace in `checkpoints.log`, or the
`observation-log/` it created. An install is not finished until an
artefact outside the skill proves it: create the workspace AND write the
activation, then print what was written and where. Where the activation
cannot be written, the install does not succeed silently: report it as
incomplete and hand over the block to paste.

### Activation config — late, intermittent, and why the guard cannot live inside it

SKILL.md step 1 carries the instruction (on turn 1, load the session-start
skills directly rather than assuming the config did, and read the config
yourself if the mount resolves but its content is not in context). This is
the reasoning behind it, and the reason that instruction is only the backup.

In some hosted or bridged session types the activation config — a project
instruction file, a session-start hook's context — does not reach context
until the **second** user turn, while the workspace it lives in is already
mounted and probes clean. From inside turn 1 a config that is merely late is
indistinguishable from one that is absent, so a whole substantive turn can
run with no session-start skill loaded. **A config delivered on a later turn
than the work it governs is equivalent to an absent one for that work.**

It has also been seen **intermittent** rather than merely late: present for
turns 2 and 3 of a bridged session, then reported as no longer present at
turn 4, with no change in the workspace link and nothing the session did to
cause it. So a rule anchored on "once it arrives it stays" fails the same way
a rule anchored on "it arrives first" does. Do not treat an earlier turn's
config as still in force.

**The skill listing lags the same way, and an absence verdict expires the
same way.** The instruction can be present and fire on a turn where the
skill it names does not yet resolve against the harness's own listing of
invocable skills — right after the instruction was added mid-session, or
in a harness that builds its available-skill list once near session
start. The honest response on that turn is a disk check and "not
installed", and that verdict is true only for the turn it was made on;
nothing revisits it, so when the listing catches up every tool call in
between went unobserved and the earlier claim stands uncorrected. So a "not installed" verdict
names the probe it came from — the listing lookup, or a disk check of the
skill directory — because the two disagree exactly here, and it holds for
one turn: re-check the listing on each later turn that makes a tool call,
and run the Session Start Protocol in full the first time the skill
resolves. Like the guard below, this rule cannot live only in the skill
that failed to resolve; the line that carries it is in the activation
block.

The durable form: **a guard against an activation config failing to load
cannot live inside the thing that config loads.** The guard in SKILL.md step
1 is in `task-observer`, which is loaded *because* the config says to load
it — so on the turn where the config is missing, nothing puts that guard in
context either. By construction it cannot fire on turn 1.

The primary guard therefore belongs in the earliest channel verified present
on turn 1 — in most harnesses the user-level preferences or system-prompt
block, which is where the line

> then read the workspace config and follow it before any other work

goes. See the activation tiers above: that channel is tier 2 (user-level preferences), and the step-1
guard is the backup for turns 2+ and for sessions where the skill happens to
be loaded directly.

**Log the cause, not just the miss.** When a session-start load is skipped,
the fix depends on which of these it was: *absent* (config unreachable),
*present-but-not-yet-injected* (late — record the turn it arrived),
*present-but-not-yet-resolving* (the instruction fired and the skill was
not in the listing — record the turn it appeared), *present and skipped*
(attention), or *loaded-but-not-run* (the invocation succeeded and the
protocol inside it never executed). Only the first two are fixed by
changing the channel, and the third by re-checking the listing; the last
two are not environmental, and an environmental cause found first will
otherwise absorb the whole explanation.

### The probe rides inside the first batched call

The probe line can be present and correct on turn 1 and still not fire
first: the session's first tool call is a batch of `Skill` invocations,
and the probe rides in the second. The failure is detectable only in the
sessions where it costs nothing, and it costs everything in the session
where the folder is not there and the agent asserts that it is.

The cause is a contest for one slot: loading the session-start skills is
the one action that genuinely *is* prior to the work, so it recruits the
"before anything else" position the probe needs, and feels like
preparation rather than action. Stating the precedence more firmly does
not change that, because the load discharges the felt obligation.

So the rule is about the **content of the first call, not its order**: the
session's first tool call is a single batched call that contains the probe
— a listing of the pinned workspace path; the target is the test, not
the command's success — and any session-start skill loads ride in that same batch,
never in an earlier one. That removes the contest instead of adjudicating it, the
harness's parallel-call guidance already permits it, and it is checkable
after the fact from the transcript (an ordering rule between two "first"
actions is not). SKILL.md step 1 states it that way; the tier-2 preferences
line above is worded to match; the activation block's "before the first
tool call" is satisfied by the load riding *in* that call.

**The pre-skill tier's line names the complete batch, not only the
probe.** Whatever the harness reads before any skill — a Claude Code user-level
(global) CLAUDE.md, a session-start hook's injected text — carries the whole first batch: the
workspace probe AND the session-start skill loads, named, in one batched
call; the tier-2 line above is the template. The failure shape: a line naming only the probe
fires the probe and leaves the loads to a project config that arrives late
or intermittently, so the first batch carries the probe alone and the
skills load a batch later. The review's activation regression pass checks
for it (`weekly-review.md`, Step 1).

**A failed probe has three readings, and the parent tells them apart.**
The pinned path is absent on the first run of every install, because
nothing creates `skill-observations/` before the first session does; a
probe read as "not mounted" sends that run looking for a mount that was
never missing, and the log is never created at all. So a failed probe
is split before any branch is chosen, by one `ls` of the pinned path's
parent: it resolves and is writable → a first run: run "Workspace
creation" (`observation-log.md`) and continue; it resolves read-only → the
grant precondition above ("A grant names a path; it does not create
one"); it does not resolve → the pinned path is wrong or its drive is not
mounted: tell the user, and never create a log elsewhere. The per-skill lookups that rode in the probe's batch
ran against no log: after a first-run creation, re-run the lookup once
per skill loaded in that batch, so `checkpoints.log` holds the
`workspace: created=…` line followed by one `loaded` line per skill.

### Install-layout hazards — three ways a skill silently stops existing

Each of these leaves no error. The skill simply stops being offered, or an
activation tier stops firing, and the only symptom is that the Session Start
Protocol no longer runs — which is indistinguishable from a session where it
ran and found nothing.

**Skill discovery is exactly one level deep.** The host reads the skills
directory and looks for `<entry>/SKILL.md`. There is no recursive lookup. On
a library of any size the natural organising instinct is to group skills into
category folders — `skills/seo/`, `skills/clients/`, `skills/writing/` — and
doing so makes **every skill inside them cease to exist**: no error, no
notice, no change in behaviour except that the skills stop being offered.
The layout is not merely the happy path; it is the rule, and it does not
travel with the maintainer who reorganises six months later. Keep every
skill directly under the skills directory.

**A backup inside the skills directory registers as a rival skill.** The
obvious way to back a skill up before overwriting it —
`cp -r ~/.claude/skills/task-observer ~/.claude/skills/.task-observer-backup`
— puts a second copy where the host is looking. The leading dot does not
exclude it from discovery. The available-skills list then holds two entries
with near-identical descriptions, and the backup still advertises the OLD
version's trigger, including its session-start instruction. That defeats the
upgrade at the one activation tier that survives an unreachable config:
description matching now has two candidates competing for the same trigger,
one of them the file the upgrade just replaced. Back up **outside** the
skills directory. The same holds for any second copy the host loads — a
user-owned copy beside an account-synced one: the older copy is a second
writer in the old format (the scan's SPLIT STORE line is how it shows),
so name each copy's version when more than one resolves.

**A hook registered by script path dies when the exec bit goes.** The
docs' example reads most naturally as naming the script directly:

```json
{ "type": "command", "command": "'/path/to/hooks/task-observer-activation.sh'" }
```

Anything that rewrites file modes — a cloud-drive resync switching between
stream and mirror mode, a restore from an archive, a checkout on a
filesystem without permission bits — returns the file as mode 600, and the
hook then fails with "permission denied" on every session start with
nothing surfacing the error. Register the interpreter instead
(`"command": "bash '/path/to/hooks/…'"`), which does not depend on the exec
bit, and treat "the Session Start Protocol stopped running" as a prompt to
check the hook rather than the skill. The same silent death follows, with
the mode intact, when the script lives on a drive that is not mounted at
session start: keep hook scripts on local storage ("Anchoring the
workspace", "Stable is not the same as always available").

### Other agent tools that read the same skills folder

A second agent tool that lists the same skills directory shows the
description to its own model, and the description starts the skill by
itself — it carries the session-start trigger so that activation
survives an unreachable config file (tier 1 above). Removing the
activation block from that tool's instruction file does not keep the
skill off there. To keep it off, use that tool's own skill-permission or
skill-path setting, or stop sharing the folder. Where it does run, the
protocol's assumptions (the pin, the permission model, the hooks) do not
hold, and a log it writes is a shard ("Before creating a log, search for
one").

### Two harness behaviours that block the protocol rather than break it

**A command-shape guard can refuse a read-only call.** Some setups run a
pre-tool hook that inspects the literal command text for governed path
segments combined with a write indicator (`=`, `>`, `cp`, `mv`) and denies
the whole call when both appear anywhere in the string — regardless of
whether the path is actually being written to. Two consequences worth
knowing before diagnosing: a `cd` into a governed directory followed by a
read-only script call is denied even though nothing is written; and a
**blocked command merely quoted inside an observation body** can trip the
same guard when that body is written through a shell. Neither is a
permission problem with the destination. Where this bites, invoke the
script with an absolute path and no `cd`, and write observation bodies with
the editing tool rather than through a shell. A guard that refuses the
session-start scan itself is handled the same way — degrade to flat
commands, never skip the step (`observation-log.md`, "A refused snippet is
a degraded path, never a skipped step").

**A harness configuration change is not like a skill edit.** A
skill's `SKILL.md` is read by itself; a corrupted copy fails to parse
and nothing else is affected. A harness config file — `settings.json` with
its hook entries, deny-lists and protection rules — is read by the harness,
and it commonly carries **other protections alongside** the thing being
changed. The natural delivery shape for a config change is a fragment:
"here's the new key, add it under `hooks`". A hand-merge that goes wrong
there does not fail loudly; it produces a valid file with the other
protections missing.

So: deliver a config change as a **complete replacement file** built from
the user's current one, never as a fragment to splice in; state in one line
what else that file was carrying, so the user can verify it survived; and
where the harness supports it, prefer a separate file over editing a shared
one.

### If CLAUDE.md (or the equivalent config) is governance-protected

Some setups guard shared config files with hooks or file-protection rules
that deny agent edits. If an edit to the config is denied, never retry the
same edit blindly and never attempt to bypass the guard — a denial is the
governance system working as intended, and a silent skip is just as bad
(the user believes activation is set up when only description-level
matching is active). Surface the denial to the user and offer these
fallbacks, lightest first: (a) if the denial came from an interactive
permission system rather than a hard guard — the denial message offers an
approval path, names a permission rule, or otherwise indicates consent
would clear it — ask the user to approve a retry of the same edit; one
confirmation resolves it, and escalating past this step spends user effort
on something already recoverable; (b) ask the user to paste the activation
block into the file themselves; (c) if the user's environment provides its
own temporary-authorization mechanism (a marker file, an environment
variable, or similar), ask the user to authorize the edit through that
mechanism and revoke it afterwards; (d) where the platform supports
unguarded project-level instruction files, add the activation instruction
there instead. Branch on whether the denial is retryable-with-consent or
categorical: an interactive permission prompt is cleared by asking, a hook
or file-protection rule is not, and collapsing both into "hand the task
back to the user" is safe but consistently over-escalates. Never assume
unrestricted edit access to shared or governance-tracked config — many
setups gate exactly those files.

**The same shape applies to a blocked hook installation.** The hook
option from the same paragraph writes to the harness's settings file or
hooks directory, and those are gated at least as often as the config
file. A denied hook install follows the rules above unchanged: never
retry the same install through a different tool or path, never bypass,
surface the refusal, then fall back lightest first — ask for a retry if
the denial is retryable-with-consent; ask the user to add the hook entry
themselves (hand them the exact JSON or script); use a temporary
authorization mechanism if one exists; and if the hook cannot be
installed at all, fall back to the declarative config instruction, saying
plainly that the enforced tier is not in place and the probabilistic one
is. A hook that silently failed to install is worse than none: the user
believes the strongest tier is active.

### A third denial class: an automated content classifier

The fallbacks above branch on two kinds of denial: a hard guard (a
governance hook, a file-protection rule) and an interactive permission
prompt that one user approval clears. There is a third, and it behaves like
neither.

An automated content classifier can refuse the edit on the grounds that the
activation block is **third-party instruction text being written into a
user-scope config**, where it will steer every future session. Reported in
the field as `Instruction Poisoning`, on a fresh install into a global
Claude Code skills directory.

What follows from that:

- **The refusal is a valid outcome, and the user sees it first.** Stop.
  Quote the refusal and what it objected to, and explain the trade-off it
  points at: the block is always-on third-party instruction text in a
  global config, steering every future session, which is a real cost the
  user is entitled to weigh. Only then offer options.
- **Rewording does not help.** The objection is to provenance and always-on
  scope, not to the phrasing, so there is no lighter version to retry.
  Shortening the block and trying again is the obvious move; it fails, and
  it is a rewrite aimed at the classifier rather than at the user — don't
  make it.
- **The options, in this order.** (1) The user pastes the block into the
  config themselves (fallback (b) above): the decision then sits with the
  person whose config it is. (2) A permission-mode change, presented as
  the user's decision with its implications stated: it changes what the
  harness lets the agent do without asking for the rest of the session,
  and it takes the classifier out of this write without answering its
  objection. (3) Leave activation at the
  description layer and say plainly which tier is in place.
- **The objection follows the content, not the file.** A documentation
  page that quotes the activation text can be refused on the same grounds
  as the config edit. Report the setup as incomplete while either the
  config or its write-up has not landed, and do not reword either to get
  past the classifier.

**The ladder is not monotonic.** Tier 4 — the session-start hook, which this
file elsewhere calls the only enforced option — can be blocked *harder* than
tier 3, and for an unrelated reason. In the same install the hook was
refused as `Auto-Mode Bypass`: configuring a hook changes what the harness
executes automatically, which that permission mode withholds categorically
rather than on content. Writing the hook *script file* alone, wired to
nothing, was refused on the same grounds. So tiers 3 and 4 failed for
different reasons that happened to coincide, and the tier presented as the
robust fallback for a blocked config edit was the one held furthest out of
reach. Do not present the ladder to the user as "if 3 fails, 4 will work".

### A mode that forbids every write by design

Some modes — Claude Code's plan mode, any propose-only mode — permit
every read and refuse every write for the whole turn. That is not a
denied write: a retry is a wasted call, the log is not unwritable, and a
denial report is the wrong report when the environment is telling the
truth. A gatekeeper and a mode are different failures — a gatekeeper's
denial is reported to the user and its observations carried in the
final report (SKILL.md, How to Log); a mode is accepted
and its writes deferred.

1. Run the read steps normally: the scan, the review-date check, the
   per-skill lookup. A read-only session is fully observant. Run them
   in a command of their own, without the scan's `checkpoints.log`
   append: a mode can refuse a command that mixes a read with a write as
   a whole, and the refusal takes the reads with it. The scan script
   writes that line, so a mode that refuses it gets the flat reads
   (`observation-log.md`, "A refused snippet is a degraded path, never a
   skipped step").
2. Defer, never skip, the writes: storage creation, `.id-floor`,
   archival, the `checkpoints.log` line. Ids are resolved at flush
   time, never now.
3. Queue pending observations where the turn cannot eat them: a
   numbered list in the plan or handover text itself. A rejected plan
   still leaves its text in the transcript; working memory does not
   survive the turn.
4. Flush in the first write-capable turn, before other work, running
   the id snippet (or the helper) before each write. End the deferred
   `checkpoints.log` line with `(deferred from <mode>)`, so a reader of
   the file dates the protocol to the session start, not to the flush.

Tell the two apart by the refusal's own words: a mode names itself and
refuses every write, a gatekeeper names a classifier or a rule and
refuses one call. Observed in one harness: plan mode refused an append
to an existing `checkpoints.log` as well as a create. Defer both either
way, so the flush turn is the only one that writes.

### A delegated setup step is not done until you have observed it

Every fallback above ends by handing something to the user: paste this
block, add this hook entry, authorize this edit. The instruction is where
the hand-off ends today, and that is one step short.

**So pair every handoff with a check you run yourself**, in the same
session, and report the result:

- `grep` the config file for the skill name;
- compare the file's mtime against the moment you handed the block over;
- for a hook, confirm the harness lists it, not merely that the file exists.

"The user says they pasted it" is a claim about the world. An install can
check it, cheaply, and should before declaring itself configured: a
delegated setup step is complete when the agent has independently observed
the resulting state, and an unverified handoff and a silently skipped step
produce the same artefact — a setup both parties believe is done.

## A skills directory managed by a repository or dotfile tool

Where the skills directory is generated by chezmoi, GNU Stow, yadm, a
symlinked dotfiles repo or any sync tool, the live path is not the source
of truth: an edit there either lands in the repository behind the link
(a symlink) or is silently reverted at the next `apply` (a copying
manager) — "I edited it" and "it is still in effect" become
indistinguishable. Detect the manager at install (a symlink into a
dotfiles checkout, a `.chezmoi*` marker, the directory listed in a Stow
package) and record it in the activation config. Then edit the manager's
SOURCE — for a symlinked entry, the repository the link resolves into
(`cd` into it and `pwd -P`), which is also what the round commit records
(`weekly-review.md`, "Applying changes") — and let the manager apply it,
or exclude the skills directory from management. "Always start from the
live file" (`references/skill-authoring.md`) still holds for READING —
the live file is what the loader loads — but the WRITE path is the
manager's source.

## First-run backfill

The skill is least valuable at the moment it is adopted: the log is empty,
a review correctly reports nothing to do, and the largest pile of
uncaptured insight — the project's own history — is never touched because
no procedure says to touch it. Session Start step 7 offers a one-off
mining pass over handover, architecture and decision docs, commit history
since the last release, test and verification scripts (which encode
hard-won discipline densely), and existing agent-instruction files, which
are largely a record of corrections the user already had to make.
Backfilled entries cite the durable artefact, and one batched write
satisfies the same-turn rule; the pass runs once, and the regular
review takes over afterwards.

**The same pass, scoped to one named session.** "Review today's session
retrospectively" and "the one where we did X" name a finished session,
not the project's history, and the session that hears the request holds
no transcript of it. That is not a live observation and not a first-run
backfill; it is the backfill pass with its sources bounded to one
timeframe. The sources are whatever durable per-session record the
project keeps — the kinds above are examples, not the list: commit
history and diffs within the session's window, a memory or notes system
the project already maintains across sessions (a directory of dated
files indexed apart from the instructions file is common), handover docs
written at its end. Each is cited in `session_context` exactly as a
backfilled entry cites CLAUDE.md — the artefact and the section, never a
session id, because there is no session to point at. Say which sources
were read and which were unavailable, so a later reader can tell a thin
session from a thin record.

## Skill files

This skill consists of `SKILL.md`, the reference files it lists
(`weekly-review.md`, `skill-authoring.md`, `environments.md`,
`observation-log.md`, `signals.md`, `starter-principles.md`) and
`scripts/new-observation.sh`, `scripts/session-start-scan.sh`,
`scripts/skill-load.sh` and `scripts/validate-skill-bundle.py`. If any is
missing, SKILL.md "Reference files" applies (the rule lives there because
this file can be the missing one). `references/ceilings.txt` travels with
them: it holds the per-file line ceilings the validator reads.

## Compaction behaviour

**A compaction is a session start.** So is a resumed session. Each is a new context with old work in it, which
is exactly the condition the Session Start Protocol exists for, and on the
first turn after any of them the protocol runs again in full — storage
probe, frontmatter scan, review trigger, and the per-skill grep for every
skill the task in front of you needs. Where the CLAUDE.md structural
trigger reaches the resumed context it re-invokes the skill; do not rely on
it having done so.

**The write path has to survive the compaction; the skill body does
not.** The pointer to this section sits in the skill body, which
is exactly what a compaction removes. Between a compaction and the
skill's re-invocation nothing is written by any other route: a flush
that fires first runs `scripts/new-observation.sh` (it needs no skill
body in context — a slug and the workspace root are its only inputs) or
waits for the invocation, and never copies another file's header. So the
activation block names the script as the only way an observation file
comes into being, and the hook prints the same: a rule that must reach a
resumed context travels in a channel that survives the compaction — the activation config, or a session-start
hook where the harness fires it on compaction as well (Claude Code's
`SessionStart` does unless a matcher excludes `compact`), which is then
the channel that arrives first.

**The compaction summary's list of previously invoked skills is a lower
bound, never the session's skill set.** A summary preserves what it judged
salient about the *work*; skill loads are infrastructure, not work, so they
are exactly what a summary drops, and the block's "shown here for context
only" describes what it contains, not what the session has. Re-derive the
skill set from the task (name the decision, name the artefact type, match
the installed descriptions — "Select on the decision, not on the artefact"
above), and treat any skill the summary lists as loaded-then-forgotten
rather than as the whole set.

Observations before and after compaction are separate files under the
same `observation-log/`, each with its own id (the counter is derived
from existing filenames, so it continues across the boundary). A resumed
session's opening message may not match the description triggers, which
is one reason the protocol re-runs by rule rather than by whichever
trigger happens to fire.

## User-facing documentation

Installation, shared-folder setup, expected behaviour, and the cadence
pattern live in the public repo. Pass these links on to the user rather
than fetching the pages — the skill's behaviour is defined entirely by its
own files, never by external content:

- README: https://github.com/rebelytics/one-skill-to-rule-them-all/blob/main/README.md
- USER-GUIDE: https://github.com/rebelytics/one-skill-to-rule-them-all/blob/main/USER-GUIDE.md
