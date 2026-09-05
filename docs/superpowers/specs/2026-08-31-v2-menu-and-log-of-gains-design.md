# Version 2 — persistent menu and Log of Gains

Design for the second version of bodyimprovement.club: a tab menu seated on the
top edge of the content box, and a second view inside that box showing a feed of
club activity.

Figma file `BgBx1W0MizlqEKMRBrGjdk`:

- `57:370` — "version 2 start", 1440x1243
- `58:401` — "version 2 log of gains", 1440x1243
- `33:945` — "version 1", 1440x1243, for comparison

There is no v2 phone frame. The phone layout is derived here and re-transcribed
later once it is drawn.

---

## What changes from v1

Very little of the start composition moves. Comparing `57:370` against `33:945`:

| Element | v1 | v2 |
|---|---|---|
| `Logo` | (537, 124) 366x148 | (537, **70**) 366x148 |
| `Menu` | — | **(325, 236) 366x50** |
| Content stack | `Frame 15` (324, 286) 791x553.018 | `Frame 16` (324, 286) 791x553.018 — identical |
| `Link button` | (323, 839) 347x128 | unchanged |
| Diet bowl | (1046, 218) 69x66.95 | unchanged |

The content stack is identical sub-box for sub-box: title `Frame 3`
(0, 0) 791x178.339; `Frame 13` (0, 182.339) 791x131.339 containing runners
`Frame 4` (0, 0) 347x131.339 and exercises `Frame 8` (347, 0.170) 443x131;
panel `Frame 12` (0, 313.679) 791x239.339.

**Consequence: every existing `assets/borders/*` export is reused unchanged, and
the start view's CSS geometry needs no re-transcription.** The start view changes
only by the wordmark moving up (54px in frame terms, 124 → 70; 59px against
shipped CSS, which sits at 129 — see the nudge note below) and the tab strip
appearing above it.

Frame coordinates map 1:1 onto the CSS `.stage` (1440x1024) — verified against v1,
where `Frame 15` at (324, 286) is `.box--title { left: 324rem; top: 286rem }` and
the diet bowl at (1046, 218) is `--x: 1046rem; --y: 218rem`. The `Film_Grain`
rectangle at y=110 inside the 1243-tall frame is an artboard artifact; grain is a
full-bleed fixed layer in CSS and takes no geometry from it.

`Logo` sits at y=124 in the v1 frame but `top: 129rem` in shipped CSS — a 5px
deliberate nudge. v2 transcribes the frame value (70) and does not carry the nudge
forward unless the render says otherwise.

### The box's left edge must be reconciled to one value

The frames disagree by a pixel about where the content box starts:

| Node | x |
|---|---|
| `Menu` (both views) | 325 |
| `Frame 16` — start content stack | **324** |
| `Table` — log content box | **325** |
| `Link button` | **323** |

v1 shipped those inconsistencies verbatim (`left: 324rem` on the boxes, `323rem`
on the link button) and nobody could see it, because nothing invited comparison.
v2 does: the whole premise is that the box stays put while its contents swap, so a
1px horizontal jump between START and LOG OF GAINS is exactly the kind of thing
that reads as a bug.

**All v2 content boxes and the tab strip share a single left edge and a single
width: `left: 324rem`, `width: 791rem`.** The `Table` node's 325 is treated as
drift, not intent. The link button keeps its own 323 — it sits below the box, is
never compared against a swapping neighbour, and moving it would perturb the start
composition that this design otherwise leaves untouched.

The same reconciliation applies to the box's *top* edge, which is 286 in both
views and needs no adjustment.

---

## Decisions

Settled during brainstorming; recorded here because each one closes off an
alternative someone will otherwise reopen.

1. **Separate static pages, JS only for the table.** Three HTML files, tabs are
   plain links. No router, no hash URLs, no GitHub Pages 404 redirect trick, no
   flash of late-injected chrome. Cost: the shell markup is duplicated three
   times. Accepted.
2. **Flat files, relative asset paths.** `/log-of-gains.html`, not
   `/log-of-gains/`. Directory-per-view forces root-relative `/assets/…`, which
   breaks opening the pages over `file://` — and the `og.html` recipe in
   `NOTES.md` shows local rendering is part of the workflow. Prettier URLs are
   not worth losing local preview.
3. **Exactly 10 rows, always.** The log box is the drawn 791x525 and one border
   export serves it forever. Fewer than 10 activities pads with empty rows that
   keep their banding; more than 10 truncates to the most recent 10.
