# principles-first


**Principles-first** means every course has three phases:

1. **The problems.** What the field exists to solve. No solutions yet.
2. **The principles.** One idea per chapter, taught with mental models, worked examples and pseudocode. **No tools, vendors or programming languages allowed.** A linter enforces this.
3. **The tools.** A map from each principle to the tools or languages that implement it, then applied chapters, then a capstone done by hand first and with tools second.

Example: digital marketing teaches "attention is scarce and bought at the margin" before any ad platform. Data structures teaches "first in, first out, here is the procedure" in pseudocode before any language.

## Quick start

```bash
# 1. one-time: register this repo as a plugin marketplace in Claude Code
/plugin marketplace add ~/Desktop/projects/official/ai-development/principles-first-courses
/plugin install principles-first-courses@principles-first-courses

# 2. in a Claude Code session opened in this repo
/course digital marketing
/course data structures and algorithms deep
/course courses/example-course            # add a chapter to an existing course
```

The skill asks at most three questions (learner, end goal, depth), researches 8 to 40 real sources, shows you an outline to approve, writes one Markdown file per chapter, runs the quality gate, builds the bundle, commits and pushes. A Standard course takes 10 to 20 minutes.

**The deliverable** is `courses/<slug>/dist/`:

| File | Use |
|---|---|
| `<slug>.md` | Same content as one Markdown file; diagrams as text drawings, no external files. |
| `<slug>.tex` | LaTeX source, images in `dist/diagrams/`. |
| `diagrams/*.png`, `*.svg` | Every diagram on its own. |


```bash
python3 scripts/build_course.py courses/<slug> [--with-answers] [--formats md,pdf,tex]
```

## What a course looks like

```
courses/<slug>/
  course.json        manifest: phases, forbidden terms, metadata
  outline.md         the approved plan: one chapter-plan block per chapter
  continuity.md      terminology, running-example facts, promises to the reader
  00-README.md       goal, how to study, chapter table
  01-....md          Phase 1 chapters
  0n-....md          Phase 2 chapters (pseudocode and diagrams only)
  0n-....md          Phase 3 chapters and capstone
  99-answers.md      answers to every chapter's questions
  sources.md         every source, single-source claims flagged
  research-log.md    quorum tracking and research metadata
  diagrams/          SVGs rendered from the chapters' Mermaid blocks
  dist/              the uploadable bundle: <slug>.md, <slug>.pdf, <slug>.tex, diagrams/*.png
```

Every chapter is a book chapter: it opens inside a concrete situation, carries three to six sections with headings that name content, shows each procedure applied step by step, gives a second real example, states where the principle breaks, and ends with a Summary and Exercises. Sources are recorded per chapter in `sources.md`, not in the running text. See [templates/chapter.md](templates/chapter.md), [references/chapter-craft.md](references/chapter-craft.md) and [references/writing-rules.md](references/writing-rules.md).

## Documentation

| Doc | Read it when |
|---|---|
| [docs/USAGE.md](docs/USAGE.md) | Running `/course`, options, approving outlines, incremental mode, re-running checks |
| [docs/PEDAGOGY.md](docs/PEDAGOGY.md) | The rules the author follows and why, with the research behind them |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the skill, agents and scripts fit together; how to change them |

## Repo layout

```
.claude-plugin/     plugin and marketplace manifests
agents/             course-author, source-reader, book-editor, innovation-scout
references/         chapter-craft.md, writing-rules.md, editor-rubric.md (the standard)
templates/          chapter.md (chapter form), book.typ (PDF book template)
courses/            generated courses, one folder each
docs/               documentation
```

## Credits

