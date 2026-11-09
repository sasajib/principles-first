# principles-first

A Claude Code plugin that turns a topic into a book-length course, in the order a learner should meet it:
the problems first, then one principle per chapter, and the tools only at the end. One finished course ships
with it — 14 chapters on marketing — as proof of what it produces.

The plugin is the interesting part. It is a small team of agents with a written standard and a script that
enforces it: research, outline, approval, one chapter at a time, a prose linter, an editor pass, then a
Markdown/PDF/LaTeX bundle.

## What principles-first means

Every course has three parts:

1. **The problems.** What the field exists to solve. No solutions yet.
2. **The principles.** One idea per chapter, taught with mental models, worked examples and pseudocode.
   **No tools, vendors or programming languages allowed.** `scripts/check_course.py` fails the build if one
   appears before the tools part.
3. **The tools.** A map from each principle to the tools that implement it, applied chapters, then a capstone
   done by hand first and with tools second.

Marketing therefore teaches "attention is scarce and bought at the margin" before any ad platform. A course on
data structures teaches "first in, first out, here is the procedure" in pseudocode before any language.

## Install

```bash
# in Claude Code
/plugin marketplace add sasajib/principles-first
/plugin install principles-first-courses@principles-first-courses
```

From a local clone instead, while you edit the agents:

```bash
/plugin marketplace add ~/path/to/principles-first
/plugin install principles-first-courses@principles-first-courses
```

Diagrams render to SVG with one dependency, so run this once in the clone:

```bash
npm install
```

## Run it

Open Claude Code inside the repo, so courses land in `courses/`:

```bash
/course digital marketing                  # standard depth, the default
/course data structures and algorithms deep
/course courses/example-course          # add a chapter to an existing course
```

The skill asks at most three questions (who is the learner, what should they be able to do, how deep), shows
an outline to approve, writes one file per chapter, runs the quality gate, builds the bundle, then commits and
pushes.

## What it costs

Be clear about this before you run it: a course is a book, not a chat answer. Standard depth is 15 to 25
sources read, 10 to 14 chapters at 2,000 to 4,500 words each, and a full-book editing pass. The included
marketing course is 14 chapters, about 42,000 words, from 52 sources.

That is hundreds of model calls on your own Claude Code plan, and the research and rewrite passes read far
more text than the output contains. I have not measured wall-clock time or token spend precisely, so I will
not quote a number. Budget hours of agent time, not minutes, and start with a Quick course (6 to 8 chapters,
8 to 12 sources) to see the cost before committing to a deep one.

## Output

`courses/<slug>/dist/` is the uploadable bundle:

| File | Use |
|---|---|
| `<slug>.pdf` | Upload to any reader or knowledge base. Diagrams embedded as images. |
| `<slug>.md` | The whole book as one Markdown file; diagrams as text drawings, no external files. |
| `<slug>.tex` | LaTeX source with images in `dist/diagrams/`. |
| `diagrams/*.png`, `*.svg` | Every diagram on its own. |

Rebuild any time:

```bash
python3 scripts/build_course.py courses/<slug> [--with-answers] [--formats md,pdf,tex]
```

`99-answers.md` is left out of the bundle on purpose, so a tutor reading it cannot hand out answers.

## What a course looks like

```
courses/<slug>/
  course.json        manifest: parts, chapter list, forbidden terms, metadata
  outline.md         the approved plan, one block per chapter
  continuity.md      terminology, running-example facts, promises to the reader
  00-README.md       goal, who it is for, how to study, chapter table
  01-....md          Part I chapters, the problems
  0n-....md          Part II chapters, the principles (pseudocode only)
  0n-....md          Part III chapters, the tools, and the capstone
  99-answers.md      answers to every chapter's questions
  flashcards.tsv     Anki-importable
  sources.md         every source, single-source claims flagged
  research-log.md    what was searched, what was read, what failed
  diagrams/          SVGs rendered from the chapters' Mermaid blocks
  dist/              the built bundle
```

Chapter form is fixed, not improvised: open inside a concrete situation, three to six sections with headings
that name content, each procedure applied step by step, a second real example, a statement of where the
principle breaks, a Summary and Exercises. The standard lives in `templates/chapter.md`,
`references/chapter-craft.md` and `references/writing-rules.md`.

## Enforced, not suggested

| Script | What it refuses |
|---|---|
| `scripts/check_course.py` | A named tool, vendor or language before the tools part; a missing Summary or Exercises; a chapter with no declared sources; wrong chapter count against the manifest. |
| `scripts/lint_prose.py` | The catalogue of AI-writing tells in `references/writing-rules.md`: banned connectives, tricolons, "not just X but Y", bold mid-text, unhealthy sentence rhythm. |
| `scripts/build_course.py` | Nothing — it builds, and fails loudly if pandoc or typst are missing. |

The agents cannot skip the gate: `skills/course/SKILL.md` orders the run and the gate is a hard stop before
publish.

## Repository layout

```
.claude-plugin/     plugin and marketplace manifests
skills/course/      the /course skill: scope, outline approval, gate, publish
agents/             course-author, source-reader, book-editor, innovation-scout
references/         chapter-craft.md, writing-rules.md, editor-rubric.md (the standard)
scripts/            check_course.py, lint_prose.py, build_course.py, render_diagrams.mjs, publish.sh
templates/          chapter.md (chapter form), book.typ (PDF book template)
courses/            generated courses, one folder each
docs/               documentation
```

## Documentation

| Doc | Read it when |
|---|---|
| [docs/USAGE.md](docs/USAGE.md) | Running `/course`, depth options, approving outlines, incremental mode, re-running checks |
| [docs/PEDAGOGY.md](docs/PEDAGOGY.md) | The rules the author follows and the research behind them |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the skill, agents and scripts fit together, and how to change them |

## Licence and credits

MIT. See [LICENSE](LICENSE).

The research pipeline is adapted from [klausners/course-builder](https://github.com/klausners/course-builder).
The writing rules and the anti-AI catalogue are adapted from
[luquiluke/claude-book-skill](https://github.com/luquiluke/claude-book-skill) and
[blader/humanizer](https://github.com/blader/humanizer). The editor loop and the "counted by a script" rule
follow [seba-cascardo/book-factory](https://github.com/seba-cascardo/book-factory). All MIT. Diagrams are
rendered with [beautiful-mermaid](https://github.com/lukilabs/beautiful-mermaid) (MIT). PDF via
[pandoc](https://pandoc.org) and [Typst](https://github.com/typst/typst). Courses are studied well with