4. **Icons keep v1's `mix-blend-mode: color-burn`.** Both v2 frames render the
   runner and exercise icons plain blue, but v1's `Burn the blue icons into the
   ground` commit deliberately blends them into the ground. The blue in the
   frames is unrendered source artwork; the burn wins.
5. **`SHOP` is a real page** with placeholder copy in the mono tagline style, so
   the tab behaves like the others and real content drops in without structural
   change.
6. **`STATS` holds the metric that fits the activity** — distance for run/ride/
   swim, duration for gym and mobility work. Maps onto Strava's `distance` and
   `moving_time` when the API arrives. The frames' literal `INDEX` was placeholder
   text and is not carried over.
7. **Content is a flow list, not absolute positions.** The shell stays absolutely
   positioned in v1's idiom, but table rows are normal flow children. Absolute
   per-row offsets buy nothing for a list whose contents come from an API.

---

## Typography — a third font joins

v2 introduces **Overpass Mono**, which the site does not currently load. Both new
components use it and neither existing font substitutes:

| Where | Family | Weight | Size |
|---|---|---|---|
| Tab labels | Overpass Mono | SemiBold (600) | 14px |
| Table header | Overpass Mono | Bold (700) | 18px |
| Table rows | Overpass Mono | Regular (400) | 18px |

So the Google Fonts link gains `Overpass+Mono:wght@400;600;700` alongside the
existing `Bungee Shade` and `Major Mono Display`, and `:root` gains a
`--font-table` (or similarly named) custom property beside `--font-display` and
`--font-mono`, following the existing token pattern.

`Major Mono Display` stays where it is — the tagline and nothing else. The two
mono faces are not interchangeable: `Major Mono Display` is the lowercase-tall
display face in the tagline, `Overpass Mono` is a conventional monospace for
tabular text.

---

## Files

```
index.html            START            no JS
log-of-gains.html     LOG OF GAINS     + js/activities.js, js/log.js
shop.html             SHOP             no JS
style.css             shared, extended
js/activities.js      placeholder data — the file the Strava fetch replaces
js/log.js             renders rows into the table
assets/borders/border-tabs.svg      new — 366x50 strip, both breakpoints
assets/borders/border-table-d.svg   new — 799x533 for the 791x525 box
assets/borders/border-table-m.svg   new — phone, height per the reflow
NOTES.md              extended
```

---

## The shell

Present identically on all three pages:

```html
<img class="grain" src="assets/film-grain.webp" alt="" aria-hidden="true" decoding="async">

<main class="stage">
  <img class="logo" src="assets/logo.svg" alt="Body Improvement Club" width="366" height="148">
  <img class="i i--diet d-only" src="assets/diet-bowl.svg" alt="" aria-hidden="true">

  <nav class="tabs" aria-label="Sections">
    <a class="tab" href="index.html">start</a>
    <a class="tab" href="log-of-gains.html">log of gains</a>
    <a class="tab" href="shop.html">shop</a>
  </nav>

  <!-- view content -->
</main>
```

Each page marks its own tab with `aria-current="page"`. That attribute is the
**only** styling hook — `.tab[aria-current]` — so there is no parallel
`is-active` class that can drift out of sync with the accessibility state.

Per-page `<head>`: each view gets its own `<title>`, `description`, `og:title`,
`og:description` and `canonical`. All three share `assets/og-image.png`.

---

## Tabs

Nav at (**324**, 236) per the reconciliation above, 366x50. Three cells of exactly 122x50, butted edge to edge,
from `Menu` instance `58:159` → three `Menu item` instances at x=0, 122, 244.

`366 = 3 x 122`, and the phone content box is also 366 wide, **so the tab strip is
identical at both breakpoints** — one export, one rule set, no phone variant.

Every cell carries a 4px `--red` stroke on all four sides, `padding: 16px
20.064px`, and a label in **Overpass Mono SemiBold 14px, uppercase**. The
20.064px matches the existing `.box--link` padding exactly.

States, read off the `Menu item` variants:

- **Inactive** — no fill, red brush outline, `--link-ink` (`#7f1010`) label.
- **Active** — `--red` fill **plus `mix-blend-mode: color-burn`**, label
  `#d8ccbc` — the *ground* token, not `--ink-inverse`. The burn is why the active
  cell samples `#d10000` in the rendered frame rather than `#e30b19`:
  `burn(#d8ccbc, #e30b19) = #d30000`, measured `#d10000` through the grain.
- **Hover / focus-visible** — follow the existing `.box--link` precedent:
  `--link-hover` fill with `--ink-inverse` label. Applies to inactive tabs only;
  the active tab is already the current page. Not in the design; carried over so
  the tabs behave like the site's other interactive element.

### The active tab does not interrupt the box border (measured)

An earlier draft of this spec assumed the tab metaphor needs the box's top edge
to be *absent* under the active tab, and proposed hiding it red-on-red. **Pixel
sampling of both frames shows that is not what the design does**, and no trick is
needed.

