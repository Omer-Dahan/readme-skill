# Render check: measure the page, do not trust the source

The lint reads text; the page applies the Unicode bidi algorithm, glyph widths and the browser's
font fallbacks. Every defect below was invisible in the source and obvious in a measurement.

## What to measure

1. **Visual order of a mixed Hebrew/Latin line.** Take the text node of the line and read the x
   coordinate of each character, then sort by x: the resulting string is what the reader sees.
   Reading RTL text through that list gives it reversed, which is correct; what matters is where the
   Latin and numeric runs land relative to the Hebrew.
2. **Closed ASCII boxes.** Compare the x of the right border on every line against the top border.
   Any difference means the box looks ragged.
3. **Glyph widths inside a box.** An emoji is not one cell: measured 16.98px for 🌕 against 8.17px for
   a monospace character, so a box padded by character count drifts by the number of emoji.
4. **Badges.** Compare the rendered `<img>` width with the SVG's declared width, and the SVG's
   `textLength` with the natural width of the label (`canvas.measureText` with the same font stack).
   A label whose natural width is far below `textLength` is stretched; a flag emoji has no glyph on
   Windows and renders as the letters "IL".

## Procedure (any agent with a browser tool)

Open the rendered page (GitHub once pushed, or a local Markdown preview) and run something
equivalent to this in its devtools console or scripted browser:

```js
(() => {
  const pre = [...document.querySelectorAll('article pre')].find(p => p.textContent.includes('<a Hebrew word>'));
  const tn = [...pre.querySelector('code').childNodes].find(n => n.nodeType === 3);
  const s = tn.nodeValue, items = [];
  for (let i = 0; i < s.length; i++) {
    const r = document.createRange(); r.setStart(tn, i); r.setEnd(tn, i + 1);
    const b = r.getBoundingClientRect();
    items.push({ ch: s[i], x: b.left, xe: b.right, y: Math.round(b.top) });
  }
  const lines = {};
  items.forEach(it => { (lines[it.y] = lines[it.y] || []).push(it); });
  return Object.keys(lines).sort((a, b) => a - b).map(y => {
    const arr = lines[y];
    const vis = arr.slice().sort((a, b) => a.x - b.x).map(a => a.ch).join('');
    const left = Math.min(...arr.map(a => a.x)).toFixed(1);
    const right = Math.max(...arr.map(a => a.xe)).toFixed(1);
    return 'right=' + right + ' | ' + vis;
  }).join('\n');
})()
```

The line list is the evidence: keep the raw output in the report.

## Result of the round that produced this reference

A README source looked correct and the lint was clean. The rendered page showed:

- logical `⚡ מהירות: 5.4MB/s` rendered as `⚡ 5.4 :מהירותMB/s` — the number moved left of the Hebrew
  label and the unit stuck to it, because a hand-typed mock omits the LRM (U+200E) the real formatter
  emits after each Hebrew label;
- logical `🎬 סרטון יוטיוב (03:45)` rendered with mirrored parentheses: `🎬 )03:45( ...`;
- box borders: the top border ended at x=594.9 while content lines ended at 586.8-595.6 and the
  emoji bar line overshot to 601.5.

Fix that worked: generate the block from the formatter's own output (LRM marks included), delete the
box borders, and note above the block that it is generated, not typed.
