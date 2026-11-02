#!/usr/bin/env node
// Render every ```mermaid block in a course folder to SVG with beautiful-mermaid.
// Usage: node scripts/render_diagrams.mjs courses/<slug> [--theme github-light] [--ascii]
// Output: courses/<slug>/diagrams/<chapter>-<n>.svg  (and .txt with --ascii)
// The SVGs are flattened: CSS custom properties and color-mix() are resolved to
// plain colours so rsvg-convert / LaTeX / typst render them correctly (unflattened,
// every shape comes out black). Chapters keep their mermaid blocks for GitHub.
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

// ---- colour helpers -------------------------------------------------------
const hexToRgb = h => { h = h.replace("#", ""); if (h.length === 3) h = [...h].map(c => c + c).join(""); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
const rgbToHex = ([r, g, b]) => "#" + [r, g, b].map(v => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, "0")).join("");
const mix = (a, pa, b) => { const A = hexToRgb(a), B = hexToRgb(b); const p = pa / 100; return rgbToHex(A.map((v, i) => v * p + B[i] * (1 - p))); };

// Resolve var(--x[, fallback]) and color-mix(in srgb, C P%, C2) against a variable map
function resolveExpr(expr, vars, depth = 0) {
  if (depth > 20) return expr;
  let out = expr.trim();
  // innermost var()
  out = out.replace(/var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*(?:\([^()]*\))?[^()]*))?\)/g, (_, name, fb) =>
    vars[name] !== undefined ? resolveExpr(vars[name], vars, depth + 1) : (fb !== undefined ? resolveExpr(fb, vars, depth + 1) : "#000000"));
  // color-mix with two colours, one percentage
  out = out.replace(/color-mix\(\s*in\s+srgb\s*,\s*(#[0-9a-fA-F]{3,8})\s+(\d+(?:\.\d+)?)%\s*,\s*(#[0-9a-fA-F]{3,8})\s*\)/g, (_, c1, p, c2) => mix(c1, parseFloat(p), c2));
  out = out.replace(/color-mix\(\s*in\s+srgb\s*,\s*(#[0-9a-fA-F]{3,8})\s*,\s*(#[0-9a-fA-F]{3,8})\s+(\d+(?:\.\d+)?)%\s*\)/g, (_, c1, c2, p) => mix(c2, parseFloat(p), c1));
  if (out !== expr && /var\(|color-mix\(/.test(out)) return resolveExpr(out, vars, depth + 1);
  return out;
}

function flattenSvg(svg) {
  const vars = {};
  // 1. variables declared on the root style attribute (--bg, --fg, ...)
  const rootStyle = svg.match(/<svg[^>]*\sstyle="([^"]*)"/);
  if (rootStyle) for (const m of rootStyle[1].matchAll(/(--[\w-]+)\s*:\s*([^;]+)/g)) vars[m[1]] = m[2].trim();
  // 2. derived variables declared in <style> blocks
  for (const sm of svg.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g))
    for (const m of sm[1].matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)) if (vars[m[1]] === undefined) vars[m[1]] = m[2].trim();
  // 3. substitute everywhere outside <style>, then strip the variable rules and the web-font import
  let out = svg.replace(/var\([^()]*(?:\([^()]*\))?[^()]*\)/g, m => resolveExpr(m, vars));
  out = out.replace(/color-mix\([^()]*\)/g, m => resolveExpr(m, vars));
  out = out.replace(/<style[^>]*>([\s\S]*?)<\/style>/g, (_, css) => {
    css = css.replace(/@import[^;]+;/g, "")
             .replace(/--[\w-]+\s*:\s*[^;]+;/g, "")
             .replace(/font-family:\s*'Inter'[^;]*;/g, "font-family: 'DejaVu Sans', 'Helvetica', 'Arial', sans-serif;");
    css = css.replace(/var\([^()]*(?:\([^()]*\))?[^()]*\)/g, m => resolveExpr(m, vars)).replace(/color-mix\([^()]*\)/g, m => resolveExpr(m, vars));
    return `<style>${css}</style>`;
  });
  // root background
  out = out.replace(/<svg([^>]*)\sstyle="[^"]*"/, (_, a) => `<svg${a} style="background:${vars["--bg"] || "#ffffff"}"`);
  return out;
}

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
      const svg = flattenSvg(renderMermaidSVG(src, theme));
      if (/var\(|color-mix\(/.test(svg)) throw new Error("unresolved CSS variables remain");
      writeFileSync(join(out, `${stem}.svg`), svg);
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