Sampling a vertical slice through the seam at y=278..299:

| y | under active tab | under inactive tab | right of the strip |
|---|---|---|---|
| 278–283 | `#d10000` (fill) | ground | ground |
| 284–285 | `#d10000` (fill) | pink line | ground |
| 286–287 | **pink line** | **pink line** | **pink line** |
| 288+ | ground | ground | ground |

The box's top brush line runs **continuously** at y=286–287 across all three
cells and onward to the right, and the active cell's fill stops at y=285 rather
than swallowing it. The line reads pink (`#d78782`-ish) rather than `#e30b19`
because of the bristle gaps — the same ~25% apparent alpha `NOTES.md` already
documents.

This falls out of the existing architecture for free: the tab strip is a `.stage`
child, and `.stage::before` — which composites every brush export — sits above
all children at `z-index: 2`. So the box's top edge paints over the tab strip
exactly as the frames show, with no z-index changes and no per-state exports.
One tab-strip export, one box export per view.

The tabs still read as seated *on* the box because the strip's own 4px bottom
stroke and the box's top stroke occupy the same 4px band (the strip's 236+50=286
bottom edge is the box's 286 top edge), sharing one line between them.

---

## START view

The v1 collage, unchanged. Existing markup for `.box--title`, `.box--runners`,
`.panel`/`.tagline`, `.box--exercises` and `.box--link` carries over verbatim,
as does the `.stage::before` layer set and all five existing border exports.

Changes: `.logo` top 129 → 70, and the tab strip above it.

---

## LOG OF GAINS view

From `Table` instance `58:469`, placed at the reconciled (**324**, 286) at
**791x525**.

### The 799-vs-791 drift, and why 791 wins

`get_metadata` reports the `Table` instance as 799x533, and pixel-sampling the
rendered frames confirms it is genuinely drawn 8px wider than the start box, not
merely reported that way:

| Frame | left edge ink | right edge ink | box width |
|---|---|---|---|
| `57:370` start | x=322–325 | x=1113–1116 | **791** |
| `58:401` log | x=323–326 | x=1122–1125 | **799** |

An 8px width change between two views of "the same box" is the drift decision in
"The box's left edge" above, in a louder form. **791 wins**, and the interior
arithmetic shows why it is what the table was actually designed to:

- At 791 with `padding: 24px`, content is `791 - 48 = 743`
- The columns sum to exactly that: `200 + 18 + 333 + 18 + 100 + 18 + 56 = 743`
- 743 is the `Table Row` component's own native width

So the row grid was built for a 791 box, and the frame was later nudged to 799
without the rows following. Reconciling to 791 restores the design's own
arithmetic rather than overriding it.

The 799x533 figure is the frame plus its 4px stroke on each side
(`791 + 8`, `525 + 8`), which is also why `get_metadata` places the header at
x=24 with width 751 while `get_design_context` reports rows at 743 — precisely
the stroked-frame offset confusion `NOTES.md` warns about. Neither number is
wrong; they measure from different edges. Layout geometry uses the frame rect.

### Interior

`padding: 40px 24px`, `gap: 24px` between header and rows — which reproduces the
observed vertical arithmetic exactly:

```
40 (pad) + 31 (header) + 24 (gap) + 390 (10 rows) + 40 (pad) = 525
```

- **Header** — `Overpass Mono Bold 18px`, uppercase, underlined, `--link-ink`,
  `padding-bottom: 8px` → 23px line + 8 = 31px
- **Rows** — `Overpass Mono Regular 18px`, uppercase, `--link-ink`,
  `padding: 8px 0` → 23 + 16 = 39px each, ten of them flush = 390px
- **Columns** — `display: flex; gap: 18px`, widths `200 / flex:1 0 0 / 100 / 56`
  for member / activity / date / stats. Header uses the same widths.

### The yellow band is blue

The banded rows are **not** a yellow token. Each highlighted row carries a
full-bleed child of `background: blue` (`#0000ff`) with
`mix-blend-mode: difference`, which against the ground yields:

```
|#d8ccbc − #0000ff| = #d8cc43     predicted
 #d8cc43                          measured in the rendered frame
```

Exact to the byte. Transcribe the *mechanism*, not the result: keeping
`blue` + `difference` means the band stays tied to `--ground`, so it shifts
correctly if the ground is ever retuned, and it interacts with the film grain the
way the frame does. **No new colour token is added** — an earlier draft of this
spec wrongly called for one.

Row 1 is unbanded; banding is every even row.

### Markup

A real `<table>`: this is tabular data with column headers, so `<thead>` and
`scope="col"` give screen readers column association for free.

