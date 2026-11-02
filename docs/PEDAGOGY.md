# Pedagogy

The author agent follows six rules. They are not style preferences; they are what the learning research supports, and the checker enforces the ones it can.

## 1. Problem before solution

Every chapter opens with a concrete situation and what goes wrong without the idea. A learner who knows what problem a concept solves can rederive it, recognise it in the wild, and judge when it does not apply. A learner who memorised the solution cannot. This is also why the first phase of every course is only problems.

## 2. Principles before tools

Phases 1 and 2 may not mention a tool, vendor, product, library or language. Tools change every few years; the principles they implement change every few decades. Learning the tool first produces people who can operate a dashboard but cannot explain why a campaign failed, or who can call a sort function but cannot reason about why it is slow. Pseudocode and procedures keep the reasoning visible.

Enforced by `scripts/check_course.py`: a built-in list of languages and big vendors, plus a per-course list the author writes into `course.json.forbidden_in_phases_1_2`.

## 3. Tools are a by-product

Phase 3 opens with a table mapping each principle to the tools that implement it. Every tool chapter says "this implements chapter N" and names what the tool hides from you. Enforced: Phase 3 chapters must reference a principle chapter by number.

## 4. Clear and concise

Short sentences, one idea per paragraph, a worked example over a definition, 700 to 1500 words of body per chapter. Longer chapters get split. The checker warns outside 500 to 1800 words and on commanding tone ("you must").

## 5. Active learning


Research behind it: an unrestricted chatbot during practice lowered unassisted exam scores by 17% versus no AI, while a hint-only tutor did not (Bastani et al., *Generative AI without guardrails can harm learning*, PNAS 2025). A one-step-at-a-time AI tutor roughly doubled gains over an active-learning class (Kestin et al., Scientific Reports 2025). Heavy reliance on AI for writing reduced recall and engagement (MIT Media Lab, 2025, small sample).

## 6. Evidence

The author reads real sources through parallel source-reader agents and tracks which claims appear in how many independent sources. Three or more: stated plainly. One: attributed and listed under "Single-source claims" in `sources.md`. Nothing is written from model memory alone.

## The innovation chapter, and why it is automatic

Fast-moving practice fields (marketing, product, management, applied AI) benefit from a closing chapter on open problems and unexplored intersections, because the frontier is where a practitioner adds value. Foundational fields (algorithms, mathematics, physics) do not; their frontier is research, not practice, and a speculative chapter would dilute a course about settled principles. The skill decides from the topic and the end goal, records the reason, and `--innovation on|off` overrides it.
