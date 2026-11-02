#!/usr/bin/env python3
"""Prose linter for principles-first chapters. Counts what references/writing-rules.md bans.

Usage: python3 scripts/lint_prose.py <chapter.md | course folder> [--json]
Exit 1 when any error-level limit is exceeded.

Errors:  banned constructions (limit 0), em/en dashes (> 2 per chapter),
         AI vocabulary (> 1 per 1000 words), meta-commentary (limit 0),
         template-slot headings (limit 0)
Warnings: hedges (> 3 per 1000 words), three consecutive sentences of near-equal
         length, bold used mid-sentence more than 6 times, bullet-heavy body (> 35% of
         non-empty lines are list items outside Summary/Exercises)
Code blocks, inline code and URLs are ignored.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

AI_VOCAB = [
    "delve", "tapestry", "nuanced", "multifaceted", "testament to", "pivotal", "underscores",
    "underscore the", "fosters", "foster a", "navigate the", "navigating the", "paramount",
    "synergy", "robust", "leverage", "leveraging", "transformative", "holistic", "embark",
    "realm", "landscape", "cornerstone", "comprehensive", "seamlessly", "empower", "empowers",
    "crucial", "vital", "utilize", "utilizing", "unlock", "harness", "showcase", "vibrant",
    "game-changer", "game changer", "elevate", "journey", "ever-evolving", "in today's world",
    "a world where",
]
BANNED = [
    r"\bnot (?:just|only|merely|simply) [^.;:]{1,60}?,? but (?:also )?",
    r"\bit'?s not (?:about )?[^.;:]{1,50}?[,;] it'?s\b",
    r"\bthis (?:does not|doesn't|isn't|is not) mean [^.]{1,80}\. it (?:means|is)\b",
    r"\blet'?s (?:dive|explore|break this down|take a look|unpack|get started)",
    r"\bhere'?s the thing\b", r"\bthe truth is\b", r"\breal talk\b",
    r"\bhere'?s what you need to know\b", r"\bhonestly\?", r"^look,", r"\bthe reality is\b",
    r"\bit (?:is|'s) (?:important|worth) (?:to note|noting|mentioning)\b",
    r"\bas we can see\b", r"\bas mentioned (?:earlier|above|before)\b",
    r"\bat the end of the day\b", r"\bin essence\b", r"\bin summary\b", r"\bin conclusion\b",
    r"\bfirst and foremost\b", r"\bit goes without saying\b",
    r"\bto be clear\b", r"\bdon'?t get me wrong\b", r"\bi'?m not saying\b",
    r"\bsome might (?:say|argue)\b", r"\bone might be tempted\b", r"\byou might think\b",
    r"\bthe real question is\b", r"\bat its core\b", r"\bwhat really matters\b",
    r"\bthe heart of the matter\b", r"\bis the (?:language|currency|architecture) of\b",
    r"\bread that again\b", r"\blet that sink in\b", r"\bthat (?:is|'s) the real win\b",
    r"\bthis (?:matters|changes everything)\.", r"\b\w+\. \w+\. \w+\.(?= [A-Z])",
]
META = [
    r"\bin this (?:chapter|section|book),? (?:we|you|I)\b", r"\bthis chapter (?:will|covers|explores|introduces)\b",
    r"\bwe (?:will|'ll) (?:now |then )?(?:look at|explore|cover|discuss|see|examine)\b",
    r"\bas (?:discussed|noted|described|shown) (?:in|above|earlier|previously)\b",
    r"\bthe (?:next|following) (?:section|chapter) (?:will|covers|discusses)\b",
    r"\bnow that we (?:have|'ve)\b", r"\bwith that in mind\b",
]
HEDGES = ["quite", "rather", "somewhat", "essentially", "basically", "generally", "typically",
          "usually", "possibly", "potentially", "arguably", "presumably", "seemingly",
          "apparently", "in a sense", "to some extent", "to a degree"]
SLOT_HEADINGS = ["the principle", "walkthrough", "where it breaks", "check yourself", "do it by hand",
                 "the problem", "introduction", "overview", "conclusion", "key takeaways", "sources"]


def strip(md: str) -> str:
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = re.sub(r"`[^`]*`", "", md)
    md = re.sub(r"\(https?://[^)]*\)", "", md)
    md = re.sub(r"https?://\S+", "", md)
    return md


def sentences(text: str) -> list[str]:
    text = re.sub(r"^#.*$", "", text, flags=re.M)
    text = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", text, flags=re.M)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", text.replace("\n", " "))
    return [p.strip() for p in parts if len(p.split()) >= 3]


def lint_file(path: Path) -> dict:
    raw = path.read_text()
    text = strip(raw)
    words = max(len(re.findall(r"\b\w+\b", text)), 1)
    per_k = lambda n: n * 1000 / words
    errors, warnings = [], []

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    dashes = [line_of(m.start()) for m in re.finditer(r"[—–]| -- ", text)]
    if len(dashes) > 2:
        errors.append(f"em/en dashes: {len(dashes)} (limit 2) at lines {dashes[:8]}")

    hits = []
    for pat in BANNED:
        for m in re.finditer(pat, text, flags=re.I | re.M):
            hits.append((line_of(m.start()), m.group(0).strip()[:50]))
    for ln, h in sorted(set(hits)):
        errors.append(f"banned construction line {ln}: '{h}'")

    meta = []
    for pat in META:
        for m in re.finditer(pat, text, flags=re.I):
            meta.append((line_of(m.start()), m.group(0)[:50]))
    for ln, h in sorted(set(meta)):
        errors.append(f"meta-commentary line {ln}: '{h}'")

    vocab = []
    for w in AI_VOCAB:
        for m in re.finditer(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text, flags=re.I):
            vocab.append((line_of(m.start()), w))
    if per_k(len(vocab)) > 1.0:
        errors.append(f"AI vocabulary: {len(vocab)} in {words} words (limit 1/1000): {sorted(set(v for _, v in vocab))[:10]}")
    elif vocab:
        warnings.append(f"AI vocabulary present ({len(vocab)}): {sorted(set(v for _, v in vocab))}")

    for m in re.finditer(r"^(#{2,3})\s+(.*)$", raw, flags=re.M):
        title = m.group(2).strip().lower().rstrip(".:")
        if title in SLOT_HEADINGS and title not in ("sources",):
            errors.append(f"template-slot heading '{m.group(2).strip()}' (name the content instead)")
        if title == "sources":
            errors.append("chapter contains a '## Sources' section; sources belong in sources.md")

    hedges = []
    for w in HEDGES:
        hedges += [line_of(m.start()) for m in re.finditer(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text, flags=re.I)]
    if per_k(len(hedges)) > 3.0:
        warnings.append(f"hedges: {len(hedges)} in {words} words (limit 3/1000)")

    sents = sentences(text)
    lens = [len(s.split()) for s in sents]
    runs = sum(1 for i in range(len(lens) - 2) if max(lens[i:i+3]) - min(lens[i:i+3]) <= 2 and lens[i] >= 8)
    if runs > 2:
        warnings.append(f"{runs} runs of three near-equal-length sentences; vary rhythm")

    mid_bold = len(re.findall(r"(?<!^)(?<!\n)\*\*[^*\n]{1,40}\*\*", text))
    if mid_bold > 6:
        warnings.append(f"bold used {mid_bold} times mid-text; bold is for first definitions only")

    body = re.split(r"^## (?:Summary|Exercises)\s*$", raw, flags=re.M)[0]
    lines = [l for l in strip(body).splitlines() if l.strip()]
    bullets = [l for l in lines if re.match(r"^\s*(?:[-*]|\d+\.)\s+", l)]
    if lines and len(bullets) / len(lines) > 0.35:
        warnings.append(f"bullet-heavy body: {len(bullets)}/{len(lines)} lines are list items; explain in prose")

    return {"file": str(path), "words": words, "errors": errors, "warnings": warnings}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    target = Path(args[0]).expanduser().resolve()
    files = sorted(target.glob("[0-9][0-9]-*.md")) if target.is_dir() else [target]
    files = [f for f in files if not f.name.startswith(("00-", "99-"))]
    results = [lint_file(f) for f in files]
    if "--json" in sys.argv:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            for w in r["warnings"]:
                print(f"WARN  {Path(r['file']).name}: {w}")
            for e in r["errors"]:
                print(f"ERROR {Path(r['file']).name}: {e}")
        n_err = sum(len(r["errors"]) for r in results)
        n_warn = sum(len(r["warnings"]) for r in results)
        print(f"{'FAIL' if n_err else 'PASS'}: {n_err} error(s), {n_warn} warning(s) in {len(results)} chapter(s)")
    return 1 if any(r["errors"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
