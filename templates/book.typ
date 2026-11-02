// Pandoc → Typst book template for principles-first-courses.
// Used by scripts/build_course.py via `pandoc --template templates/book.typ`.
// Heading levels as pandoc emits them from the merged Markdown:
//   level 1 = Part (own page), level 2 = Chapter (new page), level 3+ = sections.
#let conf(
  title: none, subtitle: none, authors: (), date: none, lang: "en", region: "US",
  abstract: none, abstract-title: none, keywords: (), thanks: none,
  margin: (x: 2.4cm, y: 2.6cm), paper: "a4", font: ("Libertinus Serif",), fontsize: 11pt,
  mathfont: (), codefont: ("DejaVu Sans Mono",), linestretch: 1.0, sectionnumbering: none,
  pagenumbering: "1", linkcolor: none, citecolor: none, filecolor: none, cols: 1, doc,
) = {
  set document(title: if title != none { title } else { "" })
  set page(paper: paper, margin: margin, numbering: none)
  set text(font: font, size: fontsize, lang: lang, region: region)
  set par(justify: true, leading: 0.72em, spacing: 1.05em, first-line-indent: 0em)
  show raw: set text(font: codefont, size: 0.86em)
  show raw.where(block: true): it => block(
    width: 100%, fill: luma(247), stroke: 0.5pt + luma(215), radius: 3pt, inset: 9pt, it)
  show link: set text(fill: rgb("#1f4e79"))
  set list(indent: 1em, spacing: 0.6em)
  set enum(indent: 1em, spacing: 0.6em)
  set table(inset: 6pt, stroke: (x, y) => if y == 0 { (bottom: 0.7pt + black) } else { (bottom: 0.3pt + luma(200)) })
  show table.cell.where(y: 0): strong
  show figure: set block(above: 1.4em, below: 1.4em)
  show quote: set pad(left: 1.5em)

  // ---- Title page ----
  page(numbering: none, margin: (x: 3cm, y: 5cm))[
    #v(1fr)
    #text(size: 2.4em, weight: "bold", hyphenate: false)[#title]
    #if subtitle != none { v(0.6em); text(size: 1.3em, fill: luma(80))[#subtitle] }
    #v(2em)
    #line(length: 30%, stroke: 0.6pt)
    #v(1fr)
    #if authors.len() > 0 { text(size: 1.05em)[#authors.map(a => a.name).join(", ")]; v(0.4em) }
    #if date != none { text(size: 0.95em, fill: luma(90))[#date] }
    #v(2cm)
  ]

  // ---- Front matter: contents ----
  set page(numbering: "i", footer: context align(center, text(size: 0.85em, counter(page).display("i"))))
  counter(page).update(1)
  show outline.entry.where(level: 1): it => { v(0.9em, weak: true); strong(it) }
  show outline.entry.where(level: 2): it => it
  outline(title: [Contents], depth: 2, indent: 1.2em)

  // ---- Headings ----
  // Part: own page, large, with "Part" label from the heading text itself
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(5cm)
    align(center)[
      #text(size: 1.9em, weight: "bold", hyphenate: false)[#it.body]
    ]
    pagebreak()
  }
  // Chapter: new page, number is part of the Markdown title ("3. Title")
  show heading.where(level: 2): it => {
    pagebreak(weak: true)
    v(1.5cm)
    block(below: 1.6em)[#text(size: 1.75em, weight: "bold", hyphenate: false)[#it.body]]
  }
  show heading.where(level: 3): it => block(above: 1.6em, below: 0.8em)[#text(size: 1.2em, weight: "bold")[#it.body]]
  show heading.where(level: 4): it => block(above: 1.2em, below: 0.6em)[#text(size: 1.02em, weight: "bold")[#it.body]]
  show heading.where(level: 5): it => block(above: 1em, below: 0.5em)[#text(size: 1em, style: "italic")[#it.body]]

  // ---- Body ----
  set page(numbering: pagenumbering,
    header: context {
      let h = query(heading.where(level: 2).before(here()))
      if h.len() > 0 and counter(page).get().first() > 1 {
        align(right, text(size: 0.82em, fill: luma(100), h.last().body))
        v(-0.5em); line(length: 100%, stroke: 0.3pt + luma(200))
      }
    },
    footer: context align(center, text(size: 0.9em, counter(page).display())))
  counter(page).update(1)
  if cols == 1 { doc } else { columns(cols, doc) }
}
