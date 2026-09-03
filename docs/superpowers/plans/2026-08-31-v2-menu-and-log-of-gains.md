# Version 2 — Menu and Log of Gains Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship v2 of bodyimprovement.club: a three-tab menu seated on the top edge of the content box, and a Log of Gains view inside that box rendering ten club activities from a placeholder data module.

**Architecture:** Three static HTML pages sharing one `style.css`, each duplicating a ~12-line shell (grain, wordmark, diet bowl, tab strip). Geometry is absolutely positioned inside a `.stage` scaled by `html { font-size }` so `1rem` = one Figma pixel, exactly as v1 does. Brush borders stay flattened SVG exports composited by a `.stage::before` overlay that paints above all children; the overlay's layer list is switched per page by a `.stage--start` / `.stage--log` / `.stage--shop` modifier. Only the log table needs JavaScript, and it reads from a single `loadActivities()` seam that the real Strava integration will later replace.

**Tech Stack:** Hand-written HTML/CSS/vanilla JS, no build step, no dependencies. Google Fonts (Bungee Shade, Major Mono Display, Overpass Mono). Verification via headless Chrome + Python/PIL pixel assertions.

**Spec:** `docs/superpowers/specs/2026-08-31-v2-menu-and-log-of-gains-design.md` — read it before starting; this plan argues from it and does not restate its reasoning.

## Global Constraints

- **`1rem` = one Figma pixel.** Every geometry value in this plan is a raw Figma pixel and is written in `rem`. Never write `px` for layout.
- **Desktop stage** 1440x1024; `html { font-size: min(1px, calc(100vw / 1440), calc(100svh / 1024)) }` (already in `style.css`).
- **Phone stage** 380x946 at `< 768px`; `html { font-size: calc(100vw / 380) }` (already in `style.css`).
- **Content box, all views:** `left: 324rem; top: 286rem; width: 791rem`. Never 325, never 799 — see the spec's "The 799-vs-791 drift".
- **Tab strip:** `left: 324rem; top: 236rem; width: 366rem; height: 50rem`; three cells of `122rem`.
- **Colours** come from the eight existing `:root` tokens. Exactly one new colour appears in v2 and it is **not** a token: the row band is `background: blue` with `mix-blend-mode: difference`.
- **No new CSS `border` on any box.** Every visible box edge is a brush SVG on the overlay.
- **No new dependencies.** No npm, no build step, no test framework.
- **Fonts:** tab labels Overpass Mono 600 / 14rem; table header Overpass Mono 700 / 18rem; table rows Overpass Mono 400 / 18rem. All uppercase via `text-transform`.
- **Commit after every task.** Never bundle two tasks into one commit.

---

## File Structure

| File | Responsibility |
|---|---|
| `index.html` | START view: shell + the v1 collage, unchanged apart from the wordmark |
| `log-of-gains.html` | LOG OF GAINS view: shell + the table box |
| `shop.html` | SHOP view: shell + placeholder copy in the box |
| `style.css` | All styling for all pages. Extended, never restructured |
| `js/activities.js` | Placeholder data only. The file the Strava fetch replaces |
| `js/log.js` | Renders rows into the table; owns `loadActivities()` |
| `tools/verify.py` | Renders pages headless and asserts measured pixel facts |
| `assets/borders/border-tabs.svg` | New. Tab strip outline, both breakpoints |
| `assets/borders/border-table-d.svg` | New. Log/shop box outline, desktop |
| `assets/borders/border-table-m.svg` | New. Log box outline, phone |
| `NOTES.md` | Extended with the v2 *why*, per its existing role |

---

### Task 1: Fix the Figma frame and export the two new brush borders

The log box is drawn 799 wide but its row grid sums to the 743 interior a 791 box implies. Fix the file so Figma and code agree, then export. Nothing in the repo renders differently after this task — it only adds assets.

**Files:**
- Create: `assets/borders/border-tabs.svg`
- Create: `assets/borders/border-table-d.svg`
- Modify: `NOTES.md`

**Interfaces:**
- Consumes: nothing.
- Produces: `assets/borders/border-tabs.svg` at **370x54** and `assets/borders/border-table-d.svg` at **795x529** — both are exports of a frame plus 2px of brush overflow on every side, the same convention as the five existing exports. Tasks 3, 4, 5 and 8 position these on the overlay.

- [ ] **Step 1: Load the Figma write skill**

`use_figma` must never be called without it:

```
Skill(skill="figma:figma-use")
```

- [ ] **Step 2: Find the Table and Menu main components**

The frames hold *instances*; resizing an instance would leave the component wrong. Run via `use_figma` on file `BgBx1W0MizlqEKMRBrGjdk`:

```js
const ids = ['58:469', '58:159'];
for (const id of ids) {
  const inst = await figma.getNodeByIdAsync(id);
  const main = await inst.getMainComponentAsync();
  console.log(inst.name, 'instance', inst.width + 'x' + inst.height,
              '-> main', main.id, main.name, main.width + 'x' + main.height);
}
```

Expected: the `Table` main component reports `799x533`, the `Menu` main component `366x50`. Record both main component ids — later steps need them.

- [ ] **Step 3: Resize the Table component to 791x525**

Using the main component id from Step 2:

```js
const table = await figma.getNodeByIdAsync('<TABLE_MAIN_ID>');
table.resizeWithoutConstraints(791, 525);
console.log(table.width + 'x' + table.height);
const rows = table.findOne(n => n.name === 'Rows');
console.log('rows width', rows.width);   // expect 743
```

Expected: `791x525`, and `rows width 743`. If `Rows` does not report 743, STOP — the layout is not resizing as the spec predicted, and the reconciliation needs rechecking before any code is written.

- [ ] **Step 4: Export the table border outline**

Clone, strip everything but the stroke, export, delete the clone. The clone keeps the original untouched:

```js
const src = await figma.getNodeByIdAsync('<TABLE_MAIN_ID>');
const clone = src.clone();
clone.name = 'EXPORT-table-border';
for (const child of [...clone.children]) child.remove();
clone.fills = [];
const bytes = await clone.exportAsync({ format: 'SVG' });
clone.remove();
console.log('bytes', bytes.length);
figma.ui.postMessage({ svg: String.fromCharCode(...bytes) });
```

Expected: an SVG whose root `width`/`height` are **795x529**. If the export instead reports 791x525, the brush overflow was not included — check `strokeAlign` is `CENTER` before continuing.

Save it to `assets/borders/border-table-d.svg`.

- [ ] **Step 5: Export the tab strip outline**

Fills must be dropped so the export is stroke-only — the active cell's red fill is done in CSS, not baked into the border:

```js
const src = await figma.getNodeByIdAsync('<MENU_MAIN_ID>');
const clone = src.clone();
clone.name = 'EXPORT-tabs-border';
for (const cell of clone.children) {
  cell.fills = [];
  for (const t of [...cell.children]) t.remove();   // drop the labels
}
const bytes = await clone.exportAsync({ format: 'SVG' });
clone.remove();
console.log('bytes', bytes.length);
```

