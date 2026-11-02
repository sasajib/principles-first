#!/usr/bin/env python3

Usage: python3 scripts/build_course.py courses/<slug> [--with-answers] [--formats md,pdf,tex]

Writes to courses/<slug>/dist/:
  <slug>.md    one Markdown file: title page, how to study, every chapter in order, sources.
               Every Mermaid diagram is converted to a Unicode/ASCII drawing in a code block,
               so the file is self-contained and readable by any parser (no images, no Mermaid).
  <slug>.pdf   via pandoc + typst (fallback lualatex/xelatex). Every Mermaid diagram becomes a PNG image
               (SVG from beautiful-mermaid -> PNG via rsvg-convert), ASCII if conversion fails.
  <slug>.tex   LaTeX source of the same document, images in dist/diagrams/.
  diagrams/    PNG (and SVG) of every diagram, named <chapter>-<n>.png.
scripts/render_diagrams.mjs is run first when node_modules/beautiful-mermaid exists.
The answer key (99-answers.md) is left out unless --with-answers is given, so a tutor
reading the file cannot hand out answers.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    folder = Path(args[0]).expanduser().resolve()
    with_answers = "--with-answers" in sys.argv
    formats = {"md", "pdf", "tex"}
    for a in sys.argv[1:]:
        if a.startswith("--formats="):
            formats = set(a.split("=", 1)[1].split(","))
    if "--formats" in sys.argv:
        formats = set(sys.argv[sys.argv.index("--formats") + 1].split(","))

    manifest = json.loads((folder / "course.json").read_text())
    slug = manifest["slug"]
    title = manifest.get("title", slug)
    phases = manifest["phases"]
    order = (list(phases.get("problems", [])) + list(phases.get("principles", []))
             + list(phases.get("tools", [])) + list(phases.get("capstone", [])))
    extra = sorted(p.name for p in folder.glob("[0-9][0-9]-*.md")
                   if p.name not in order and not p.name.startswith(("00-", "99-")))
    order += extra  # e.g. the innovation chapter

    dist = folder / "dist"
    dist.mkdir(exist_ok=True)
    root = Path(__file__).resolve().parent.parent
    if (root / "node_modules" / "beautiful-mermaid").exists() and shutil.which("node"):
        subprocess.run(["node", str(root / "scripts" / "render_diagrams.mjs"), str(folder)],
                       capture_output=True, text=True)
    dist_dg = dist / "diagrams"
    dist_dg.mkdir(exist_ok=True)
    if (folder / "diagrams").exists() and shutil.which("rsvg-convert"):
        for svg in sorted((folder / "diagrams").glob("*.svg")):
            png = dist_dg / (svg.stem + ".png")
            shutil.copy(svg, dist_dg / svg.name)
            subprocess.run(["rsvg-convert", "-z", "2", "-b", "white", "-o", str(png), str(svg)],
                           capture_output=True)

    parts: list[str] = []
    parts.append(f"---\ntitle: \"{title}\"\nsubtitle: \"A principles-first course\"\n"
                 f"date: \"{manifest.get('generated_at', '')}\"\nlang: {manifest.get('language', 'en')}\n"
                 f"toc: true\ntoc-depth: 2\nnumbersections: false\n---\n")
    readme = (folder / "00-README.md").read_text()
    readme = re.sub(r"^# .*\n", "", readme, count=1)  # pandoc title block carries the title
    readme = re.sub(r"^## Files\s*$.*?(?=^## |\Z)", "", readme, flags=re.M | re.S)  # folder listing is meaningless in a bundle
    parts.append(readme.strip() + "\n\n\\newpage\n")

    phase_titles = {}
    for name, label in (("problems", "Phase 1 — The problems"), ("principles", "Phase 2 — The principles"),
                        ("tools", "Phase 3 — The tools"), ("capstone", "Capstone")):
        for f in phases.get(name, []):
            phase_titles.setdefault(f, label)
    for f in extra:
        phase_titles.setdefault(f, "Phase 3 — The tools")

    last_phase = None
    for fname in order:
        p = folder / fname
        if not p.exists():
            print(f"warning: {fname} listed but missing", file=sys.stderr)
            continue
        ph = phase_titles.get(fname)
        if ph != last_phase:
            parts.append(f"\n# {ph}\n")
            last_phase = ph
        md = p.read_text().strip()
        md = re.sub(r"^# ", "## ", md, count=1, flags=re.M)          # chapter title one level down
        md = re.sub(r"^## (The principle|Walkthrough|Where it breaks|Check yourself|Do it by hand|Sources)\s*$",
                    r"### \1", md, flags=re.M)
        parts.append(md + "\n\n\\newpage\n")

    if with_answers and (folder / "99-answers.md").exists():
        ans = (folder / "99-answers.md").read_text().strip()
        ans = re.sub(r"^# .*\n", "", ans, count=1)
        parts.append("\n# Appendix A — Answers\n\n" + ans + "\n\n\\newpage\n")
    if (folder / "sources.md").exists():
        src = (folder / "sources.md").read_text().strip()
        src = re.sub(r"^# .*\n", "", src, count=1)
        parts.append("\n# Appendix — Sources\n\n" + src + "\n")

    merged = "\n".join(parts)
    merged = re.sub(r"```pseudo(code)?\s*\n", "```text\n", merged)  # pandoc has no 'pseudo' lexer

    # Locate each mermaid block's chapter so it can be matched to diagrams/<chapter>-<n>
    counters: dict[str, int] = {}
    chapter_of_pos: list[tuple[int, str]] = []
    for m in re.finditer(r"^## (\d+)\. ", merged, flags=re.M):
        chapter_of_pos.append((m.start(), m.group(1).zfill(2)))

    def chapter_at(pos: int) -> str | None:
        cur = None
        for start, num in chapter_of_pos:
            if start <= pos:
                cur = num
            else:
                break
        return cur

    def ascii_render(src: str) -> str:
        try:
            out = subprocess.run(
                ["node", "-e",
                 "import('beautiful-mermaid').then(m=>{let s='';process.stdin.on('data',d=>s+=d).on('end',()=>process.stdout.write(m.renderMermaidASCII(s)))})"],
                input=src, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent), timeout=60)
            return out.stdout if out.returncode == 0 and out.stdout.strip() else src
        except Exception:
            return src

    ascii_cache: dict[str, str] = {}

    def make_repl(mode: str):
        def repl(m: re.Match) -> str:
            num = chapter_at(m.start())
            counters[num] = counters.get(num, 0) + 1
            src = m.group(1)
            if mode == "image" and num:
                cands = sorted(dist_dg.glob(f"{num}-*-{counters[num]}.png"))
                if cands:
                    return f"![]({cands[0].as_posix()}){{ width=85% }}\n"
            if src not in ascii_cache:
                ascii_cache[src] = ascii_render(src).rstrip()
            return "```text\n" + ascii_cache[src] + "\n```\n"
        return repl

    mermaid_re = r"```mermaid\s*\n(.*?)```\n?"
    counters.clear()
    md_out = re.sub(mermaid_re, make_repl("ascii"), merged, flags=re.S)
    md_path = dist / f"{slug}.md"
    if "md" in formats:
        md_path.write_text(md_out.replace("\\newpage\n", ""))
        print(f"wrote {md_path}")

    if not (formats & {"pdf", "tex"}):
        return 0
    if not shutil.which("pandoc"):
        print("pandoc not found; install it for pdf/tex (sudo pacman -S pandoc texlive-luatex)", file=sys.stderr)
        return 1

    counters.clear()
    pdf_md = re.sub(mermaid_re, make_repl("image"), merged, flags=re.S)
    pdf_src = dist / f".{slug}.pandoc.md"
    pdf_src.write_text(pdf_md if not shutil.which("typst") else pdf_md.replace("\\newpage\n", ""))

    # PDF engine: typst (single static binary, bundled fonts, unicode-safe) preferred;
    # lualatex / xelatex as fallbacks. The .tex output always comes from pandoc itself.
    if shutil.which("typst"):
        engine_args = ["--pdf-engine=typst", "-V", "papersize=a4", "-V", "margin-x=2.2cm", "-V", "margin-y=2.2cm"]
    else:
        engine = "lualatex" if shutil.which("lualatex") else "xelatex"
        engine_args = [f"--pdf-engine={engine}", "-V", "papersize=a4", "-V", "geometry:margin=2.2cm",
                       "-V", "mainfont=DejaVu Serif", "-V", "monofont=DejaVu Sans Mono", "-V", "colorlinks=true"]
    common = ["pandoc", str(pdf_src), "--from", "markdown+raw_tex", "--toc", "--resource-path", str(folder)]
    tex_args = ["--standalone", "-V", "papersize=a4", "-V", "geometry:margin=2.2cm", "-V", "colorlinks=true"]
    rc = 0
    if "tex" in formats:
        tex = dist / f"{slug}.tex"
        r = subprocess.run(common + tex_args + ["-o", str(tex)], capture_output=True, text=True)
        print(f"wrote {tex}" if r.returncode == 0 else f"tex failed: {r.stderr[-800:]}")
        rc |= r.returncode
    if "pdf" in formats:
        pdf = dist / f"{slug}.pdf"
        r = subprocess.run(common + engine_args + ["-o", str(pdf)], capture_output=True, text=True)
        print(f"wrote {pdf}" if r.returncode == 0 else f"pdf failed: {r.stderr[-1200:]}")
        rc |= r.returncode
    pdf_src.unlink(missing_ok=True)
    return 1 if rc else 0


if __name__ == "__main__":
    sys.exit(main())
