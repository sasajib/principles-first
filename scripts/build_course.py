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
    phases = manifest.get("parts") or manifest["phases"]
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
    parts.append(f"---\ntitle: \"{title}\"\nsubtitle: \"Problems first, principles second, tools last\"\n"
                 f"date: \"{manifest.get('generated_at', '')}\"\nlang: {manifest.get('language', 'en')}\n"
                 f"author: \"{manifest.get('author', 'principles-first-courses')}\"\n"
                 f"toc: true\ntoc-depth: 2\nnumbersections: false\n---\n")
    readme = (folder / "00-README.md").read_text()
    readme = re.sub(r"^# .*\n", "", readme, count=1)  # pandoc title block carries the title
    for sec in ("Files", "Innovation chapter", "Generation notes"):   # project meta, not book content
        readme = re.sub(r"^## " + sec + r"\s*$.*?(?=^## |\Z)", "", readme, flags=re.M | re.S)
    readme = re.sub(r"^## ", "### ", readme, flags=re.M)
    readme = "## Preface\n\n" + readme.strip()
    parts.append(readme + "\n\n\\newpage\n")

    phase_titles = {}
    for name, label in (("problems", "Part I — The problems"), ("principles", "Part II — The principles"),
                        ("tools", "Part III — The tools"), ("capstone", "Capstone")):
        for f in phases.get(name, []):
            phase_titles.setdefault(f, label)
    for f in extra:
        phase_titles.setdefault(f, "Part III — The tools")

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
        # sections one level down first, then the chapter title (so it is not demoted twice)
        md = re.sub(r"^#### ", "##### ", md, flags=re.M)
        md = re.sub(r"^### ", "#### ", md, flags=re.M)
        md = re.sub(r"^## ", "### ", md, flags=re.M)
        md = re.sub(r"^# ", "## ", md, count=1, flags=re.M)
        parts.append(md + "\n\n\\newpage\n")

    if with_answers and (folder / "99-answers.md").exists():
        ans = (folder / "99-answers.md").read_text().strip()
        ans = re.sub(r"^# .*\n", "", ans, count=1)
        ans = re.sub(r"^### ", "#### ", ans, flags=re.M); ans = re.sub(r"^## ", "### ", ans, flags=re.M)
        parts.append("\n## Answers to the exercises\n\n" + ans + "\n\n\\newpage\n")
    if (folder / "sources.md").exists():
        src = (folder / "sources.md").read_text().strip()
        src = re.sub(r"^# .*\n", "", src, count=1)
        src = re.sub(r"^### ", "#### ", src, flags=re.M); src = re.sub(r"^## ", "### ", src, flags=re.M)
        parts.append("\n## Notes and sources\n\n" + src + "\n")

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
                    # size from the SVG aspect ratio so tall diagrams fit one page:
                    # text block on A4 with 2.2cm margins is ~16.6cm x 25cm
                    width_cm = 15.0
                    svg = cands[0].with_suffix(".svg")
                    vb = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', svg.read_text()) if svg.exists() else None
                    if vb:
                        aspect = float(vb.group(2)) / max(float(vb.group(1)), 1e-6)
                        width_cm = min(15.0, 17.0 / aspect)
                    rel = cands[0].relative_to(dist).as_posix()
                    return f"![]({rel}){{ width={width_cm:.1f}cm }}\n"
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
    root_tpl = Path(__file__).resolve().parent.parent / "templates" / "book.typ"
    use_typst = bool(shutil.which("typst")) and root_tpl.exists()
    pdf_src = dist / f".{slug}.pandoc.md"
    if use_typst:
        # the book template draws its own contents page; drop pandoc's toc flag and raw LaTeX breaks
        pdf_md = re.sub(r"^toc(-depth)?:.*\n", "", pdf_md, flags=re.M).replace("\\newpage\n", "")
    pdf_src.write_text(pdf_md)

    # PDF: pandoc -> Typst source that imports templates/book.typ, compiled with typst in dist/
    # (so relative image paths resolve). Fallback: pandoc + lualatex/xelatex.
    common = ["pandoc", str(pdf_src), "--from", "markdown+raw_tex", "--toc", "--resource-path", str(folder)]
    tex_args = ["--standalone", "-V", "papersize=a4", "-V", "geometry:margin=2.2cm", "-V", "colorlinks=true"]
    engine_args = []
    if not use_typst:
        engine = "lualatex" if shutil.which("lualatex") else "xelatex"
        engine_args = [f"--pdf-engine={engine}", "-V", "papersize=a4", "-V", "geometry:margin=2.2cm",
                       "-V", "mainfont=DejaVu Serif", "-V", "monofont=DejaVu Sans Mono", "-V", "colorlinks=true"]
    rc = 0
    if "tex" in formats:
        tex = dist / f"{slug}.tex"
        r = subprocess.run(common + tex_args + ["-o", str(tex)], capture_output=True, text=True)
        print(f"wrote {tex}" if r.returncode == 0 else f"tex failed: {r.stderr[-800:]}")
        rc |= r.returncode
    if "pdf" in formats:
        pdf = dist / f"{slug}.pdf"
        if use_typst:
            shutil.copy(root_tpl, dist / "book.typ")
            typ = dist / f"{slug}.typ"
            r = subprocess.run(["pandoc", str(pdf_src), "--from", "markdown+raw_tex", "--to", "typst", "--standalone",
                                "-V", "template=book.typ", "-o", str(typ)], capture_output=True, text=True)
            if r.returncode == 0:
                r = subprocess.run(["typst", "compile", "--root", str(dist), typ.name, pdf.name],
                                   cwd=str(dist), capture_output=True, text=True)
            print(f"wrote {pdf}" if r.returncode == 0 else f"pdf failed: {r.stderr[-1500:]}")
        else:
            r = subprocess.run(common + engine_args + ["-o", str(pdf)], capture_output=True, text=True)
            print(f"wrote {pdf}" if r.returncode == 0 else f"pdf failed: {r.stderr[-1200:]}")
        rc |= r.returncode
    pdf_src.unlink(missing_ok=True)
    return 1 if rc else 0


if __name__ == "__main__":
    sys.exit(main())
