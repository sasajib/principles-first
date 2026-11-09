# Usage

## Install the plugin

From GitHub:

```
/plugin marketplace add sasajib/principles-first
/plugin install principles-first-courses@principles-first-courses
```

From a local clone, which is what you want while you edit the agents or skills:

```
/plugin marketplace add ~/path/to/principles-first
/plugin install principles-first-courses@principles-first-courses
```

After editing anything under `skills/` or `agents/`, run `/plugin update principles-first-courses` or restart the session.

Also run `npm install` once in the repo so diagrams render to SVG.

## Build a course

Open Claude Code **inside this repo** (so courses land in `courses/`), then:

```
/course <topic> [quick|standard|deep] [--innovation on|off] [--lang xx]
```

| Argument | Meaning | Default |
|---|---|---|
| topic | anything: "digital marketing", "data structures and algorithms", "negotiation" | required |
| quick / standard / deep | 6-8 / 10-14 / 16-24 chapters; 8-12 / 15-25 / 25-40 sources | standard |
| --innovation on/off | force the final "open problems" chapter | decided automatically |
| --lang xx | course language | language of your request |

What happens:

1. **Scoping.** Up to three questions: who is the learner, what should they be able to do, how deep. Answer in one line each. Say "no questions, just build" to skip everything including outline approval.
2. **Research.** Parallel source-reader agents read real articles. Claims need three independent sources to be stated as fact.
3. **Outline approval.** You get the three-phase outline. Reply "approve" or list edits ("merge chapters 4 and 5", "add a chapter on X", "move Y to Phase 3").
4. **Writing.** One file per chapter, 2,000 to 4,500 words each, then a full-book editing pass. This is the slow part and it is a book, not a chat answer: a Standard course is 10 to 14 chapters and about 40,000 words, from 15 to 25 sources read. Expect hours of agent time and hundreds of model calls on your own Claude Code plan. Run a Quick course first to see the cost before committing to Standard or Deep.
5. **Innovation chapter.** Runs automatically for practice fields (marketing, product, management), skipped for foundational ones (math, algorithms, physics). The reason is recorded in `course.json` and `00-README.md`.
6. **Quality gate.** `scripts/check_course.py` must pass. The author fixes chapters, never the checker.
7. **Bundle and publish.** `build_course.py` writes `dist/<slug>.md`, `.pdf`, `.tex` and `diagrams/*.png`; then commit and push.

## Add to an existing course

```
/course courses/example-course add a chapter on attribution
```

The author reads the manifest, researches only the new material, inserts the chapter in the right phase, renumbers if needed, and updates the README, answers and flashcards.

## Run the checks by hand

```bash
python3 scripts/check_course.py courses/<slug>            # errors fail, warnings print
python3 scripts/check_course.py courses/<slug> --strict   # warnings fail too
node scripts/render_diagrams.mjs courses/<slug>           # SVGs into courses/<slug>/diagrams/
node scripts/render_diagrams.mjs courses/<slug> --theme tokyo-night --ascii
bash scripts/publish.sh <slug> "message"                  # check + render + commit + push
```

Checker errors and what to do:

| Error | Fix |
|---|---|
| `Phase 1-2 chapter names a tool/vendor/language: 'x'` | Reword in terms of the principle, or move that sentence to a Part III chapter |
| `Phase 1-2 code block tagged 'python'` | Retag as ```pseudo and rewrite as pseudocode |
| `opening before the first section is N words` | Open inside a concrete situation, two to five paragraphs, before any heading |
| `only N content sections` / `missing section ## Summary` / `## Exercises must be last` | Follow `templates/chapter.md`: three or more content sections, then Summary, then Exercises |
| `prose: banned construction ...` / `prose: em/en dashes ...` / `prose: AI vocabulary ...` / `prose: meta-commentary ...` | See `references/writing-rules.md`; rewrite the sentence, do not patch the word |
| `prose: template-slot heading` / `chapter contains a '## Sources' section` | Headings name content; sources go in `sources.md` under the chapter |
| `00-README.md: contains reading-time estimates` | The preface of a book has none |
| `no section for '<title>' in 99-answers.md` | Add `## <N>. <Chapter title>` with numbered answers |
| `Phase 3 chapter never references a principle chapter by number` | Add "implements chapter 4" style back-references |
| `flashcards.tsv: malformed lines` | Exactly one tab per line, no header |

Run the prose linter alone on one chapter while editing: `python3 scripts/lint_prose.py courses/<slug>/04-....md`.

Forbidden terms: write tool names in `course.json.forbidden_in_phases_1_2` with their real capitalisation (`Plausible`, `Notion`). Capitalised terms match case-sensitively so ordinary words like "plausible" are not flagged; all-lowercase terms match any case.

Translated courses: keep the English headings, or translate them and put the mapping in `course.json.headings` (`{"## The principle": "## Das Prinzip", ...}`).

## Rebuild the bundle

```bash
python3 scripts/build_course.py courses/<slug>                  # md + pdf + tex
python3 scripts/build_course.py courses/<slug> --with-answers   # include the answer key as an appendix
python3 scripts/build_course.py courses/<slug> --formats md     # only the single Markdown
```

Diagram handling per format: PDF and LaTeX get PNG images (SVG from beautiful-mermaid, converted with `rsvg-convert`); the single Markdown gets a Unicode text drawing of each diagram so it has no external dependencies. The answer key is excluded by default so a tutor reading the file cannot hand out answers.

The PDF uses `templates/book.typ` (title page, contents, part pages, chapter pages with running headers). Requirements: `pandoc`, `typst` (a single binary, installed in `~/.local/bin`; `lualatex` works as fallback without the book template), `rsvg-convert` (librsvg), Node with `npm install` done in the repo.

## Cost and time

A Standard course uses roughly the tokens of a long coding session (one Opus author, 4-8 Haiku readers, optional Opus scout). Deep roughly doubles that. Quick is a third.
