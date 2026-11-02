# Architecture

```
/course <topic>                      skills/course/SKILL.md   (team lead, talks to you)
   │  brief
   ▼
course-author (Opus)                 agents/course-author.md
   │  batches of 3-4 URLs
   ├──► source-reader ×N (Haiku)     agents/source-reader.md   → structured notes per source
   │
   ├── outline.md  ──► you approve ──► chapters, README, answers, flashcards, sources, course.json
   │
   ▼  HANDOFF
innovation-scout (Opus, auto on/off) agents/innovation-scout.md → NN-open-problems.md
   ▼
scripts/check_course.py              quality gate (fails the build)
scripts/render_diagrams.mjs          Mermaid → SVG via beautiful-mermaid
scripts/build_course.py              bundle: dist/<slug>.md (ASCII diagrams), .pdf (PNG diagrams, typst), .tex
scripts/publish.sh                   check → render → build → commit + push courses/<slug>
   ▼
```

## Pieces

| Path | Role | Change it when |
|---|---|---|
| `skills/course/SKILL.md` | Scoping questions, innovation auto-decision, outline pause, gate, bundle, publish, delivery summary |
| `agents/course-author.md` | Research depth table, source priorities, outline design, chapter template, manifest schema, self-check | You want to change the pedagogy, phase structure or output files |
| `agents/source-reader.md` | Reads 3-4 sources and returns structured notes (cheap model) | You want readers to extract something new |
| `agents/innovation-scout.md` | Writes the open-problems chapter | You want a different closing chapter |
| `scripts/check_course.py` | Enforces: phases, forbidden terms, fences, sections, questions answered, flashcards | You add a heading, a file, or a new rule. Keep errors strict; add soft rules as warnings |
| `scripts/render_diagrams.mjs` | Renders ```mermaid blocks to `diagrams/*.svg` (and `.txt` with `--ascii`) | You want another theme or output |
| `scripts/build_course.py` | Merges chapters into one document; converts diagrams (PNG for PDF/LaTeX, text drawing for Markdown); answer key excluded unless `--with-answers` | You change the bundle layout, page setup or engine |
| `scripts/publish.sh` | check → render → build → commit → push one course | You change the branch |
| `templates/chapter.md` | The chapter skeleton the checker expects | Together with the checker and the author |

## Design decisions

- **The checker is the contract.** Agents are told to fix chapters, never the checker. If a rule is wrong, change it here deliberately, with the reason in the commit message.
- **Mermaid stays in the chapter sources.** GitHub renders it natively. The bundle converts every diagram (PNG in PDF/LaTeX, text drawing in the single Markdown) because uploaded documents go through parsers that do not run Mermaid. SVG/PNG are derived artefacts, regenerated, never hand-edited.
- **Research is delegated to cheap readers** (from course-builder). The author's context holds notes, not raw articles, which leaves room for synthesis.

## Local development

```bash
npm install                                  # beautiful-mermaid
python3 scripts/check_course.py courses/x    # no Python deps beyond stdlib
/plugin update principles-first-courses      # after editing skills/ or agents/
```

Agent frontmatter (`model`, `effort`, `maxTurns`, `tools`, `memory`) follows Claude Code's agent definition format; `memory: user` gives the author and scout a persistent memory across courses.
