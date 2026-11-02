# Writing rules

Read before drafting; the editor audits against this file. Adapted from
luquiluke/claude-book-skill `writing-rules.md` and blader/humanizer (both MIT),
trimmed to what a principles-first book needs. `scripts/lint_prose.py` counts the
mechanical items; the editor judges the rest.

## 1. The book is not a worksheet

- Headings name content ("Why the first channel is usually the wrong one"), never the
  template slot ("The principle", "Walkthrough"). The only fixed headings in a chapter
  are `## Summary` and `## Exercises` at the end.
- Explanations are prose. Bullets only for genuine lists (steps in order, a checklist
  the reader will reuse, a summary). A list of reasons becomes a paragraph that argues them.
- No meta-commentary. The book never narrates itself ("in this chapter we will",
  "as mentioned earlier", "let's explore"). The chapter opening may state what the
  reader will be able to do; nothing else announces itself.
- No recap endings. A section ends by landing its point or bridging to the next idea.
  The only recap is the `## Summary` list.
- Citations are invisible in the running text. Name a person or study inline only when
  the name carries information ("Dunford's five components", "Sharp's purchase data").
  Never "according to a blog post", never a URL in prose. Every load-bearing claim is
  recorded in `sources.md` under its chapter instead.

## 2. Concrete before abstract

- Open every concept with a specific situation the reader recognises, then the
  intuition, then the formal statement or procedure, then a worked example with its
  intermediate states, then where it breaks. Never definition first.
- At least two examples per principle, from different domains or sources, at least one
  of them real (from the research) with its real numbers. A running example may thread
  the book, but a chapter that only uses the running example is thin.
- Numbers and quotes come from sources. If a number is illustrative, say so in the
  sentence ("suppose 300 visitors"). Never present an invented figure as a finding.

## 3. Banned vocabulary (lint-counted, limit 1 per 1000 words)

delve, tapestry, nuanced, multifaceted, testament, pivotal, underscore (verb),
foster, navigate (metaphor), paramount, synergy, robust, leverage (verb),
transformative, holistic, embark, realm, landscape (metaphor), cornerstone,
comprehensive, seamlessly, empower, crucial, vital, utilize, unlock, harness,
showcase, vibrant, game-changer, elevate, journey (metaphor), ever-evolving,
in today's world, a world where.

## 4. Banned constructions (lint-counted, limit 0)

- Not X but Y, not just X but Y, it's not X, it's Y, X rather than Y as decoration,
  the split version ("This does not mean X. It means Y.").
- Staged openers: let's dive in, let's explore, here's the thing, the truth is,
  honestly, look, real talk, here's what you need to know.
- Filler scaffolding: it is important to note, it's worth noting, as we can see,
  as mentioned earlier, in other words (followed by restatement), at the end of the day,
  in essence, in summary, in conclusion, first and foremost, it goes without saying.
- Arguing with no one: to be clear, don't get me wrong, I'm not saying, some might say,
  one might be tempted to, you might think ... but.
- One-line closers that restate the paragraph ("That is the real win.", "Read that
  again.", "This matters."), rows of fragments, every. single. word.
- Deep-sounding sayings: the real question is, at its core, what really matters,
  the heart of the matter, X is the language/currency/architecture of Y.

## 5. Hedges (lint-counted, limit 3 per 1000 words)

quite, rather, somewhat, essentially, basically, generally, typically, usually,
possibly, potentially, arguably, presumably, seemingly, apparently, in a sense,
to some extent. Keep a hedge that carries real uncertainty ("this result has not been
replicated"); cut the ones that only soften.

## 6. Mechanics

- Em and en dashes: at most 2 per chapter. Use a comma, colon, full stop or parentheses.
- Bold only for a term on first definition. Never for emphasis. No italics for emphasis
  more than twice a chapter.
- Headings in sentence case. No emoji. No title-case lists of bold labels.
- Forced triads: three parallel items only when the meaning has three parts.
- Sentence rhythm: never three consecutive sentences within three words of the same
  length. Paragraphs vary between two and eight sentences.
- Person: "you" for the reader, "we" only when the reader and author act together in a
  walkthrough. Never "I".
- Contractions are fine. Write like a knowledgeable colleague explaining at a whiteboard.

## 7. Compression

- Explain each idea once. If an example has made the point, do not explain the point
  after it.
- A paragraph that restates the previous paragraph in different words is cut.
- Chapter word budgets are in the outline. More than 25% over budget means something
  is being explained twice; find it.

## 8. Principles-first (checked by `check_course.py`)

- Parts I and II name no tool, vendor, product, library or programming language.
  Describe the capability ("a place to see which page a visitor came from") instead.
- Pseudocode in Parts I and II uses fenced blocks tagged `pseudo`, written as numbered
  procedures or indented steps in plain words, never a real language's syntax.
- Every Part III tool is introduced by the principle it implements, with the chapter
  number, and the chapter says what the tool hides from the user.

## 9. Pre-flight (writer runs it, editor runs it again)

- [ ] `python3 scripts/lint_prose.py <chapter>` reports 0 errors
- [ ] No template-slot headings; headings name content
- [ ] Opens with a specific situation, not a definition
- [ ] Two or more examples per principle, at least one real with real numbers
- [ ] No section ends on a recap; no meta-commentary
- [ ] Every claim with a number or a name is in `sources.md` under this chapter
- [ ] Terminology matches `continuity.md`; forward references recorded there
- [ ] Word count within the outline's budget
