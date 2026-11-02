# How a chapter is built

What a reader of a good instructional book meets, in order, and how to write each part.
Based on publisher guidance (Manning author resources: chapter plan, opening with
expectations, tiered headings, summary; Pragmatic: the reader is on a journey from
knowing little) and on the worked-example research (Sweller, Atkinson et al. 2000,
van Gog et al. 2010): novices learn more from studied step-by-step examples than from
unguided problem solving, and examples paired with self-explanation prompts transfer.

## 0. The chapter plan (written in the outline, before any prose)

For every chapter, one block in `outline.md`:

```
### <N>. <Working title>
Purpose: the one thing the reader can do after this chapter that they could not before.
Why now: which earlier chapter it depends on and what it unlocks later.
Problem scene: the concrete situation the chapter opens with (who, what goes wrong).
Principle: one sentence, stated as a rule a reader could apply.
Examples: 2-4, named, with the source each comes from; mark the running example if used.
Procedure or model: what the pseudocode / diagram / table will show.
Where it breaks: the limits and the strongest counter-view, with source.
Concepts introduced: terms defined here. Concepts used: terms from earlier chapters.
Exercises: 3-5 one-line ideas, at least one by hand with paper only.
Budget: <words>.
```

The plan is the contract. The editor checks the chapter against it.

## 1. Opening (two to five paragraphs, no heading)

Start inside the problem scene: a specific person, product or situation, and what goes
wrong. Make the reader feel the cost before naming the idea. Then one short paragraph
that says what the chapter gives them, in terms of what they will be able to do. Do not
write "in this chapter". Do not define the term yet.

Good: "The invoice went out on the third. On the thirtieth nothing had arrived, and the
developer who sent it had already drafted four versions of a reminder she could not bring
herself to send."
Bad: "Positioning is the set of decisions that gives buyers context."

## 2. Body sections (three to six, `##` headings that name content)

Each section carries one move of the argument. The default order for a principle:

1. **Intuition** through the scene or a second example: why the naive approach fails.
2. **The principle**, stated once, plainly, with a mental model or analogy that will be
   reused later in the book. Define the term here, in bold, once.
3. **The procedure or model**: pseudocode, a numbered procedure, a table or a diagram.
   Show it applied step by step to the scene, with intermediate states visible
   ("after step 2 the list has three entries: ..."). This is the worked example and it is
   the heart of the chapter; give it room.
4. **A second worked example** from a different domain or a real case from the sources,
   with its real numbers, so the reader sees the principle is general.
5. **Where it breaks**: limits, trade-offs, the strongest counter-view from the research,
   and how practitioners reconcile it. This is where a book earns trust.

Headings describe what the section shows, not the slot it fills: "The three questions a
buyer answers before reading", "Running the Bullseye on a product with 300 users",
"When a sharp segment is too sharp".

Transitions are sentences, not headings: the last sentence of a section points at the
next section's problem.

## 3. Summary (`## Summary`, four to seven bullets)

Each bullet is a complete claim the reader could repeat without the chapter: the rule,
the model, the limit. Not "we discussed positioning" but "Positioning is decided in
order: alternatives, attributes, value, segment, category, because each depends on the
one before."

## 4. Exercises (`## Exercises`, three to six, numbered)

Mixed difficulty, in this order: two or three recall and explain questions that can be
answered from memory; one or two apply-it problems with given data; one by-hand project
on the reader's own case with a rubric line ("done when ..."). No answers in the
chapter; model answers go in the answers appendix under the chapter title.
In Parts I and II the exercises need only paper. In Part III, "do it with the tool, then
name the principle each step applied".

## 5. Diagrams and code

One diagram when structure or flow is easier to see than to read; fewer than fifteen
nodes; a caption that states what to notice. Pseudocode blocks tagged `pseudo`, short,
with the data shown before and after. Part III may use real code; it is still minimal and
shows input and expected output.

## 6. Length

Part I chapters 2,000-3,000 words. Part II chapters 3,000-4,500 words, because the
worked examples live there. Part III chapters 2,500-4,000. Capstone 2,500-4,000.
A book at Standard depth is therefore 35,000-55,000 words, which is a real short book.