Expected: an SVG of **370x54** containing red brush paths and no text and no fills. Save to `assets/borders/border-tabs.svg`.

- [ ] **Step 6: Verify both files are stroke-only**

```bash
cd assets/borders
head -c 200 border-tabs.svg; echo
head -c 200 border-table-d.svg; echo
grep -c '#7F1010\|#7f1010' border-tabs.svg border-table-d.svg || echo "no text glyphs: good"
grep -c '#0000FF\|#0000ff' border-table-d.svg || echo "no blue bands: good"
grep -o '#D8CCBC\|#d8ccbc' border-table-d.svg | head
```

Expected: root elements `width="370" height="54"` and `width="795" height="529"`; **zero** matches for `#7F1010` (text) and `#0000FF` (bands). If a `#D8CCBC` full-bleed ground rect is present, delete that one `<rect>` element by hand — a direct export of a node inside a frame includes the parent's background, which would paint an opaque slab over the composition.

- [ ] **Step 7: Record the geometry in NOTES.md**

Append to `NOTES.md` under `## style.css`, after the "Brush strokes" section:

```markdown
### v2 exports

`border-tabs.svg` (370x54) is the tab strip: the `Menu` component with every cell
fill and label removed, so it is stroke-only. The active cell's red fill is CSS,
not baked in — otherwise it could not move between pages.

`border-table-d.svg` (795x529) is the log/shop box. The `Table` component was
drawn 799x533 but its row grid sums to 743, the interior a 791 box implies
(`791 - 2*24` padding), so the component was resized to 791x525 to match the grid
it was built for. Both exports carry the usual 2px brush overflow per side.
```

- [ ] **Step 8: Commit**

```bash
git add assets/borders/border-tabs.svg assets/borders/border-table-d.svg NOTES.md
git commit -m "Export the tab strip and log box brush borders"
```

---

### Task 2: Verification harness

Written before any page work so every later task has a failing assertion driving it. The spec's Verification section is the requirements list; this makes it executable.

**Files:**
- Create: `tools/verify.py`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `python tools/verify.py [page…]` — exits `0` if all checks pass, `1` otherwise, printing one `PASS`/`FAIL` line per check. Helper functions `ink_runs(im, y, x0, x1)` → list of `(start, end)` red-ink runs, and `median(im, x0, x1, y0, y1)` → `(r, g, b)`. Tasks 3–9 add `CHECKS` entries and run this.

- [ ] **Step 1: Write the harness**

Create `tools/verify.py`:

```python
#!/usr/bin/env python
"""Render each page headless and assert measured pixel facts about it.

Every expected number here is a raw Figma pixel, which is also a CSS px at the
1440x1024 and 380x946 render sizes, because .stage is scaled so 1rem == 1px.
"""
import argparse
import pathlib
import statistics as st
import subprocess
import sys
import tempfile

from PIL import Image

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = pathlib.Path(__file__).resolve().parent.parent

DESKTOP = (1440, 1024)
PHONE = (380, 946)


def shot(page, size):
    """Render `page` at `size` and return it as an RGB image."""
    out = pathlib.Path(tempfile.mkdtemp()) / "shot.png"
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         f"--screenshot={out}", f"--window-size={size[0]},{size[1]}",
         "--virtual-time-budget=8000", (ROOT / page).as_uri()],
        check=True, capture_output=True,
    )
    return Image.open(out).convert("RGB")


def redness(p):
    r, g, b = p
    return r - (g + b) / 2


def ink_runs(im, y, x0, x1, thr=25):
    """Contiguous runs of red ink along the scanline `y`."""
    xs = [x for x in range(x0, x1) if redness(im.getpixel((x, y))) > thr]
    runs = []
    for x in xs:
        if runs and x - runs[-1][-1] <= 2:
            runs[-1].append(x)
        else:
            runs.append([x])
    return [(r[0], r[-1]) for r in runs]


def median(im, x0, x1, y0, y1):
    px = [im.getpixel((x, y)) for y in range(y0, y1) for x in range(x0, x1)]
    return tuple(round(c) for c in (st.median(ch) for ch in zip(*px)))


def hexof(rgb):
    return "#%02x%02x%02x" % rgb


def near(a, b, tol=6):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


class Report:
    def __init__(self):
        self.failed = 0

    def check(self, ok, label, got=None, want=None):
        if ok:
            print(f"  PASS  {label}")
        else:
            self.failed += 1
            detail = "" if got is None else f"  (got {got!r}, want {want!r})"
            print(f"  FAIL  {label}{detail}")


# --- shared shell checks -----------------------------------------------------

def check_shell(r, im, page):
    """The tab strip and box edges, identical on every desktop page."""
    # Box left/right edge, measured on a scanline inside the box.
    runs = ink_runs(im, 700, 250, 1250)
    edges = (runs[0][0], runs[-1][-1]) if len(runs) >= 2 else None
    r.check(edges is not None and abs(edges[0] - 324) <= 3
            and abs(edges[1] - 1115) <= 3,
            f"{page}: box spans x=324..1115 (791 wide)", edges, (324, 1115))

    # The box's top brush line runs continuously across all three tab cells.
    for label, x0, x1 in [("under tab 1", 330, 440),
                          ("under tab 2", 452, 562),
                          ("under tab 3", 574, 684),
                          ("right of strip", 700, 780)]:
        band = median(im, x0, x1, 286, 288)
        r.check(redness(band) > 25,
                f"{page}: top brush line present {label}", hexof(band), "reddish")


def check_active_tab(r, im, page, cell):
    """Cell 0/1/2 is the active one: colour-burned red fill, ending at y=285."""
    x0 = 330 + cell * 122
    fill = median(im, x0, x0 + 100, 250, 284)
    r.check(near(fill, (209, 0, 0), tol=12),
            f"{page}: active tab {cell} is colour-burned red", hexof(fill), "#d10000")
    for other in range(3):
        if other == cell:
            continue
        ox = 330 + other * 122
        inactive = median(im, ox, ox + 100, 250, 284)
        r.check(near(inactive, (214, 202, 188), tol=12),
                f"{page}: tab {other} is not filled", hexof(inactive), "ground")


# --- per-page checks ---------------------------------------------------------

def check_index(r):
    im = shot("index.html", DESKTOP)
    check_shell(r, im, "index")
    check_active_tab(r, im, "index", 0)
    # The wordmark moved from top:129 to top:70, so assert where its ink STARTS.
    # Sampling a single row inside the glyphs would pass at either position.
    top = next((y for y in range(40, 300) if ink_runs(im, y, 400, 1040)), None)
    r.check(top is not None and abs(top - 70) <= 12,
            "index: wordmark ink starts near y=70", top, 70)


def check_log(r):
    im = shot("log-of-gains.html", DESKTOP)
    check_shell(r, im, "log")
    check_active_tab(r, im, "log", 1)

    # Ten rows of 39px starting at y=381; even rows carry the difference band.
    for i in range(10):
        top = 381 + i * 39
        band = median(im, 550, 566, top + 4, top + 35)
        if i % 2:
            r.check(near(band, (216, 204, 67), tol=10),
                    f"log: row {i + 1} banded #d8cc43", hexof(band), "#d8cc43")
        else:
            r.check(near(band, (216, 204, 188), tol=10),
                    f"log: row {i + 1} unbanded", hexof(band), "ground")

    bottom = median(im, 550, 566, 800, 806)
    r.check(near(bottom, (216, 204, 188), tol=10),
            "log: no 11th row below y=800", hexof(bottom), "ground")


def check_shop(r):
    im = shot("shop.html", DESKTOP)
    check_shell(r, im, "shop")
    check_active_tab(r, im, "shop", 2)


def check_phone(r):
    for page in ("index.html", "log-of-gains.html", "shop.html"):
        im = shot(page, PHONE)
        runs = ink_runs(im, 300, 0, 380)
        edges = (runs[0][0], runs[-1][-1]) if len(runs) >= 2 else None
        r.check(edges is not None and abs(edges[0] - 12) <= 4
                and abs(edges[1] - 378) <= 4,
                f"phone {page}: box spans x=12..378", edges, (12, 378))


CHECKS = {
    "index": check_index,
    "log": check_log,
    "shop": check_shop,
    "phone": check_phone,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", default=None,
                    help="subset of: " + ", ".join(CHECKS))
    args = ap.parse_args()
    names = args.names or list(CHECKS)

    r = Report()
    for name in names:
        print(name)
        CHECKS[name](r)
    print()
    print("FAILED" if r.failed else "OK", f"({r.failed} failing)")
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it and confirm it fails for the right reasons**

```bash
python tools/verify.py index
```

Expected: FAIL. `index.html` is still v1 — there is no tab strip, so "active tab 0 is colour-burned red" and the "top brush line present under tab N" checks fail. The `box spans x=324..1115` check should already PASS, since v1's boxes are already 791 wide at 324. If that one fails, the harness's coordinate mapping is wrong and must be fixed before any page work.

- [ ] **Step 3: Confirm the other three suites fail on missing files**

```bash
python tools/verify.py log shop phone
```

Expected: errors or failures — `log-of-gains.html` and `shop.html` do not exist yet. This confirms the harness is actually loading the pages rather than silently passing.

- [ ] **Step 4: Commit**

```bash
git add tools/verify.py
git commit -m "Add a pixel verification harness for the v2 compositions"
```

---

### Task 3: The shell — fonts, tab strip, wordmark, on index.html

Turns v1's `index.html` into the v2 START view. This is the task that makes the shared shell exist; Tasks 4 and 5 copy it.

**Files:**
- Modify: `index.html`
- Modify: `style.css`
- Modify: `NOTES.md`

**Interfaces:**
- Consumes: `assets/borders/border-tabs.svg` (370x54) from Task 1; `tools/verify.py` from Task 2.
- Produces: the shell markup block (`.grain`, `.stage.stage--start`, `.logo`, `.i--diet`, `nav.tabs` with three `a.tab`) and the `.tabs` / `.tab` CSS. Tasks 4 and 5 copy the markup verbatim, changing only which `<a>` carries `aria-current="page"` and the `.stage--*` modifier.

- [ ] **Step 1: Run the failing check**

```bash
python tools/verify.py index
```

Expected: FAIL on the tab checks, as established in Task 2.

- [ ] **Step 2: Add Overpass Mono to the font link**

In `index.html`, replace the stylesheet link:

```html
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Bungee+Shade&family=Major+Mono+Display&family=Overpass+Mono:wght@400;600;700&display=swap">
```

- [ ] **Step 3: Add the font token**

In `style.css`, in `:root`, after `--font-mono`:

```css
  --font-ui:      "Overpass Mono", monospace;