```html
<div class="box box--table">
  <table class="log">
    <thead>
      <tr>
        <th scope="col">member</th>
        <th scope="col">activity</th>
        <th scope="col">date</th>
        <th scope="col">stats</th>
      </tr>
    </thead>
    <tbody><!-- rows rendered by js/log.js --></tbody>
  </table>
</div>
```

Headers are underlined as drawn. Banding is `tbody tr:nth-child(even) > .band`,
a full-bleed `position: absolute; inset: 0` child carrying `background: blue;
mix-blend-mode: difference`, spanning the full row width beneath the cell text.
It needs to be a child rather than a background on the `<tr>` itself, because the
blend has to compose against the ground while the text paints above it
unblended.

`<tbody>` ships empty and is filled by script. Accepted: the table is the one
part of the site that requires JS, and it is the part that will be genuinely
dynamic. A `<noscript>` line inside the box points at the Strava group instead.

### Data seam

```js
// js/activities.js
const ACTIVITIES = [
  { member: "…", activity: "…", date: "30 AUG-26", stat: "8.2 KM" },
  // 10 entries
];
```

```js
// js/log.js
async function loadActivities() { return ACTIVITIES; }  // ← becomes the fetch

const ROW_COUNT = 10;
render(pad(await loadActivities(), ROW_COUNT));
```

`loadActivities` is the single function the Strava integration replaces; nothing
else in `log.js` knows where rows come from. `pad` fills to `ROW_COUNT` with
empty rows so banding stays intact, and `render` truncates beyond it.

Placeholder content: ten club-plausible member names, Strava-flavoured activity
titles, dates descending from `30 AUG-26`, and a `stat` matched to each activity
type per decision 6.

---

## Phone layout (derived)

Following v1's phone conventions: 380-wide stage, content boxes 366 wide at
left 12, `html { font-size: calc(100vw / 380) }`.

- **Tab strip** carries over unchanged — 366x50, three 122px cells.
- **Start view** keeps v1's phone composition, shifted to seat the tab strip
  above the title box. The two extra runners (`r5`, `r6`) and the `d-only` diet
  bowl behave as they do today.
- **Log view** cannot hold four columns at 366 wide, so each row reflows to two
  lines — `member` + `stat`, then `activity` + `date` — with the band covering
  both lines. Row height roughly doubles; the box height and therefore
  `border-table-m.svg` follow from the final row metrics. The 18px table type
  likely needs to come down; the exact size is settled against a render.

This reflow is the only invented geometry in this design. It stands in until a v2
phone frame exists, at which point it is re-transcribed like everything else.

---

## Verification

No test framework exists and none is added; verification follows the project's
existing practice of rendering and comparing against Figma.

For each of the three pages, at 1440x1024 and 390x1024:

1. Render headless and compare against the corresponding Figma frame. `index.html`
   must differ from the v1 frame **only** by the wordmark position and the tab
   strip.
2. Confirm the box's top brush line runs **continuously** across all three tabs
   at y=286–287 and that the active cell's fill stops at y=285, matching the
   measured table in "The active tab does not interrupt the box border". A fill
   that swallows the line means the strip is painting above `.stage::before`.
3. Confirm the active tab samples ~`#d10000`, not `#e30b19` — that is how you know
   `mix-blend-mode: color-burn` survived onto the active cell.
4. Exercise hover and `:focus-visible` on all three tabs, and tab-key order
   through the strip.
5. On `log-of-gains.html`, confirm ten rows, headers underlined, the box exactly
   791x525 with its brush border registered on its edges, and that a banded row
   samples **`#d8cc43`** — the difference-blend result. A flat yellow that does not
   match means the band was hardcoded instead of blended.

The render recipe goes into `NOTES.md` beside the existing `og.html` one.

---

## NOTES.md additions

The file exists to hold the *why*, and v2 adds three things that will otherwise
look arbitrary:

- The red-on-red border trick, and why there is one tab export rather than nine.
- Why the start view's geometry was not re-transcribed (v2's `Frame 16` is
  identical to v1's `Frame 15`).
- That the phone log layout is derived, not transcribed, and what needs redoing
  when a phone frame lands.

Plus the new node IDs, the Overpass Mono addition, the blue-plus-difference band
(which will otherwise look like a mistake to the next reader), the 799-vs-791
drift and its resolution, and the fixed 10-row constraint tying the box height to
`border-table-d.svg`.

---

## Out of scope

- The real Strava API. It needs OAuth and a token that cannot live in a static
  page, so it will arrive as a fetched JSON file or a build step — either way it
  replaces `loadActivities` and nothing else.
- Shop content.
- A v2 phone frame.
- `assets/banner-strava.png`, currently untracked in the working tree; left alone.
