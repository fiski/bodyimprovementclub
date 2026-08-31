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

States:

- **Inactive** — transparent fill, red brush outline, `--link-ink` label.
- **Active** — solid `--red` fill, cream label (`--ink-inverse` or the ground;
  read the exact fill and text colour off the `Menu item` variant).
- **Hover / focus-visible** — follow the existing `.box--link` precedent:
  `--link-hover` fill with `--ink-inverse` label. Applies to inactive tabs only;
  the active tab is already the current page.

### Why one border export covers every active state

The tab metaphor requires the box's top edge to be *absent* under the active tab,
which naively means a separate box export per active state — nine exports.

It does not, because the brush lines and the active fill are both `--red`. An
opaque red field over a red brush line is indistinguishable from the field, and
the exports are solid `#e30b19` painted as bristles with gaps (see `NOTES.md`).
So the active cell's fill erases, red-on-red, both its own bottom edge and the
segment of the box's top edge beneath it. One shared tab-strip export carrying
every edge, one box export per view, and no z-index reordering against
`.stage::before`.

Verify against the `Menu item` active variant during transcription: if that
variant genuinely drops its bottom stroke in Figma, the effect is identical and
the reasoning above is simply belt-and-braces.

---

## START view

The v1 collage, unchanged. Existing markup for `.box--title`, `.box--runners`,
`.panel`/`.tagline`, `.box--exercises` and `.box--link` carries over verbatim,
as does the `.stage::before` layer set and all five existing border exports.

Changes: `.logo` top 129 → 70, and the tab strip above it.

---

## LOG OF GAINS view

From `Table` instance `58:469`, drawn at (325, 286) 799x533 and placed at the
reconciled (**324**, 286) — a **791x525** box with the
usual 4px brush overflow on each side (`799 = 791 + 8`, `533 = 525 + 8`).

Interior:

- `Table Header` at (24, 40), 751x31
- `Rows` frame at (24, 95), 751x390 — ten `Table Row` instances of exactly 39px,
  flush, ending at y=485
- 40px bottom padding, matching the 40px above the header

Column offsets within the 751-wide row, and the yellow band colour, are read off
the components via the Plugin API during transcription — **not** from Dev Mode,
per the `NOTES.md` warning about stroked-frame offsets. The yellow gets a
`:root` token named after its Figma variable, like the existing eight.

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

Headers are underlined as drawn. Banding is `tbody tr:nth-child(even)` in the
yellow token, spanning the full row width. Row 1 is unbanded.

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
  lines — `member` + `stat`, then `activity` + `date` — with the yellow band
  covering both lines. Row height roughly doubles; the box height and therefore
  `border-table-m.svg` follow from the final row metrics.

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
2. Confirm the active tab reads as continuous with the box — no visible line
   under it, no seam at its edges.
3. Exercise hover and `:focus-visible` on all three tabs, and tab-key order
   through the strip.
4. On `log-of-gains.html`, confirm ten rows, banding on even rows, headers
   underlined, and that the rendered box is exactly 791x525 with the brush border
   registered on its edges.

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

Plus the new node IDs, the new colour token's Figma variable, and the fixed
10-row constraint tying the box height to `border-table-d.svg`.

---

## Out of scope

- The real Strava API. It needs OAuth and a token that cannot live in a static
  page, so it will arrive as a fetched JSON file or a build step — either way it
  replaces `loadActivities` and nothing else.
- Shop content.
- A v2 phone frame.
- `assets/banner strava.png`, currently untracked in the working tree; left alone.