```

Named for its role, like the other two: it is the face for interface chrome and tabular text. `--font-mono` stays Major Mono Display, which is the tagline's display face and not interchangeable.

- [ ] **Step 4: Add the tab strip markup**

In `index.html`, add `stage--start` to the stage and insert the nav after the diet bowl:

```html
<main class="stage stage--start">

  <img class="logo" src="assets/logo.svg" alt="Body Improvement Club" width="366" height="148">

  <img class="i i--diet d-only" src="assets/diet-bowl.svg" alt="" aria-hidden="true">

  <nav class="tabs" aria-label="Sections">
    <a class="tab" aria-current="page" href="index.html">start</a>
    <a class="tab" href="log-of-gains.html">log of gains</a>
    <a class="tab" href="shop.html">shop</a>
  </nav>
```

- [ ] **Step 5: Add the tab CSS**

In `style.css`, after the `.box--link` rules:

```css
.tabs {
  display: flex;
}

.tab {
  flex: 0 0 122rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16rem 20.064rem;
  font-family: var(--font-ui);
  font-weight: 600;
  line-height: normal;
  text-align: center;
  text-transform: uppercase;
  text-decoration: none;
  white-space: nowrap;
  color: var(--link-ink);
}

.tab[aria-current] {
  background-color: var(--red);
  color: var(--ground);
  mix-blend-mode: color-burn;
}

.tab:not([aria-current]):hover,
.tab:not([aria-current]):focus-visible {
  background-color: var(--link-hover);
  color: var(--ink-inverse);
}
```

`.tabs` needs no `position` — `.stage > *` already makes every direct child absolute.

- [ ] **Step 6: Add the shared geometry, and move the wordmark**

In `style.css`, in the phone (default) block, beside the other geometry:

```css
.tabs { left: 12rem; top: 236rem; width: 366rem; height: 50rem; }
.tab  { font-size: 14rem; }
```

Then in the `@media (min-width: 768px)` block, change `.logo`'s top from `129rem` to `70rem` and add the desktop strip position:

```css
  .logo { left: 537rem; top: 70rem; width: 366rem; height: 148rem; }

  .tabs { left: 324rem; top: 236rem; }
```

The strip is `366rem` wide and its cells `122rem` at **both** breakpoints, so only `left` differs — the phone content column is also 366 wide. That is why there is no phone tab variant.

- [ ] **Step 7: Composite the tab border onto the overlay**

The current `.stage::before` rules are unconditional. Scope them so each page gets its own layer list. Rename the existing phone `.stage::before` selector to `.stage--start::before`, and prepend the tabs layer to both its lists:

```css
.stage--start::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background-repeat: no-repeat;
  background-image:
    url("assets/borders/border-tabs.svg"),
    url("assets/borders/border-title-m.svg"),
    url("assets/borders/border-runners-m.svg"),
    url("assets/borders/border-exercises-m.svg"),
    url("assets/borders/border-panel-m.svg"),
    url("assets/borders/border-link-m.svg");
  background-position:
    10rem 234rem,
    10rem 212rem,
    11rem 384rem,
    11rem 707rem,
    10rem 467rem,
    10rem 790rem;
  background-size:
    370rem  54rem,
    370rem 175rem,
    368rem  86rem,
    368rem  86rem,
    370rem 243rem,
    370rem 132rem;
}
```

Every tabs layer is positioned at (strip origin − 2rem) at its natural 370x54 — the same "frame origin minus overflow" rule the five existing layers follow. Phone strip origin is (12, 236), so the layer sits at (10, 234).

Do the same inside the media query, adding the tabs layer first with position `322rem 234rem` (desktop origin (324, 236) − 2) and size `370rem 54rem`, and renaming that selector to `.stage--start::before` too.

Extract the shared parts so the three page modifiers do not each repeat them:

```css
.stage::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background-repeat: no-repeat;
}
```

and leave only `background-image` / `-position` / `-size` in the `.stage--start::before` rules.

- [ ] **Step 8: Run the check**

```bash
python tools/verify.py index
```

Expected: PASS on every `index` check, including "top brush line present under tab 1/2/3" — which passes only because `.stage::before` paints above the strip. If the line is missing under the active tab, the strip is painting above the overlay; do not "fix" this by reordering, check `z-index: 2` survived Step 7.

- [ ] **Step 9: Record the two non-obvious bits in NOTES.md**

Append under `## style.css`:

