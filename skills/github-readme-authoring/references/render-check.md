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

## Mermaid diagrams (a diagram is code; parse it)

A diagram that fails to parse is worse than no diagram: the reader gets a raw error box. GitHub
shows it in the DOM as a sibling of the `<pre lang="mermaid">` element:

```
Unable to render rich display
Parse error on line 10: ...: SSRF guard; direct-link engine also do
```

Validate before publishing by loading the renderer and parsing each block with it (a blank page
plus the CDN build is enough):

```js
const inject = (src) => new Promise((res, rej) => {
  const s = document.createElement('script'); s.src = src;
  s.onload = () => res(true); s.onerror = () => rej(new Error('load fail'));
  document.head.appendChild(s);
});
await inject('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js');
try {
  await mermaid.parse(block);
  console.log('OK');
} catch (e) {
  console.log('FAIL -> ' + String(e.message).replace(/\n/g, ' | ').slice(0, 220));
}
```

Measured failure (media-bot-v2 README, 17/10/2026): one `;` inside a `stateDiagram-v2` description
(`SSRF guard; direct-link engine ...`) aborted the whole block at line 10 - a semicolon is a
statement separator in that diagram type. Replacing it with a comma made the block parse. The same
block's `&` characters and `->` inside descriptions parsed fine, so do not "clean up" those; test
the actual variant instead of guessing which character is at fault.

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
