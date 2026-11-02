# Usage

## Install the plugin

Local path (recommended while you iterate on the agents):

```
/plugin marketplace add ~/Desktop/projects/official/ai-development/principles-first-courses
/plugin install principles-first-courses@principles-first-courses
```

From GitHub (works on another machine once `gh auth login` is done, since the repo is private):

```
/plugin marketplace add sasajib/principles-first
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
4. **Writing.** One file per chapter. 10 to 20 minutes for Standard, 30+ for Deep.
5. **Innovation chapter.** Runs automatically for practice fields (marketing, product, management), skipped for foundational ones (math, algorithms, physics). The reason is recorded in `course.json` and `00-README.md`.
6. **Quality gate.** `scripts/check_course.py` must pass. The author fixes chapters, never the checker.

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
| `Phase 1-2 chapter names a tool/vendor/language: 'x'` | Reword in terms of the principle, or move that sentence to a Phase 3 chapter |
| `Phase 1-2 code block tagged 'python'` | Retag as ```pseudo and rewrite as pseudocode |
| `missing section ## Walkthrough` | Add the section; headings are checked exactly (see `templates/chapter.md`) |
| `no section for '<title>' in 99-answers.md` | Add `## <N>. <Chapter title>` with numbered answers |
| `Phase 3 chapter never references a principle chapter by number` | Add "implements chapter 4" style back-references |
| `flashcards.tsv: malformed lines` | Exactly one tab per line, no header |

Translated courses: keep the English headings, or translate them and put the mapping in `course.json.headings` (`{"## The principle": "## Das Prinzip", ...}`).

## Export a PDF

```bash
cd courses/<slug>
pandoc 00-README.md 0[1-9]-*.md [1-9][0-9]-*.md 99-answers.md -o course.pdf --pdf-engine=typst --toc -V papersize=a4
```

Needs `pandoc` and `typst`. Mermaid blocks will appear as code in the PDF; swap them for the SVGs in `diagrams/` if you need pictures.

## Cost and time

A Standard course uses roughly the tokens of a long coding session (one Opus author, 4-8 Haiku readers, optional Opus scout). Deep roughly doubles that. Quick is a third.