```markdown
### Tabs

The strip is 366 wide with 122-wide cells at BOTH breakpoints — the phone content
column is also 366, and 366 = 3 x 122 — so only `left` changes between them.

The active cell is `--red` filled with a `--ground` label and
`mix-blend-mode: color-burn`, which is why it samples ~#d10000 rather than
#e30b19; that is the burn against the ground, not a different red.

The strip does NOT interrupt the box's top border. The tab metaphor might suggest
the active cell should open into the box, but sampling both v2 frames shows the
box's top brush line running continuously across all three cells with the active
fill stopping just above it. This falls out for free: the strip is a `.stage`
child and `.stage::before` composites every brush export above all children at
`z-index: 2`. No per-active-state exports, no z-index juggling.

`.stage::before` is split — shared properties on `.stage::before`, the per-view
layer lists on `.stage--start` / `.stage--log` / `.stage--shop`.
```

- [ ] **Step 10: Commit**

```bash
git add index.html style.css NOTES.md
git commit -m "Seat the v2 tab strip on the content box"
```

---

### Task 4: shop.html

The simplest page carrying the shell. Built before the log view so the shell's reuse is proven by something trivial, and so all three tab targets resolve.

**Files:**
- Create: `shop.html`
- Modify: `style.css`
- Modify: `tools/verify.py` (nothing — `check_shop` already exists)

**Interfaces:**
- Consumes: the shell markup from Task 3; `border-table-d.svg` (795x529) from Task 1.
- Produces: `.stage--shop::before` overlay rules and the `.box--copy` placeholder box, both reused conceptually by Task 5's `.box--table`.

- [ ] **Step 1: Run the failing check**

```bash
python tools/verify.py shop
```

Expected: failure — `shop.html` does not exist.

- [ ] **Step 2: Create shop.html**

Copy `index.html`'s shell verbatim, move `aria-current` to the shop tab, swap the stage modifier, and put the placeholder box in:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shop — Body Improvement Club</title>
<meta name="description" content="Body Improvement Club >>> club kit, coming soon.">

<link rel="canonical" href="https://bodyimprovement.club/shop.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Body Improvement Club">
<meta property="og:url" content="https://bodyimprovement.club/shop.html">
<meta property="og:title" content="Shop — Body Improvement Club">
<meta property="og:description" content="Body Improvement Club >>> club kit, coming soon.">
<meta property="og:image" content="https://bodyimprovement.club/assets/og-image.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The BIC monogram: three red letters stepping diagonally down to the right on a grainy sand ground.">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/fav-icon.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Bungee+Shade&family=Major+Mono+Display&family=Overpass+Mono:wght@400;600;700&display=swap">

<link rel="stylesheet" href="style.css">
</head>
<body>

<img class="grain" src="assets/film-grain.webp" alt="" aria-hidden="true" decoding="async">

<main class="stage stage--shop">

  <img class="logo" src="assets/logo.svg" alt="Body Improvement Club" width="366" height="148">

  <img class="i i--diet d-only" src="assets/diet-bowl.svg" alt="" aria-hidden="true">

  <nav class="tabs" aria-label="Sections">
    <a class="tab" href="index.html">start</a>
    <a class="tab" href="log-of-gains.html">log of gains</a>
    <a class="tab" aria-current="page" href="shop.html">shop</a>
  </nav>

  <div class="box box--copy">
    <p>Club kit is coming. Until then the only merch is the work.</p>
  </div>

</main>

</body>
</html>
```

- [ ] **Step 3: Add the box and overlay CSS**

In `style.css`, in the phone block:

```css
.box--copy {
  left: 12rem; top: 286rem; width: 366rem; height: 525rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rem 24rem;
}

.box--copy p {
  margin: 0;
  font-family: var(--font-ui);
  font-weight: 400;
  font-size: 18rem;
  line-height: 23rem;
  text-align: center;
  text-transform: uppercase;
  color: var(--link-ink);
}

.stage--shop::before {
  background-image:
    url("assets/borders/border-tabs.svg"),
    url("assets/borders/border-table-m.svg");
  background-position:
    10rem 234rem,
    10rem 284rem;
  background-size:
    370rem  54rem,
    370rem 529rem;
}
```

and in the media query:

```css
  .box--copy { left: 324rem; width: 791rem; }

  .stage--shop::before {
    background-image:
      url("assets/borders/border-tabs.svg"),
      url("assets/borders/border-table-d.svg");
    background-position:
      322rem 234rem,
      322rem 284rem;
    background-size:
      370rem  54rem,
      795rem 529rem;
  }
