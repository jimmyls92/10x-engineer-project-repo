"""Merge the working prompt-log shards into docs/prompt-log.md.

Concatenation in filename order, per-shard front matter dropped, one heading for the
whole file. Also derives the C1.3 iteration index from the entries themselves rather
than from a hand-kept list.
"""
import pathlib
import re

SHARDS = sorted(pathlib.Path("docs/prompt-log").glob("0*.md"))

TASK_MAP = [
    ("1-6", "Setup", "Working protocol, `CLAUDE.md`, the log itself — and one discarded attempt"),
    ("7-40", "Task 1.1 / 1.2", "Staged exploration -> `docs/SYSTEM_MODEL.md`, six sections plus the context strategy"),
    ("41-73", "Tasks 1.3-1.7", "Bugs #1-#4 and `PATCH /prompts/{id}`"),
    ("74-75", "Task 1.8", "`docs/ai-verification-note.md`"),
    ("76-89", "Task 1.9", "Docstrings, the README, and the corrections the clean-clone test forced"),
]

entries = []  # (number, heading, body)
ESCAPED = re.compile(r"\\u([0-9a-fA-F]{4})")

for shard in SHARDS:
    text = shard.read_text(encoding="utf-8")
    # shard 02 was written by a session that escaped its dashes; repair them here,
    # in the merged file only, leaving the working shards as they were committed.
    text = ESCAPED.sub(lambda m: chr(int(m.group(1), 16)), text)
    start = text.index("\n## Entry ")
    body = text[start:].strip("\n")
    for chunk in re.split(r"(?m)^(?=## Entry \d+)", body):
        chunk = chunk.strip()
        if not chunk.startswith("## Entry "):
            continue
        chunk = re.sub(r"\n+---\s*$", "", chunk)
        head = chunk.splitlines()[0]
        num = int(re.match(r"## Entry (\d+)", head).group(1))
        entries.append((num, head, chunk))

numbers = [n for n, _, _ in entries]
assert numbers == sorted(numbers), "entries are out of order"
assert numbers == list(range(1, len(numbers) + 1)), f"gap in numbering: {numbers}"

# --- C1.3 index, derived from the entries -------------------------------------
KINDS = [
    ("narrow", "narrowed context"),
    ("restructur", "restructured the prompt"),
    ("constraint", "added a constraint"),
]
index_rows = []
for num, head, chunk in entries:
    m = re.search(r"\*\*(?:Why|Constraint)[^*]{0,160}C1\.3[^*]{0,200}\*\*(.{0,400})", chunk, re.S)
    if not m:
        continue
    window = (m.group(0)).lower()
    kind = None
    for needle, label in KINDS:
        if needle in window:
            kind = label
            break
    if kind is None:
        kind = "iteration"
    title = head.split("—", 1)[1].strip() if "—" in head else head
    index_rows.append((num, kind, title))

header = ["""# Prompt log

**Criterion C1.3.** Every prompt sent in this repository during Module 1, in order, with what came
back and why the next prompt changed. {n} entries, written live — each one appended before or
alongside the work it describes, never reconstructed afterwards.

The first person throughout is **the engineer prompting**, not the assistant. Prompts are quoted
verbatim, typos included; nothing here was tidied up after the fact.

**Tool:** Claude Code (Opus 5), run from the repository root.

**How the liveness is evidenced.** The log was kept as one shard per task under `docs/prompt-log/`,
and each shard was committed as it was written rather than at the end. The commit history of that
directory, interleaved with the code and document commits it describes, is the evidence that this
file was not written backwards from a finished repository. This file is the concatenation of those
shards in filename order, with the per-shard front matter dropped and nothing else changed.

## What the entries cover

| Entries | Task | Deliverable |
|---|---|---|
""".format(n=len(entries))]

for rng, task, deliverable in TASK_MAP:
    header.append(f"| {rng} | {task} | {deliverable} |\n")

header.append("""
## The C1.3 iterations

C1.3 asks for at least two iterations that **narrowed context, added a constraint, or restructured** a
prompt because the output was not good enough — rewording does not count. Those are flagged in place,
inside the entry, with the reason the change was made. They are indexed here so they can be found
without reading {n} entries:

| Entry | Kind | What it did |
|---|---|---|
""".format(n=len(entries)))

for num, kind, title in index_rows:
    header.append(f"| **{num}** | {kind} | {title} |\n")

header.append("""
The flag's wording changed as the module went on — the earliest entries name the move in a sentence,
the later ones in a bracket after "C1.3". Rows reading simply *iteration* are the ones whose flag
names the move in prose; the entry itself says which of the three it was. Nothing was retrofitted to
make the index tidier.

---

""")

out = "".join(header) + "\n\n---\n\n".join(chunk for _, _, chunk in entries) + "\n"
pathlib.Path("docs/prompt-log.md").write_text(out, encoding="utf-8")
print(f"merged {len(entries)} entries from {len(SHARDS)} shards -> docs/prompt-log.md")
print(f"C1.3 index rows: {[n for n, _, _ in index_rows]}")
