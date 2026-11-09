# Architecture

```
/course <topic>                      skills/course/SKILL.md   (team lead, talks to you)
   │  brief
   ▼
course-author (Opus)                 agents/course-author.md
   │  batches of 3-4 URLs
   ├──► source-reader ×N (Haiku)     agents/source-reader.md   → structured notes per source
   │
   ├── outline.md (chapter plans) ──► you approve ──► chapters, preface, answers, flashcards, sources, continuity.md
   │        │
   │        └──► book-editor ×N (Opus)   agents/book-editor.md  → findings, SHIP/REVISE, ≤2 cycles
   ▼  HANDOFF
innovation-scout (Opus, auto on/off) agents/innovation-scout.md → NN-open-problems.md
   ▼
scripts/check_course.py              quality gate: structure, principles-first, runs lint_prose.py (fails the build)
scripts/lint_prose.py                anti-AI prose catalogue, counted by script
scripts/render_diagrams.mjs          Mermaid → SVG via beautiful-mermaid
scripts/build_course.py              bundle: dist/<slug>.md (ASCII diagrams), .pdf (PNG diagrams, typst), .tex
scripts/build_bundle.sh              check → render → build one course bundle (no git)
   ▼
you read dist/<slug>.pdf, dist/<slug>.md or dist/<slug>.tex anywhere
```

## Pieces

| Path | Role | Change it when |
|---|---|---|
| `skills/course/SKILL.md` | Scoping questions, innovation auto-decision, outline pause, gate, bundle, publish, delivery summary |
| `agents/course-author.md` | Research depth table, source priorities, outline design, chapter template, manifest schema, self-check | You want to change the pedagogy, phase structure or output files |
| `agents/source-reader.md` | Reads 3-4 sources and returns structured notes (cheap model) | You want readers to extract something new |
| `agents/book-editor.md` | Reviews one chapter against `references/editor-rubric.md`; returns findings and SHIP/REVISE | You change the rubric or want a different review depth |
| `references/chapter-craft.md` | How a chapter is built: plan, opening, sections, summary, exercises, length | You change the book form |
| `references/writing-rules.md` | Prose rules and the anti-AI catalogue the linter counts | You add or relax a prose rule (change `lint_prose.py` together) |
| `references/editor-rubric.md` | The rows the editor scores | Together with the two files above |
| `scripts/lint_prose.py` | Counts banned constructions, dashes, AI vocabulary, meta-commentary, hedges, rhythm, bullet density | A rule changes |
| `templates/book.typ` | Typst book template: title page, contents, part pages, chapter pages, running headers | You want a different look |
| `agents/innovation-scout.md` | Writes the open-problems chapter | You want a different closing chapter |
| `scripts/check_course.py` | Enforces: phases, forbidden terms, fences, sections, questions answered, flashcards | You add a heading, a file, or a new rule. Keep errors strict; add soft rules as warnings |
| `scripts/render_diagrams.mjs` | Renders ```mermaid blocks to `diagrams/*.svg` (and `.txt` with `--ascii`) | You want another theme or output |
| `scripts/build_course.py` | Merges chapters into one document; converts diagrams (PNG for PDF/LaTeX, text drawing for Markdown); answer key excluded unless `--with-answers` | You change the bundle layout, page setup or engine |
| `scripts/build_bundle.sh` | check → render → build one course bundle | You want a different pipeline |
| `templates/chapter.md` | The chapter skeleton the checker expects | Together with the checker and the author |
| `courses/<slug>/course.json` | Manifest the checker relies on | Generated; edit only to fix phase membership or forbidden terms |

## Design decisions

- **One Markdown file per chapter**, not one big file. A reader can quiz a single chapter, diffs stay readable, and incremental mode can insert a chapter without rewriting everything.
- **Counted means counted by a script.** The prose rules that can be counted live in `lint_prose.py`; agents copy its numbers and never recount by hand (a rule borrowed from book-factory).
- **The checker is the contract.** Agents are told to fix chapters, never the checker. If a rule is wrong, change it here deliberately, with the reason in the commit message.
- **Mermaid stays in the chapter sources.** GitHub renders it natively. The bundle converts every diagram (PNG in PDF/LaTeX, text drawing in the single Markdown) because uploaded documents go through parsers that do not run Mermaid. SVG/PNG are derived artefacts, regenerated, never hand-edited.
- **The deliverable is a document, not a service.** You get one PDF, one Markdown file and one LaTeX source, and the plugin stays out of whatever you read them in.
- **Research is delegated to cheap readers** (from course-builder). The author's context holds notes, not raw articles, which leaves room for synthesis.
- **Generated output is ignored.** The plugin is the artefact. A course you build stays local unless you deliberately change `.gitignore`.

## Local development

```bash
npm install                                  # beautiful-mermaid
python3 scripts/check_course.py courses/x    # no Python deps beyond stdlib
/plugin update principles-first-courses      # after editing skills/ or agents/
```

Agent frontmatter (`model`, `effort`, `maxTurns`, `tools`, `memory`) follows Claude Code's agent definition format; `memory: user` gives the author and scout a persistent memory across courses.