```

`border-table-m.svg` does not exist until Task 8; the phone rule is written now and will simply show no border until then. Desktop, which is what `check_shop` renders, is complete.

- [ ] **Step 4: Run the check**

```bash
python tools/verify.py shop
```

Expected: PASS on all `shop` checks — box spanning 324..1115, top line continuous, tab 2 burned red, tabs 0 and 1 unfilled.

- [ ] **Step 5: Commit**

```bash
git add shop.html style.css
git commit -m "Add the shop placeholder page"
```

---

### Task 5: The log table box, with static rows

Geometry first, with the ten rows hardcoded, so the box, columns, type and banding are verified independently of any JavaScript. Task 6 then swaps the static rows for rendered ones and proves the result is pixel-identical.

**Files:**
- Create: `log-of-gains.html`
- Modify: `style.css`
- Modify: `NOTES.md`

**Interfaces:**
- Consumes: the shell from Task 3; `border-table-d.svg` from Task 1.
- Produces: the `.box--table` / `.log` CSS and the exact `<table>` structure — `<colgroup>` of four `<col>` (`c-member`, `c-activity`, `c-date`, `c-stat`), a `<thead>` of four `<th scope="col">`, and a `<tbody>` of ten `<tr>` each with four bare `<td>` in member/activity/date/stat order. Task 6's `render()` must produce exactly this `<tbody>` shape.

- [ ] **Step 1: Run the failing check**

```bash
python tools/verify.py log
```

Expected: failure — `log-of-gains.html` does not exist.

- [ ] **Step 2: Create log-of-gains.html**

Same `<head>` as `shop.html` with the shop strings replaced by:

```html
<title>Log of Gains — Body Improvement Club</title>
<meta name="description" content="Body Improvement Club >>> the club's most recent gains, logged.">
<link rel="canonical" href="https://bodyimprovement.club/log-of-gains.html">
<meta property="og:url" content="https://bodyimprovement.club/log-of-gains.html">
<meta property="og:title" content="Log of Gains — Body Improvement Club">
<meta property="og:description" content="Body Improvement Club >>> the club's most recent gains, logged.">
```

Same shell, with `stage--log` and `aria-current` on the middle tab, then:

```html
  <div class="box box--table">
    <table class="log">
      <colgroup>
        <col class="c-member">
        <col class="c-activity">
        <col class="c-date">
        <col class="c-stat">
      </colgroup>
      <thead>
        <tr>
          <th scope="col">member</th>
          <th scope="col">activity</th>
          <th scope="col">date</th>
          <th scope="col">stats</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>max w.</td><td>morning shakeout</td><td>30 aug-26</td><td>8.2 km</td></tr>
        <tr><td>hanna k.</td><td>lunch ride</td><td>30 aug-26</td><td>31.7 km</td></tr>
        <tr><td>jonas b.</td><td>pull day</td><td>29 aug-26</td><td>52:10</td></tr>
        <tr><td>elif s.</td><td>pool 40x50</td><td>29 aug-26</td><td>2.0 km</td></tr>
        <tr><td>tomas r.</td><td>threshold 6x1k</td><td>28 aug-26</td><td>11.4 km</td></tr>
        <tr><td>mira l.</td><td>legs and lungs</td><td>28 aug-26</td><td>47:35</td></tr>
        <tr><td>david o.</td><td>gravel loop north</td><td>27 aug-26</td><td>58.3 km</td></tr>
        <tr><td>sofia n.</td><td>mobility and core</td><td>27 aug-26</td><td>28:00</td></tr>
        <tr><td>lukas p.</td><td>easy recovery jog</td><td>26 aug-26</td><td>6.1 km</td></tr>
        <tr><td>nora f.</td><td>push day</td><td>26 aug-26</td><td>1:04:20</td></tr>
      </tbody>
    </table>
    <noscript>
      <p class="fallback">The log needs JavaScript. The gains themselves are in the strava group.</p>
    </noscript>
  </div>
```

- [ ] **Step 3: Add the table CSS**

In `style.css`, phone block first — but write the desktop-correct interior here and override only widths later, since the type and paddings are the same:

```css
.box--table {
  left: 12rem; top: 286rem; width: 366rem; height: 525rem;
  padding: 40rem 24rem;
}

.log {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
}

.log th,
.log td {
  padding: 0;
  text-align: left;
  vertical-align: top;
  font-family: var(--font-ui);
  font-size: 18rem;
  line-height: 23rem;
  text-transform: uppercase;
  color: var(--link-ink);
}

.log thead th {
  font-weight: 700;
  text-decoration: underline;
  padding-bottom: 32rem;
}

.log tbody td {
  font-weight: 400;
  height: 23rem;
  padding: 8rem 0;
}

.log tbody tr:nth-child(even) td {
  position: relative;
}

.log tbody tr:nth-child(even) td::before {
  content: "";
  position: absolute;
  inset: 0;
  background: blue;
  mix-blend-mode: difference;
  pointer-events: none;
}

.log .c-member   { width: 218rem; }
.log .c-activity { width: 351rem; }
.log .c-date     { width: 118rem; }
.log .c-stat     { width:  56rem; }

.log th:not(:last-child),
.log td:not(:last-child) { padding-right: 18rem; }

.fallback {
  margin: 0;
  font-family: var(--font-ui);
  font-size: 18rem;
  line-height: 23rem;
  text-transform: uppercase;
  color: var(--link-ink);
}

.stage--log::before {
  background-image:
    url("assets/borders/border-tabs.svg"),
    url("assets/borders/border-table-m.svg");
  background-position:
    10rem 234rem,
    10rem 284rem;
  background-size:
    370rem  54rem,
    370rem 529rem;
}
```

The 32rem header `padding-bottom` is 8 (the drawn header padding) + 24 (the drawn gap between header and rows). Folding the gap into the header cell reproduces `Rows` starting at y=95 without a spacer row: `40 + 23 + 32 = 95`. Rows are then `8 + 23 + 8 = 39` each, ten of them = 390, and `95 + 390 + 40 = 525`.

Column widths carry the 18rem gutter inside them, so content widths come out at the drawn 200 / 333 / 100 / 56 and the four columns still sum to 743.

The band is a `::before` on each even-row cell rather than one element per row: `position: relative` on `<td>` is solid across engines where the same on `<tr>` is not. `inset: 0` covers each cell's padding too, so the per-cell segments abut into one unbroken band across the full 743.

Then in the media query:

```css
  .box--table { left: 324rem; width: 791rem; }

  .stage--log::before {
    background-image:
      url("assets/borders/border-tabs.svg"),
      url("assets/borders/border-table-d.svg");
    background-position:
      322rem 234rem,
      322rem 284rem;
    background-size:
      370rem  54rem,
      795rem 529rem;
  }
```

- [ ] **Step 4: Run the check**

```bash
python tools/verify.py log
```

Expected: PASS on all `log` checks. In particular rows 2, 4, 6, 8, 10 must sample `#d8cc43` and rows 1, 3, 5, 7, 9 the ground, and nothing below y=800. A banded row reading a flat yellow that is not `#d8cc43` means the band got hardcoded instead of blended; a row pitch that drifts off 39 means `line-height` or the header's 32rem is wrong.

- [ ] **Step 5: Record the band and the header padding in NOTES.md**

Append under `## style.css`:

```markdown
### The log table

The banded rows are BLUE, not yellow: each even-row cell carries a `::before` of
`background: blue` with `mix-blend-mode: difference`, exactly as the Figma
component does. Against the ground that computes to
`|#d8ccbc - #0000ff| = #d8cc43`, which is what the frames sample. Keeping the
mechanism rather than the result means the band tracks `--ground` if the ground is
ever retuned, and it grains the way the frame does. Do not "simplify" it to a
yellow token.

The band is a per-cell `::before`, not one element per row, because
`position: relative` on `<td>` is reliable where the same on `<tr>` is not. The
segments abut into one unbroken band because `inset: 0` covers each cell's
padding.

The header's `padding-bottom: 32rem` is the drawn 8px header padding plus the
drawn 24px gap between header and rows. Folding the gap into the header cell puts
the first row at y=95 with no spacer row, and keeps the whole box at
40 + 23 + 32 + 390 + 40 = 525.

