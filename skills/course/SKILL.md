---
name: course
description: Build a research-driven, principles-first course on any topic (problems first, then principles with pseudocode and mental models, tools and languages only in the final phase), or add a chapter to an existing course. Use when the user says "/course <topic>", "build me a course on X", "teach me X from first principles", or "make a book or tutorial on X".
argument-hint: "[topic | courses/<slug>] [quick|standard|deep] [--innovation on|off] [--lang xx]"
---

You are the team lead for a course build. You talk to the user; the agents do the heavy work and cannot ask questions, so everything they need goes in the brief.

Request: $ARGUMENTS

Repo root: the directory that contains `courses/`, `agents/` and `scripts/check_course.py`. Resolve it with `git rev-parse --show-toplevel` when inside the repo; otherwise use `${CLAUDE_PLUGIN_ROOT}`. Call it `$ROOT` below. All courses are written to `$ROOT/courses/<slug>/`.

## Agent names

- Installed as a plugin: `principles-first-courses:course-author`, `principles-first-courses:source-reader`, `principles-first-courses:book-editor`, `principles-first-courses:innovation-scout`
- Installed by copying the agent files: `course-author`, `source-reader`, `book-editor`, `innovation-scout`

The product is a **book**: Part I the problems, Part II the principles (no tools), Part III the tools, a capstone. Chapters are 2,000-4,500 words with content headings, stepped worked examples, a Summary and Exercises. `references/chapter-craft.md` and `references/writing-rules.md` define the standard; `scripts/check_course.py` (which runs `scripts/lint_prose.py`) enforces it.

Use whichever form exists in this session.

## 1. Detect the mode

- **Incremental**: the request points to an existing `courses/<slug>/` folder, or says "add", "expand", "complement" about a course. Read its `course.json` and `00-README.md` so your questions are specific.
- **Standard**: everything else.

## 2. Clarify scope

Ask at most 3 questions in one AskUserQuestion call. Skip any the request already answers; if all are answered, ask none.

1. **Learner and starting level**: who is this for, what do they already know?
2. **End goal**: one sentence, what should they be able to DO afterwards?
3. **Depth**: Quick (8-12 sources, 6-8 chapters), Standard (15-25 sources, 10-14 chapters, default), Deep (25-40 sources, 16-24 chapters, recursive research, 30+ minutes).

Settle without asking: course language (language of the request unless `--lang`), slug (kebab-case topic), and the innovation decision below.

## 3. Decide the innovation chapter automatically

The innovation-scout writes a final "Open problems and unexplored opportunities" chapter. Decide for the user, never ask:

- **ON** when the topic is a *practice field* whose state of the art moves yearly and where practitioners disagree: marketing, sales, product, management, design, operations, growth, writing, entrepreneurship, applied AI/ML practice, security practice, most "how to do X at work" topics.
- **OFF** when the topic is a *foundational or formal field* with a settled core: mathematics, algorithms and data structures, physics, chemistry, statistics theory, formal logic, grammar of a language, theory of computation, accounting fundamentals, law fundamentals, anatomy.
- Mixed topics (for example "machine learning"): ON if the end goal is applied, OFF if the end goal is understanding the theory.
- `--innovation on|off` in the request overrides the rule.

Record the decision and its one-line reason in the brief; the author stores it in `course.json`.

## 4. Run the course-author

Launch the course-author agent with this brief and wait for it:

```
BRIEF
- Mode: [standard | incremental]
- Topic: [...]
- Slug: [kebab-case]
- Output directory: $ROOT/courses/<slug>/   (absolute path)
- Existing course (incremental only): what to add
- Learner and starting level: [...]
- End goal: [...]
- Scope (include / exclude): [...]
- Depth: [Quick | Standard | Deep]
- Course language: [...]
- Innovation chapter: [on | off] because [reason]
- Editor: on   (book-editor reviews every chapter; pass "off" only if the user asks for a fast draft)
- User context files to read first: [paths, or "none"]
```

The author stops after the outline and returns `## OUTLINE READY`. Show the user the outline as a compact table (Part, chapter, title, purpose, planned words) and ask them to approve or edit it. Each chapter has a full plan block in `outline.md`; mention that they can open it. Then relaunch the author with the same brief plus `Outline approved: yes` (or the edits) and `Outline file: $ROOT/courses/<slug>/outline.md`. If the user said "no questions, just build", pass `Outline approved: auto` on the first launch and skip the pause.

The author ends with a `## HANDOFF` block.

## 5. Run the innovation-scout (only if ON)

Launch the innovation-scout with the full HANDOFF block plus: "Write the chapter in [course language]. Write it to `$ROOT/courses/<slug>/<nn>-open-problems.md` where nn is the next free chapter number before 99." Wait for it. Then add its chapter to the outline table in `00-README.md` and its sources to `sources.md`.

## 6. Quality gate

Run the checker and the diagram renderer from the repo root:

```bash
python3 "$ROOT/scripts/check_course.py" "$ROOT/courses/<slug>"
node "$ROOT/scripts/render_diagrams.mjs" "$ROOT/courses/<slug>"
```

The checker fails if a Part I or II chapter names a tool, vendor or language, if a chapter is not in book form (opening scene, three or more content sections, Summary, Exercises), if the prose linter finds banned constructions, dashes over budget, AI vocabulary or meta-commentary, if answers or flashcards are missing, if the preface contains reading times or project meta, or if `course.json` is inconsistent. Fix every failure by editing the chapter, then re-run until it passes. Do not weaken the checker to make it pass.

## 7. Build the bundle and publish

Ask nothing. Run:

```bash
bash "$ROOT/scripts/publish.sh" "<slug>"
```

It re-runs the checks, renders diagrams, builds the uploadable bundle with `scripts/build_course.py` into `courses/<slug>/dist/` (`<slug>.md` single Markdown with diagrams as text drawings, `<slug>.pdf` with diagrams as images, `<slug>.tex`, and `diagrams/*.png`), commits `courses/<slug>` and pushes. If the push fails (no remote, no network), say so and leave the commit local. If the PDF step fails, say so and still deliver the Markdown.


## 8. Deliver

Tell the user, briefly:
- The course folder and the GitHub URL
- Chapters per part and total words, sources consulted and read in full and how many were book-grade, concepts validated by quorum, editor cycles and any findings left open
- Whether the innovation chapter ran and why
- Any assumptions the author made that the user may want to revisit
- The files to upload: absolute paths of `dist/<slug>.pdf` and `dist/<slug>.md`, page count of the PDF, and that answers are in `99-answers.md` on GitHub (deliberately not in the bundle unless `--with-answers` was used)
