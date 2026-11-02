#!/usr/bin/env node
// Render every ```mermaid block in a course folder to SVG with beautiful-mermaid.
// Usage: node scripts/render_diagrams.mjs courses/<slug> [--theme github-light] [--ascii]
// Output: courses/<slug>/diagrams/<chapter>-<n>.svg  (and .txt with --ascii)
// the SVGs are for PDFs, static sites and readers without Mermaid support.
import { readdirSync, readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join, basename, resolve } from "node:path";
import { renderMermaidSVG, renderMermaidASCII, THEMES } from "beautiful-mermaid";

const args = process.argv.slice(2);
const folder = args.find(a => !a.startsWith("--"));
if (!folder) { console.error("usage: render_diagrams.mjs courses/<slug> [--theme name] [--ascii]"); process.exit(2); }
const themeName = args.includes("--theme") ? args[args.indexOf("--theme") + 1] : "github-light";
const theme = THEMES[themeName];
if (!theme) { console.error(`unknown theme '${themeName}'. Available: ${Object.keys(THEMES).join(", ")}`); process.exit(2); }
const wantAscii = args.includes("--ascii");

const dir = resolve(folder);
const out = join(dir, "diagrams");
let total = 0, failed = 0;
for (const f of readdirSync(dir).filter(f => /^\d\d-.*\.md$/.test(f)).sort()) {
  const md = readFileSync(join(dir, f), "utf8");
  const blocks = [...md.matchAll(/```mermaid\s*\n([\s\S]*?)```/g)].map(m => m[1]);
  blocks.forEach((src, i) => {
    total++;
    const stem = `${basename(f, ".md")}-${i + 1}`;
    try {
      if (!existsSync(out)) mkdirSync(out, { recursive: true });
      writeFileSync(join(out, `${stem}.svg`), renderMermaidSVG(src, theme));
      if (wantAscii) writeFileSync(join(out, `${stem}.txt`), renderMermaidASCII(src));
      console.log(`ok    ${stem}.svg`);
    } catch (e) {
      failed++;
      console.log(`FAIL  ${f} block ${i + 1}: ${e.message.split("\n")[0]}`);
    }
  });
}
console.log(`${total - failed}/${total} diagrams rendered to ${out}`);
process.exit(failed ? 1 : 0);