`height: 23rem` on the row cells is what keeps a padded EMPTY row 39px tall, so
the banding stays on a short feed.
```

- [ ] **Step 6: Commit**

```bash
git add log-of-gains.html style.css NOTES.md
git commit -m "Add the log of gains table box with static rows"
```

---

### Task 6: Render the rows from the data module

Swap the static rows for rendered ones behind a single seam, and prove nothing moved.

**Files:**
- Create: `js/activities.js`
- Create: `js/log.js`
- Modify: `log-of-gains.html`
- Modify: `NOTES.md`

**Interfaces:**
- Consumes: the `<tbody>` shape defined in Task 5.
- Produces: `ACTIVITIES` — an array of `{ member, activity, date, stat }` string objects; `loadActivities()` → `Promise<Array>`, the single function the Strava integration replaces; `pad(rows, n)` → array of exactly `n` rows; `render(rows, tbody)` → void.

- [ ] **Step 1: Capture the static render as the baseline**

Before changing anything, save what Task 5 produces so the rendered version can be diffed against it:

```bash
python -c "
import sys; sys.path.insert(0, 'tools')
from verify import shot, DESKTOP
shot('log-of-gains.html', DESKTOP).save('/tmp/log-static.png')
print('baseline saved')
"
```

Use a scratch path that suits your environment; `/tmp` here is illustrative. Confirm the file exists and is a 1440x1024 PNG.

- [ ] **Step 2: Create js/activities.js**

The same ten rows Task 5 hardcoded, so the diff in Step 6 is meaningful:

```js
/* Placeholder club feed. Replaced wholesale when the Strava API lands —
   see loadActivities() in log.js, which is the only seam that matters. */
const ACTIVITIES = [
  { member: "max w.",   activity: "morning shakeout",  date: "30 aug-26", stat: "8.2 km"  },
  { member: "hanna k.", activity: "lunch ride",        date: "30 aug-26", stat: "31.7 km" },
  { member: "jonas b.", activity: "pull day",          date: "29 aug-26", stat: "52:10"   },
  { member: "elif s.",  activity: "pool 40x50",        date: "29 aug-26", stat: "2.0 km"  },
  { member: "tomas r.", activity: "threshold 6x1k",    date: "28 aug-26", stat: "11.4 km" },
  { member: "mira l.",  activity: "legs and lungs",    date: "28 aug-26", stat: "47:35"   },
  { member: "david o.", activity: "gravel loop north", date: "27 aug-26", stat: "58.3 km" },
  { member: "sofia n.", activity: "mobility and core", date: "27 aug-26", stat: "28:00"   },
  { member: "lukas p.", activity: "easy recovery jog", date: "26 aug-26", stat: "6.1 km"  },
  { member: "nora f.",  activity: "push day",          date: "26 aug-26", stat: "1:04:20" },
];
```

- [ ] **Step 3: Create js/log.js**

```js
/* The box is a fixed 791x525 with one brush border export, so the table is
   always exactly ROW_COUNT rows: a shorter feed pads, a longer one truncates. */
const ROW_COUNT = 10;
const COLUMNS = ["member", "activity", "date", "stat"];
const EMPTY = { member: "", activity: "", date: "", stat: "" };

async function loadActivities() {
  return ACTIVITIES;
}

function pad(rows, n) {
  const out = rows.slice(0, n);
  while (out.length < n) out.push(EMPTY);
  return out;
}

function render(rows, tbody) {
  tbody.replaceChildren(...rows.map((row) => {
    const tr = document.createElement("tr");
    for (const column of COLUMNS) {
      const td = document.createElement("td");
      td.textContent = row[column];
      tr.append(td);
    }
    return tr;
  }));
}

async function main() {
  const tbody = document.querySelector(".log tbody");
  render(pad(await loadActivities(), ROW_COUNT), tbody);
}

main();
```

- [ ] **Step 4: Empty the tbody and load the scripts**

In `log-of-gains.html`, replace the ten static `<tr>` with nothing:

```html
      <tbody></tbody>
```

and add, just before `</body>`:

```html
<script src="js/activities.js"></script>
<script src="js/log.js"></script>
```

Plain classic scripts in order, no `type="module"` — modules are blocked by CORS on `file://`, and the whole verification harness renders local files.

- [ ] **Step 5: Run the check**

```bash
python tools/verify.py log
```

Expected: PASS, identically to Task 5. Rows now come from JS.

- [ ] **Step 6: Diff against the static baseline**

The real assertion for this task — the swap must be invisible:

```bash
python -c "
import sys; sys.path.insert(0, 'tools')
from verify import shot, DESKTOP
from PIL import Image, ImageChops
a = Image.open('/tmp/log-static.png').convert('RGB')
b = shot('log-of-gains.html', DESKTOP)
box = ImageChops.difference(a, b).getbbox()
print('identical' if box is None else f'DIFFERS in {box}')
"
```

Expected: `identical`. Any difference means `render()` is not producing the `<tbody>` shape Task 5's CSS targets — most likely a wrong cell order or a stray wrapper element.

- [ ] **Step 7: Verify the padding path**

Confirm a short feed still fills the box, since that is the whole reason `pad` and the `height: 23rem` cell rule exist:

```bash
python - <<'PY'
import re, pathlib, shutil, sys
sys.path.insert(0, 'tools')
from verify import shot, DESKTOP, median, near, hexof

src = pathlib.Path('js/activities.js')
backup = src.read_text(encoding='utf-8')
# keep only the first three activities
trimmed = re.sub(r'(\{ member: "elif s\.".*)(\n\];)', r'\2', backup, flags=re.S)
src.write_text(trimmed, encoding='utf-8')
try:
    im = shot('log-of-gains.html', DESKTOP)
    band = median(im, 550, 566, 385 + 9 * 39, 416 + 9 * 39)
    print('row 10 band', hexof(band), 'banded' if near(band, (216, 204, 67), 10) else 'NOT banded')
finally:
    src.write_text(backup, encoding='utf-8')
PY
```

Expected: `row 10 band #d8cc43 banded` — the tenth row is empty but still 39px tall and still carries its band. Then confirm `git diff --stat js/activities.js` is empty, i.e. the file was restored.

- [ ] **Step 8: Note the seam in NOTES.md**

Append a new top-level section:

