# Editor rubric

Applied to one chapter at a time by the `book-editor` agent. Each row is a finding with
severity. The chapter ships when there are no critical findings and at most two
significant ones, and after at most two revision cycles.

| id | sev | check |
|---|---|---|
| plan-1 | critical | The chapter delivers the plan's Purpose: a reader can now do the stated thing. |
| plan-2 | significant | Every concept in "Concepts introduced" is defined here; every "Concepts used" was defined in an earlier chapter (check `continuity.md`). |
| plan-3 | significant | The examples named in the plan appear; none is replaced by a vaguer one. |
| ped-1 | critical | Opens inside a concrete situation; the term is not defined before the problem is felt. |
| ped-2 | critical | The main procedure or model is shown applied step by step with intermediate states, not just stated. |
| ped-3 | significant | At least two examples per principle, at least one real with real figures traceable to `sources.md`. |
| ped-4 | significant | "Where it breaks" names a real limit and the strongest counter-view, not a strawman. |
| ped-5 | significant | Each section motivates before it mechanises; examples follow the concept they illustrate. |
| ped-6 | minor | Summary bullets are standalone claims; exercises progress from recall to apply to own case. |
| pf-1 | critical | Parts I and II: no tool, vendor, product, library or language, including in examples and asides. Part III: each tool tied to a principle chapter by number and says what it hides. |
| pf-2 | significant | Pseudocode is language-neutral and readable as plain procedure. |
| voice-1 | critical | No template-slot headings; no meta-commentary; no recap endings. |
| voice-2 | significant | `lint_prose.py` reports 0 errors (banned constructions, dashes, AI vocabulary over limit). |
| voice-3 | significant | Prose, not bullets, carries the explanation; bullets only for true lists. |
| voice-4 | minor | Sentence and paragraph rhythm vary; no three-alike runs; "you" person held. |
| cont-1 | significant | Terminology matches `continuity.md`; running example facts unchanged; forward references paid or recorded. |
| cont-2 | minor | Transitions bridge to the next chapter's problem where the outline expects it. |
| src-1 | critical | Every number, named study, quote or named framework in the chapter has an entry in `sources.md` under this chapter. Nothing invented. |
| src-2 | significant | No URL, "according to a blog", or citation clutter in running text. |
| len-1 | minor | Within 25% of the plan's word budget. |

Output format for the editor: a findings list `id | sev | location (heading or first words) | what is wrong | what to do`, then a one-line verdict `SHIP` or `REVISE`, then, for REVISE, the three most important fixes in priority order.
