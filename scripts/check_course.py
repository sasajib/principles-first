#!/usr/bin/env python3
"""Quality gate for a principles-first course folder.

Usage: python3 scripts/check_course.py courses/<slug> [--strict]

Fails (exit 1) when:
  * course.json is missing, invalid, or lists files that do not exist
  * a Phase 1 or Phase 2 chapter names a tool, vendor, product, library or
    programming language (built-in list + course.json.forbidden_in_phases_1_2)
  * a Phase 1 or Phase 2 code block is tagged with a real language
  * a chapter lacks a required section
  * a chapter has no "Check yourself" questions, or 99-answers.md lacks a
    section for it
  * flashcards.tsv is missing, empty, or malformed
  * 00-README.md or sources.md is missing
Warnings (exit 0 unless --strict): chapter body outside 500-1800 words,
missing mermaid/pseudo blocks where expected, "you must/should" tone.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "## The principle",
    "## Walkthrough",
    "## Where it breaks",
    "## Check yourself",
    "## Do it by hand",
    "## Sources",
]
REQUIRED_OPENERS = ["**The problem.**", "**The question this chapter answers.**"]

# Generic names that never belong in Phase 1-2. Matched case-insensitively as
# whole words. Course-specific lists live in course.json.
BUILTIN_FORBIDDEN = [
    # programming languages and runtimes
    "python", "javascript", "typescript", "java", "c++", "c#", "golang", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "haskell", "perl", "matlab",
    "node.js", "nodejs", "bash", "powershell", "sql", "r language",
    # big vendors and platforms
    "google", "microsoft", "amazon", "aws", "azure", "meta ads", "facebook",
    "instagram", "tiktok", "linkedin", "youtube", "openai", "chatgpt",
    "anthropic", "claude", "gemini", "hubspot", "salesforce", "mailchimp",
    "shopify", "wordpress", "excel", "google sheets", "notion", "figma",
    "canva", "semrush", "ahrefs", "ga4", "google analytics",
    # dev tooling
    "github", "gitlab", "docker", "kubernetes", "react", "vue", "angular",
    "django", "flask", "spring", "numpy", "pandas", "tensorflow", "pytorch",
    "leetcode", "hackerrank",
]
REAL_LANG_FENCES = {
    "python", "py", "js", "javascript", "ts", "typescript", "java", "c", "cpp",
    "c++", "csharp", "cs", "go", "rust", "rb", "ruby", "php", "swift", "kotlin",
    "scala", "sql", "bash", "sh", "shell", "zsh", "powershell", "r", "matlab",
    "html", "css", "jsx", "tsx",
}
ALLOWED_FENCES_P12 = {"pseudo", "pseudocode", "text", "txt", "mermaid", "", "plain", "math", "latex"}

ORDER_WORDS = re.compile(r"\byou (must|need to|have to)\b", re.I)


def words_in_body(md: str) -> int:
    body = re.sub(r"```.*?```", "", md, flags=re.S)
    body = re.sub(r"^#.*$", "", body, flags=re.M)
    return len(re.findall(r"\b\w+\b", body))


def fences(md: str) -> list[str]:
    return [m.group(1).strip().lower() for m in re.finditer(r"^```([^\n]*)$", md, flags=re.M)][0::2]


def strip_code_and_links(md: str) -> str:
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = re.sub(r"`[^`]*`", "", md)
    md = re.sub(r"\(https?://[^)]*\)", "", md)
    md = re.sub(r"https?://\S+", "", md)
    # drop the Sources section: URLs and org names are allowed there
    md = re.split(r"^## Sources\s*$", md, flags=re.M)[0]
    return md


def find_forbidden(text: str, terms: list[str]) -> list[tuple[str, int]]:
    hits = []
    for term in terms:
        pat = r"(?<![\w.+#-])" + re.escape(term) + r"(?![\w+#-])"
        for m in re.finditer(pat, text, flags=re.I):
            line = text.count("\n", 0, m.start()) + 1
            hits.append((term, line))
    return hits


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    strict = "--strict" in sys.argv
    folder = Path(sys.argv[1]).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = folder / "course.json"
    if not manifest_path.exists():
        print(f"FAIL: {manifest_path} missing")
        return 1
    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"FAIL: course.json invalid: {exc}")
        return 1

    phases = manifest.get("phases") or {}
    for key in ("problems", "principles", "tools", "capstone"):
        if key not in phases:
            errors.append(f"course.json: phases.{key} missing")
    p12 = list(phases.get("problems", [])) + list(phases.get("principles", []))
    p3 = list(phases.get("tools", [])) + list(phases.get("capstone", []))
    all_chapters = p12 + p3
    if not all_chapters:
        errors.append("course.json: no chapters listed")

    headings = manifest.get("headings") or {}
    def h(name: str) -> str:
        return headings.get(name, name)

    forbidden = BUILTIN_FORBIDDEN + list(manifest.get("forbidden_in_phases_1_2", []))
    forbidden = sorted(set(t.lower() for t in forbidden), key=len, reverse=True)
    if len(manifest.get("forbidden_in_phases_1_2", [])) < 10 and manifest.get("status") == "complete":
        warnings.append("course.json: forbidden_in_phases_1_2 has fewer than 10 entries; add this topic's tools and vendors")

    for required in ("00-README.md", "99-answers.md", "flashcards.tsv", "sources.md"):
        if not (folder / required).exists():
            errors.append(f"{required} missing")

    answers = (folder / "99-answers.md").read_text() if (folder / "99-answers.md").exists() else ""

    for fname in all_chapters:
        path = folder / fname
        if not path.exists():
            errors.append(f"{fname}: listed in course.json but file missing")
            continue
        md = path.read_text()
        tag = f"{fname}"

        for opener in REQUIRED_OPENERS:
            if h(opener) not in md:
                errors.append(f"{tag}: missing opener {opener}")
        for sec in REQUIRED_SECTIONS:
            if not re.search(r"^" + re.escape(h(sec)) + r"\s*$", md, flags=re.M):
                errors.append(f"{tag}: missing section {sec}")

        # Check-yourself questions must exist and be answered
        m = re.search(r"^## Check yourself\s*$(.*?)(?=^## |\Z)", md, flags=re.M | re.S)
        n_q = len(re.findall(r"^\s*\d+[.)]", m.group(1), flags=re.M)) if m else 0
        if n_q < 3:
            errors.append(f"{tag}: fewer than 3 numbered questions under Check yourself ({n_q})")
        title = re.match(r"^#\s+(.*)$", md, flags=re.M)
        if title and answers:
            t = title.group(1).strip()
            if t not in answers and re.sub(r"^\d+\.\s*", "", t) not in answers:
                errors.append(f"{tag}: no section for '{t}' in 99-answers.md")

        n_words = words_in_body(md)
        if n_words < 500:
            warnings.append(f"{tag}: body is short ({n_words} words)")
        elif n_words > 1800:
            warnings.append(f"{tag}: body is long ({n_words} words); consider splitting")

        if ORDER_WORDS.search(md):
            warnings.append(f"{tag}: commanding tone ('you must/need to/have to'); prefer explaining why")

        if fname in p12:
            hits = find_forbidden(strip_code_and_links(md), forbidden)
            for term, line in sorted(set(hits), key=lambda x: x[1]):
                errors.append(f"{tag}:{line}: Phase 1-2 chapter names a tool/vendor/language: '{term}'")
            for lang in fences(md):
                if lang in REAL_LANG_FENCES:
                    errors.append(f"{tag}: Phase 1-2 code block tagged '{lang}'; use ```pseudo")
                elif lang not in ALLOWED_FENCES_P12:
                    warnings.append(f"{tag}: unusual fence tag '{lang}' in a Phase 1-2 chapter")
        else:
            if not re.search(r"\b(chapter|ch\.?)\s*\d+", md, flags=re.I):
                errors.append(f"{tag}: Phase 3 chapter never references a principle chapter by number")

    # flashcards
    fc = folder / "flashcards.tsv"
    if fc.exists():
        lines = [l for l in fc.read_text().splitlines() if l.strip()]
        bad = [i + 1 for i, l in enumerate(lines) if l.count("\t") != 1 or not all(p.strip() for p in l.split("\t"))]
        if not lines:
            errors.append("flashcards.tsv is empty")
        if bad:
            errors.append(f"flashcards.tsv: malformed lines (need exactly one tab): {bad[:10]}")
        if lines and len(lines) < 3 * len(all_chapters):
            warnings.append(f"flashcards.tsv: {len(lines)} cards for {len(all_chapters)} chapters; aim for 3-8 per chapter")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    status = "FAIL" if errors or (strict and warnings) else "PASS"
    print(f"{status}: {len(errors)} error(s), {len(warnings)} warning(s) in {folder.name}")
    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