```markdown
---

## js/

`activities.js` is placeholder data and nothing else. `log.js` owns the only seam
that matters: `loadActivities()`. When the Strava integration lands it replaces
that one function — a fetch of a generated JSON file, most likely, since Strava
needs OAuth and a token cannot live in a static page. Nothing else in `log.js`
knows where rows come from.

`ROW_COUNT` is 10 and must stay tied to `border-table-d.svg`: the box is a fixed
791x525 with one border export, so `pad()` fills a short feed and `slice()`
truncates a long one. Changing the row count means re-exporting the border.

Both are classic scripts loaded in order, NOT modules — `type="module"` is blocked
by CORS on `file://`, and both `tools/verify.py` and the `og.html` recipe render
local files.
```

- [ ] **Step 9: Commit**

```bash
git add js/activities.js js/log.js log-of-gains.html NOTES.md
git commit -m "Render the log rows from a data module"
```

---

### Task 7: Phone breakpoint — tab strip and start view

The strip already carries over; what needs settling is that it does not collide with the phone collage, whose title box currently starts at y=212.

**Files:**
- Modify: `style.css`
- Modify: `tools/verify.py`

**Interfaces:**
- Consumes: `.tabs` phone geometry from Task 3 (`left: 12rem; top: 236rem`).
- Produces: the phone y-offsets for the whole start collage, which Task 8 reuses for `.box--table`'s phone top.

- [ ] **Step 1: See the collision**

```bash
python tools/verify.py phone
```

Expected: failure or a wrong box span for `index.html`. Also render it to look at directly:

```bash
python -c "
import sys; sys.path.insert(0, 'tools')
from verify import shot, PHONE
shot('index.html', PHONE).save('/tmp/phone-start.png')
"
```

The strip is at y=236..286 while the phone title box is at y=214..385 — they overlap by 50px. Confirm that overlap is visible before fixing it.

- [ ] **Step 2: Push the phone collage down by 74rem**

The strip must sit directly on the title box, so the title box's top must equal the strip's bottom, 286. It is at 214, so everything from the title box down moves `+72rem`. Keep the wordmark and the strip where they are.

In `style.css`'s phone block, add 72 to the `top` of each of these, and to each corresponding `.stage--start::before` background y:

| Rule | `top` was | `top` becomes |
|---|---|---|
| `.box--title` | `214rem` | `286rem` |
| `.box--runners` | `385rem` | `457rem` |
| `.panel` | `469rem` | `541rem` |
| `.box--exercises` | `708rem` | `780rem` |
| `.box--link` | `792rem` | `864rem` |

and the overlay positions, which are each 2rem above their box:

| Layer | y was | y becomes |
|---|---|---|
| `border-title-m.svg` | `212rem` | `284rem` |
| `border-runners-m.svg` | `384rem` | `456rem` |
| `border-panel-m.svg` | `467rem` | `539rem` |
| `border-exercises-m.svg` | `707rem` | `779rem` |
| `border-link-m.svg` | `790rem` | `862rem` |

- [ ] **Step 3: Grow the phone stage**

`.box--link` now ends at `864 + 128 = 992`, past the 946 stage. In the phone block:

```css
.stage {
  position: relative;
  flex: none;
  width: 380rem;
  height: 1018rem;
  transform: translateX(-5rem);
}
```

1018 = 992 + 26, keeping roughly the 26rem of breathing room the 946 stage had below the old 920 bottom. The page already scrolls on the phone (`body { overflow-y: auto }`), so a taller stage is fine.

- [ ] **Step 4: Add a phone start check**

In `tools/verify.py`, extend `check_phone` so it does more than measure the box width:

```python
def check_phone(r):
    for page in ("index.html", "log-of-gains.html", "shop.html"):
        im = shot(page, PHONE)
        runs = ink_runs(im, 300, 0, 380)
        edges = (runs[0][0], runs[-1][-1]) if len(runs) >= 2 else None
        r.check(edges is not None and abs(edges[0] - 12) <= 4
                and abs(edges[1] - 378) <= 4,
                f"phone {page}: box spans x=12..378", edges, (12, 378))

        # The strip's cells are 122 wide here too, so cell 2 starts at 12+244.
        strip = ink_runs(im, 260, 0, 380)
        r.check(len(strip) >= 4,
                f"phone {page}: strip shows three cells at y=260", strip, ">=4 runs")

        # The strip sits ON the box: its bottom edge is the box's top edge.
        seam = median(im, 40, 340, 286, 288)
        r.check(redness(seam) > 25,
                f"phone {page}: strip/box seam inked at y=286", hexof(seam), "reddish")
```

`ink_runs` at y=260 crosses the three cells' four vertical edges, so four or more runs means the strip is drawn and not collapsed.

- [ ] **Step 5: Run the checks**

```bash
python tools/verify.py index shop log phone
```

Expected: `index`, `shop` and `log` still PASS (desktop is untouched by this task), and `phone index.html` passes all three of its checks. `phone log-of-gains.html` will still fail its box-span check until Task 8 — note which failures are expected.

- [ ] **Step 6: Commit**

```bash
git add style.css tools/verify.py
git commit -m "Seat the phone tab strip on the phone collage"
```

---

### Task 8: Phone breakpoint — the log table reflow

The only invented geometry in v2. Four columns do not fit 366; each row becomes two lines.

**Files:**
- Modify: `style.css`
- Create: `assets/borders/border-table-m.svg`
- Modify: `NOTES.md`

**Interfaces:**
- Consumes: the `<table>` structure from Task 5 — unchanged, this is CSS-only reflow.
- Produces: `border-table-m.svg` and the final phone `.box--table` height, which `.stage--shop::before` and `.stage--log::before` both already reference.

- [ ] **Step 1: See the overflow**

```bash
python -c "
import sys; sys.path.insert(0, 'tools')
from verify import shot, PHONE
shot('log-of-gains.html', PHONE).save('/tmp/phone-log.png')
"
```

Confirm the four 18rem columns overflow the 366-wide box before reflowing them.

- [ ] **Step 2: Reflow the rows to two lines**

In `style.css`'s phone block, after the shared `.log` rules:

```css
.box--table { height: 640rem; }

.log,
.log thead,
.log tbody,
.log tr { display: block; width: 100%; }

.log colgroup { display: none; }

.log thead { display: none; }

.log tbody tr {
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-areas:
    "member stat"
    "activity date";
  column-gap: 12rem;
  padding: 8rem 0;
}

.log tbody td { display: block; height: auto; padding: 0; font-size: 15rem; line-height: 20rem; }

.log tbody td:nth-child(1) { grid-area: member; font-weight: 700; }
.log tbody td:nth-child(2) { grid-area: activity; }
.log tbody td:nth-child(3) { grid-area: date; text-align: right; }
.log tbody td:nth-child(4) { grid-area: stat; text-align: right; font-weight: 700; }

.log th:not(:last-child),
.log td:not(:last-child) { padding-right: 0; }

.log tbody tr:nth-child(even) td { position: static; }
.log tbody tr:nth-child(even) td::before { content: none; }

.log tbody tr:nth-child(even) {
  position: relative;
  isolation: isolate;
}

.log tbody tr:nth-child(even)::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background: blue;
  mix-blend-mode: difference;
  pointer-events: none;
}
```

Row height becomes `8 + 20 + 20 + 8 = 56rem`, ten rows = 560, and the box `40 + 560 + 40 = 640` — which is where the `640rem` above comes from. The header is dropped: with member/activity labelled by position and weight, a four-column header cannot honestly label a two-line row, and `scope="col"` still serves assistive tech from the markup.

**Treat 640 as a prediction, not a fact.** Grid line-box rounding at a fractional `rem` will move it by a pixel or two. Step 3 measures the real value and corrects it; do not skip that step because the arithmetic looks clean.

Here the rows are `display: grid`, so the band can move back onto the row itself — `position: relative` on a grid container is reliable where it is not on a table row. `z-index: -1` with `isolation: isolate` puts it behind the cell text without a stacking-context escape.

- [ ] **Step 3: Measure the real box height**

```bash
python - <<'PY'
import sys; sys.path.insert(0, 'tools')
from verify import shot, PHONE, redness
im = shot('log-of-gains.html', PHONE)
im.save('/tmp/phone-log2.png')
# find the last inked row band edge, scanning down the left gutter
last = max(y for y in range(286, 946) if redness(im.getpixel((30, y))) > 10)
print('last inked y', last)
PY
```

Set `.box--table`'s phone `height` so the box bottom clears the last row by the drawn 40rem padding, then re-render and confirm the ten bands are evenly pitched and none is clipped.

- [ ] **Step 4: Export the phone border**

Repeat Task 1's Step 4 clone-and-export against a temporary Figma frame resized to `366 x <the height from Step 3>`, or — since no phone frame exists to transcribe — scale `border-table-d.svg` to the phone box. Prefer the scale: the brush texture is the same line and a phone frame does not exist to be faithful to.

```bash
python - <<'PY'
import re, pathlib
src = pathlib.Path('assets/borders/border-table-d.svg').read_text(encoding='utf-8')
H = 000  # <- the height measured in Step 3, plus 4 for the 2px overflow per side
out = src.replace('width="795"', 'width="370"', 1).replace(f'height="529"', f'height="{H}"', 1)
out = re.sub(r'viewBox="0 0 795 529"', 'viewBox="0 0 795 529"', out)  # keep the viewBox; only the box scales
pathlib.Path('assets/borders/border-table-m.svg').write_text(out, encoding='utf-8')
print('wrote border-table-m.svg', H)
PY
```

Keeping the `viewBox` while changing `width`/`height` scales the artwork non-uniformly, which on a 366-wide box stretches the brush. If it reads badly at the seam, re-export from Figma at the real phone size instead — the plan permits either, the render decides.

- [ ] **Step 5: Run every check**

```bash
python tools/verify.py
```

Expected: every suite PASSes, including `phone log-of-gains.html`.

- [ ] **Step 6: Note that the phone log is invented**

Append to `NOTES.md` under `## style.css`:

```markdown
### The phone log table is DERIVED, not transcribed

There is no v2 phone frame. Four 18px columns do not fit a 366 box, so each row
reflows to two lines — member + stat, then activity + date — at 15px/20px, and the
header is dropped because a four-column header cannot honestly label a two-line
row. `scope="col"` in the markup still serves assistive tech.

On the phone the band moves from a per-cell `::before` back onto the row, because
the rows are `display: grid` there and `position: relative` on a grid container is
reliable where it is not on a table row.

`border-table-m.svg` is `border-table-d.svg` rescaled, not a fresh export, for the
same reason. When a phone frame is drawn, re-transcribe all of this and re-export.
```

- [ ] **Step 7: Commit**

```bash
git add style.css assets/borders/border-table-m.svg NOTES.md
git commit -m "Reflow the log table for the phone breakpoint"
```

---

### Task 9: Full-suite verification and documentation pass

**Files:**
- Modify: `NOTES.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: everything.
- Produces: nothing new — the completion gate.

- [ ] **Step 1: Run the whole suite**

```bash
python tools/verify.py
```

Expected: `OK (0 failing)`. Do not proceed past this step with any failure.

- [ ] **Step 2: Confirm the start view did not regress**

The spec's first verification requirement: `index.html` must differ from the v1 frame only by the wordmark and the strip. Compare the desktop start render against the v1 Figma frame region below the strip:

```bash
python - <<'PY'
import sys; sys.path.insert(0, 'tools')
from verify import shot, DESKTOP, median, hexof, ink_runs
im = shot('index.html', DESKTOP)
# The collage below the strip should be v1's: title box, runner strip, panel, link.
for label, y in [("title box", 340), ("icon strips", 520), ("panel", 700), ("link button", 900)]:
    runs = ink_runs(im, y, 250, 1250)
    print(f"{label:12} y={y}  edges {runs[0][0] if runs else None}..{runs[-1][-1] if runs else None}")
PY
```

Expected: `title box`, `panel` spanning ~324..1115; `link button` ~322..670. If any span changed, Task 7's phone offsets leaked into the desktop block.

- [ ] **Step 3: Check every tab target resolves and every asset exists**

```bash
grep -ho 'href="[^"]*"\|src="[^"]*"' index.html log-of-gains.html shop.html \
  | sed 's/.*="//;s/"//' | grep -v '^https\?://' | sort -u \
  | while read -r f; do [ -e "$f" ] || echo "MISSING: $f"; done
grep -o 'url("[^"]*")' style.css | sed 's/url("//;s/")//' | sort -u \
  | while read -r f; do [ -e "$f" ] || echo "MISSING in css: $f"; done
```

Expected: no output.

- [ ] **Step 4: Check the tab strip's keyboard order and focus visibility by hand**

Open `index.html` in a real browser, press Tab three times, and confirm focus moves start → log of gains → shop in visual order with a visible `--link-hover` fill on each inactive tab. The harness cannot see focus states. Note the result.

- [ ] **Step 5: Add the verification recipe to NOTES.md**

Append a new top-level section:

```markdown
---

## tools/verify.py

Renders each page in headless Chrome and asserts measured pixel facts against the
Figma frames — the same sampling that settled the v2 design questions, kept
runnable so a change that breaks the composition fails loudly.

```sh
python tools/verify.py            # every suite
python tools/verify.py log phone  # a subset
```

Every expected number in it is a raw Figma pixel, which is also a CSS px at the
render sizes, because `.stage` is scaled so `1rem` == `1px`. The `CHROME` path at
the top is a Windows absolute path; change it to suit the machine.

What it deliberately cannot check: focus-visible states and keyboard order, which
are a manual pass in a real browser.
```

- [ ] **Step 6: Point the README at the docs**

`README.md` is currently two lines. Replace with:

```markdown
# bodyimprovementclub

BIC! The club's site — [bodyimprovement.club](https://bodyimprovement.club/)

Static HTML/CSS with one small script, no build step. `index.html` (start),
`log-of-gains.html`, `shop.html`, all sharing `style.css`.

- `NOTES.md` — why the files look the way they do. Read before editing either.
- `docs/superpowers/specs/` — designs
- `python tools/verify.py` — render the pages and check them against the designs
```

- [ ] **Step 7: Commit**

```bash
git add NOTES.md README.md
git commit -m "Document the v2 verification pass"
```

---

## Self-review notes

Checked against the spec:

- Every spec section maps to a task: shell → 3; tabs → 3; START → 3; LOG box and interior → 5; band → 5; data seam → 6; SHOP → 4; phone → 7 and 8; typography → 3; exports → 1 and 8; verification → 2 and 9; NOTES additions → distributed into 1, 3, 5, 6, 8, 9.
- The spec's "flat files, relative asset paths" decision is enforced by Task 9 Step 3's link check and by Task 6 Step 4's no-modules note.
- Two known-loose ends are called out **as** loose in the plan rather than papered over: the phone box height in Task 8 Step 2 is explicitly a guess to be replaced by the Step 3 measurement, and the phone border in Step 4 offers rescale-or-re-export with the render deciding. Both are the derived phone layout the spec already flags as invented.
- `ROW_COUNT`, `COLUMNS`, `loadActivities`, `pad`, `render`, `ink_runs`, `median`, `shot`, `check_shell`, `check_active_tab` are each defined once and referenced consistently.
