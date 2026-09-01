# Body Improvement Club — implementation notes

Reference for `index.html`, `style.css` and `og.html`. The source files carry no
comments; everything that explains *why* they look the way they do lives here.

Figma file: `BgBx1W0MizlqEKMRBrGjdk`

- desktop node `33:945` / `5:653` — 1440x1024 composition
- phone node `6:1847` — 390x1024 composition

---

## index.html

### Link preview

`og:image` MUST be absolute — scrapers do not resolve relative URLs, and GitHub
Pages serves this project site from a `/bodyimprovementclub` subpath, so a
root-relative path would 404. Update both the URLs in the head and the Pages
settings together if the site ever moves to a custom domain.

`assets/og-image.png` is rendered from `og.html`; see that file to regenerate.

Facebook, LinkedIn and X cache a scrape aggressively — after changing the card,
re-scrape the URL in each platform's debugger to see the new one.

### Markup notes

- `.i--diet` (`d-only`) is desktop-only: the phone composition has no diet-bowl
  icon.
- The icon strips are a collage; per-icon offsets live in `style.css` so they can
  differ between the desktop and phone compositions. `r5`/`r6` are the two extra
  runners the phone layout adds.
- The whole `.box--link` is the link, not just the label: the Figma Hover variant
  fills the entire button. Its brush border is drawn by `.stage::before`.

---

## style.css

Geometry is transcribed from the file's absolute child transforms, read via the
Plugin API — NOT from Figma's generated Tailwind, which offsets every child of a
stroked frame by half the stroke width.

### Brush strokes

Box strokes are BRUSH strokes (Figma's hand-drawn stroke style) — solid `#e30b19`
at 100%, weight 4 on the title box and the strava link button, 1.85 on the icon
strips, 1 on the panel, all `strokeAlign: CENTER` — but painted as a bundle of
wobbling ink lines rather than one clean rule. Neither Dev Mode nor the Plugin API
exposes the brush; both report a plain solid stroke, which is why an earlier
transcription drew flat rules and why sampling a render reads a washed-out ~25%
alpha (the gaps between bristles, not the colour).

No CSS border can draw this, so each stroked frame was exported from Figma as a
flattened outline path (`assets/borders/*.svg`) and is composited by
`.stage::before`.

The exported outlines ride on one overlay pseudo-element rather than on the boxes
themselves, for two reasons: a CENTER-aligned brush overflows the frame rect by
~2px on every side and would be cut by the boxes' own `overflow: hidden`, and in
Figma a frame's stroke paints ABOVE its children, which the `z-index` reproduces
(the desktop runner clipped at the left edge of the runners box has the line drawn
over it, not under).

Each layer sits at (frame origin − overflow) at the SVG's natural size, so the
line straddles the frame edge exactly as CENTER alignment does. Overflow is half
the difference between the export's bounds and the frame rect: e.g. the phone
title box is 366x171 and its export 370x175, so `2rem`.

Backgrounds do not paint outside their box, so `.stage::before` has to be at least
as tall as the lowest brush layer: y=922 on the phone, 969 on desktop. Both
`.stage` heights clear that, so it simply fills the stage.

### v2 exports

`border-tabs.svg` (370x54) is the tab strip: the `Menu` component with every cell
fill and label removed, so it is stroke-only. The active cell's red fill is CSS,
not baked in — otherwise it could not move between pages.

`border-table-d.svg` (795x529) is the log/shop box. The `Table` component was
drawn 799x533 but its row grid sums to 743, the interior a 791 box implies
(`791 - 2*24` padding), so the component was resized to 791x525 to match the grid
it was built for. Both exports carry the usual 2px brush overflow per side.

Re-exporting either border later: the naive recipe (clone the component, then
remove each cell's children directly) throws `Removing this node is not
allowed`, because both the Table clone's children and the Menu's three cells
are component instances, and Figma refuses to remove an instance's children
directly. Call `detachInstance()` first — on the clone itself for the table,
and on *each cell* for the tab strip (detaching the outer Menu clone alone is
not enough; every `Menu item` cell inside it is still its own instance and
needs its own `detachInstance()` before its label can be removed).

The `Menu` component's middle cell (`log of gains`) was found HUG-sized, auto-
fitting its label to 144.13px while its siblings stayed FIXED at 122px — a drift
from the intended three-equal-122px strip (366 wide, flush with the 366px phone
content box). It has been pinned to FIXED 122 to match its siblings. If a future
edit sets it back to HUG, the cell will silently widen to fit whatever label is
in it, `Menu` will stop being 366 wide, and `border-tabs.svg` will no longer
align with the tab strip it is composited over — re-export is not enough, the
component's sizing mode has to stay FIXED. Note the label itself never fit the
122px cell's padding even before this (`log of gains` ink is ~111px in an
81.9px content box after the 20.064px horizontal padding), so the CSS for this
strip drops horizontal padding on the tab labels and centers them instead.

### Palette

The eight tokens on `:root` mirror, one-for-one, the "Color" variable collection
in the Figma file (collection `VariableCollectionId:40:28`, single mode
"Default"). Each custom property is named after its Figma variable, so a change on
either side has an obvious counterpart on the other. Everything further down
composes from these — no page rule carries a raw hex.

| Token | Value | Role |
| --- | --- | --- |
| `--ground` | `#d8ccbc` | page background |
| `--red` | `#e30b19` | strokes, title |
| `--box-fill` | `#d3c7b7` | tagline box fill |
| `--ink` | `#000000` | tagline type |
| `--link-ink` | `#7f1010` | strava label |
| `--link-hover` | `#3a67ed` | strava hover fill |
| `--ink-inverse` | `#ffffff` | label reversed out of the hover fill |

`--grid-line`: Figma's 0.5px grid strokes resolve to a 1px line at 50% alpha
(measured off the export, which renders these correctly). The Figma variable is
the opaque base colour, `#c90000` — matching the strokes as authored; the `0.5`
in the stylesheet is emulating that sub-pixel rasterisation, not a colour choice,
which is why the two values differ.

`--stroke-alpha` / `--stroke`: the desktop tagline box is the one stroke still
drawn by CSS — it was not among the brush exports. Dial the alpha if it reads
heavier than the brushed lines around it.

### Scaling

Both compositions are fixed-size posters, so rather than reflow them, `1rem` is
defined as one design pixel and tracks the viewport. The whole canvas scales as a
unit and never overflows horizontally. Hairline rules keep a real 1px floor so
they stay crisp at reduced scale.

**Phone.** Canvas is 390x1024 design px. The scale is bound by WIDTH alone: the
poster is drawn edge to edge and the page scrolls vertically whenever that makes
it taller than the viewport. It used to be bound by both axes so that nothing ever
scrolled, but on a phone the height was almost always the binding one and the
poster shrank to roughly three quarters of the screen — a narrow column of drawing
with empty ground down either side.

The divisor is not the raw canvas but the INKED extent plus a margin, so the
poster is sized to what is actually drawn rather than to the empty background
around it. The phone composition inks x 10..380 (the brush borders start 2px
outside the 12px gutter):

    width 380 = 370 + 10  →  a 5px margin on each side

The stage is then made 380 wide too and its contents nudged left, rather than left
at the canvas's own 390 with the surplus gutter hanging off the edge: overflow
that is only clipped still pans under a finger on iOS.

No upper cap: the desktop composition takes over at 768px, so the largest this can
reach is a touch over 2px per design px, on the widest phone held in portrait.

**Desktop.** Canvas is 1440x1024, never upscaled past 1:1. Fractional Figma nudge
values (178.339, 468.509, 599.679 …) are snapped to whole design px; they are
artifacts of dragging, not intent, and the sub-pixel versions smear every 1px rule
across two rows.

### body

Nothing is meant to overflow horizontally — the stage is built to the viewport
width — so `overflow-x: hidden` is a backstop against sub-pixel rounding and
against `100vw` over-reporting by the width of a scrollbar, not the thing keeping
the poster in place. It cannot be the thing: a clipped overflow still drags under a
finger on iOS.

Vertically the page is free to scroll, which is the whole point of sizing the
poster to the width. `min-height` rather than `height` so that a poster taller than
the viewport grows this box instead of overflowing a centred flex line, which would
put its top edge out of reach of the scrollbar.

No `touch-action` here: pinch-zoom must still pan in both axes.

### .grain

`Film_Grain` is `children[0]` in Figma — the BOTTOM layer. It shows through
unfilled frames but is covered by the tagline box's opaque fill. Verified: the
tagline interior in Figma's export is flat `#d3c7b7`, std 0.0. Covers the viewport,
not just the stage, so the texture reads on any screen size.

### .stage

The phone box is the scroll height, not the height of the Figma frame: 946 = the
inked extent's bottom edge at 922 — the Strava button's brush, 2px below its 920
rect edge — plus a 24px bottom margin. The top margin needs no help; the
composition's own empty band above the logo at y=54 supplies it.

The width is the 380 the scale was fitted to, NOT the canvas's 390: at 390 the
stage is wider than the viewport by its empty right-hand gutter, and an overflow
that is merely clipped is still an overflow — iOS hands the user a horizontal drag
over it. So the box is cut to the fitted width and the shift slides the composition
into it, left 5, which puts the inked extent (x 10..380) at 5..375 and leaves the
5px margin on each side.

It is a transform, not an edit to the children's x offsets, so the Figma
coordinates stay a faithful transcription — the composition is moved as a unit,
exactly as it is scaled as a unit. What the shift pushes past the viewport is 5
design px of empty gutter off the LEFT edge, and a box's left overflow is not
scrollable in a left-to-right page — so there is nothing to drag in either
direction. Vertically there is no shift: the canvas's own band above the logo at
y=54 is the top margin, and where the viewport is taller than the poster, body's
flex centring places it.

On desktop it is the full frame, not the inked extent, and no shift: the desktop
content (129..969 of 1024) already sits inside its own canvas with margin to spare,
and the canvas is fitted to both axes, so this composition neither scrolls nor
overflows.

### Boxes

- `.box--title` — `clipsContent: true`
- `.box--runners` — `clipsContent: true` (runner clipped)
- `.box--exercises` — `clipsContent: false`
- `.panel` — `overflow: hidden` clips the grid gradients; the stroke is a brush
  layer.
- `.logo` on phone is lifted 10 off Figma's y=64 — the top margin is now real page
  space above a scrolling poster, not the empty band inside a fitted frame.

The `background-position` values on `.stage::before` are each the frame origin
minus the brush overflow:

| Layer | Phone | Desktop |
| --- | --- | --- |
| title | 12,214 − 2 | 324,286 − 2 |
| runners | 12,385 − 1 | 324,468 − 2 |
| exercises | 12,708 − 1 | 671,468 − 2 |
| panel | 12,469 − 2 | 324,600 − 2.5 |
| link | 12,792 − 2 | 323,839 − 2 |

### Strava link button

Figma component "Link button" (`33:1764`), variants Default / Hover. Same brush box
as the other frames — weight 4, `strokeAlign: CENTER`, so its outline export
overflows the rect by 2px like the title box — drawn by `.stage::before`, which is
why nothing in `.box--link` paints a border.

The `<a>` is the whole box, not just the label: the Hover variant fills the entire
frame, so the box is what has to respond. The fill sits under the brush layer
(`z-index: 2` on `.stage::before`) exactly as a frame fill sits under its stroke in
Figma, and that layer is `pointer-events: none` so it never eats the click. The
default variant has no fill, so the grain shows through.

Vertical placement is flex centring rather than Figma's 35.67 padding: the
instances are 128 tall against the component's 129.34, and centring the 58px
two-line label is what puts it at y=35 in both.

`:focus-visible` is not in the Figma file — it is the keyboard equivalent of the
Hover state, so the one interactive element on the page is reachable without a
mouse.

On desktop `.box--link` sits directly under the panel (600 + 239 = 839) at the
runners box's width. The 323 left is Figma's, 1px shy of the 324 column the other
boxes use.

### Graph-paper panel

Two gradient layers replace the 127 individual rule rectangles in the file. Rules
cover only the top 215 design px of the 239px panel, leaving the blank strip above
the bottom stroke that the design calls for.

### Tagline

The fill is opaque so the graph-paper rules stop at the box edge — which also hides
the `.grain` layer underneath. The texture is re-composited here from the same
image, under a flat scrim of the box fill at 80% (reproducing `.grain`'s 0.20
opacity).

Sizing mirrors the `.grain` `<img>`'s `object-fit: cover` against the viewport, but
written in viewport units rather than the `cover` keyword: the image is 1440x1024,
so a width of `max(100vw, 140.625vh)` with auto height is that exact cover scale.
Stated this way the grain matches the surrounding page even where
`background-attachment: fixed` degrades to scroll (iOS Safari) and the positioning
area becomes the box — only the crop shifts, never the scale, and a shifted crop of
noise is indistinguishable.

`.panel::after` (the horizontal rules) is effectively the panel's last child, so it
would paint over this opaque box without an explicit stacking bump — hence
`z-index: 1`.

No stroke on the phone tagline box — the desktop one has a 1px INSIDE stroke, this
variant has none.

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

### The log table

The banded rows are BLUE, not yellow: each even-row cell blends a `blue` layer
against a `var(--ground)` layer via `background-blend-mode: difference`, exactly
as the Figma component does. Against the ground that computes to
`|#d8ccbc - #0000ff| = #d8cc43`, which is what the frames sample. Keeping the
mechanism rather than the result means the band tracks `--ground` if the ground is
ever retuned, and it grains the way the frame does. Do not "simplify" it to a
yellow token.

The band is painted as the cell's own `background-image` (two stacked
`linear-gradient(solid, solid)` layers blended with `background-blend-mode`),
NOT a `::before`. An absolutely positioned `::before` paints in a later phase
than the cell's in-flow text and gets caught by its own `mix-blend-mode`,
inverting the glyphs along with the ground (`#7f1010` ink reads as `#7f10ef`
under the band — verified by `tools/verify.py log`, which samples row text for
this). A `background-image` paints in the background layer, guaranteed below
content, so the dark-red ink stays dark-red on top of the yellow band. Do not
reach for `z-index: -1` on a `::before` instead — that joins the root stacking
context and lands under `.grain` at `z-index: 0`, washing the band out.

The header's `padding-bottom: 32rem` is the drawn 8px header padding plus the
drawn 24px gap between header and rows. Folding the gap into the header cell puts
the first row at y=95 with no spacer row, and keeps the whole box at
40 + 23 + 32 + 390 + 40 = 525.

`height: 23rem` on the row cells is necessary but not sufficient to keep a padded
EMPTY row 39px tall: a `<td>` with no light-DOM children gets no line box in this
renderer, so the height alone still collapses (loses `padding: 8rem 0`, landing
at 23rem not 39rem) and the banding drops out on a short feed. The
`.log tbody td:empty::after { content: "\00a0"; }` rule just below restores the
line box for any genuinely empty cell — a padded row from `log.js`'s `pad()`, or
a real feed entry with a blank field — so `height: 23rem` plus that generated
nbsp is what actually holds the row at 39rem. See `## js/` further down for how
`pad()`'s `EMPTY` rows exercise this.

`white-space: nowrap` on `.log th`/`.log td` is required, not decorative: several
of the hardcoded stat values (e.g. "8.2 KM") measure wider than a stat column
sized for Figma's 5-character placeholder ("index") at Overpass Mono's real
advance width, and without `nowrap` the space before the unit becomes a
soft-wrap point, doubling that row's height and knocking every following row
off the 39rem pitch (verified by sampling row bands in `tools/verify.py log` —
omitting `nowrap` flips rows 2-5 and 10 and paints an 11th row below y=800).
Single-line rows are load-bearing for the fixed 39rem pitch, not just tidy.

Column widths are `218 / 319 / 118 / 88`, not the drawn `218 / 351 / 118 / 56`:
the drawn 56rem stat column was sized for the 5-character placeholder and is
too narrow for real values ("31.7 KM", "1:04:20", ~81rem at 18rem Overpass
Mono) — with `nowrap` in place those values overflowed rightward past the box's
own interior and out through its brush border rather than wrapping. Activity
gives up exactly the 32rem stat needs (351 → 319) and stat gains that same
32rem (56 → 88), so the four still sum to the drawn 743. Activity was picked
as the donor because it has real slack even after losing 32rem: its content
box is 301rem after its own gutter, and its longest value ("gravel loop
north") measures only ~202rem. `tools/verify.py log` asserts no cell ink
appears past the interior's right edge (x=1091) to catch this class of
regression.

### The phone log table is DERIVED, not transcribed

There is no v2 phone frame for the log table. Four 18px columns do not fit the
366-wide phone box, so each row reflows to two lines -- member + stat on the
first, activity + date on the second -- at 15px/20px, and the header is
hidden with `display: none`. That removes it from the accessibility tree in
every major browser too, so this is hidden from ALL users at phone width, not
just sighted ones -- a four-column header cannot honestly label a two-line
row for anyone, and the reflowed rows are self-describing by position and
weight. The markup still keeps `<thead>` and `scope="col"`, but only because
the desktop layout needs them; neither does anything for a phone-width user,
assistive tech included.

Two phone borders exist, not one, because the two phone boxes are different
heights: `border-box-m.svg` (370x529) is `shop.html`'s unchanged 366x525
centred-copy box; `border-table-m.svg` (370x644) is `log-of-gains.html`'s
reflowed, taller box. On desktop the two pages still share one export
(`border-table-d.svg`) because both boxes are 791x525 there -- only the phone
layout diverges.

Both were produced by the same recipe as the desktop `border-table-d.svg`
(clone `Table` (`59:56`) via `createInstance()`, `detachInstance()` the clone
itself, remove its children, resize, export, delete the clone) -- NOT by
rescaling `border-table-d.svg`. Squeezing 795 down to 370 is a 0.465 horizontal
compression that a hand-drawn brush stroke does not survive: the bristles
visibly bunch up. Re-exporting at the real phone width keeps the stroke
density correct.

`.box--table`'s phone height (640rem) was measured, not computed from
`8 + 10x56 + 8`-style arithmetic: a script rendered the page, read
`getBoundingClientRect()` on the last row and the box, and converted back to
rem via the root font-size. The arithmetic prediction (`40 + 10x56 + 40 =
640`) landed within 0.05rem of the measured value, but the measurement is
what was kept -- grid line-box rounding at a fractional rem can move this,
and only a render proves it settled.

On the phone the band moves from a per-cell `background-image` to the row's
own `::after`, because the rows are `display: grid` there and
`position: relative` + `isolation: isolate` on a grid container is reliable
where `position: relative` is not on a table row (see the desktop notes above
on why a `::before`/`z-index` approach fails). The row `::after` still uses
the same self-contained two-layer `background-blend-mode: difference` trick
as the desktop per-cell band (`linear-gradient(blue,blue)` blended against
`linear-gradient(var(--ground),var(--ground))`) rather than `background: blue;
mix-blend-mode: difference` blending against whatever happens to be painted
behind the row (the grain texture, not a flat ground) -- the two-layer form is
correct regardless of backdrop, and `column-gap` between the member/activity
and stat/date columns is safe because the row's own `::after` covers the
gap along with the rest of the row's box.

When a phone frame for the log table is eventually drawn in Figma, all of
this -- the two-line layout, the 640rem box height, both border exports --
should be re-transcribed and re-exported rather than assumed still correct.

---

## og.html

SOURCE for `assets/og-image.png` — the link preview served by the `og:image` tag in
`index.html`. Not linked from the site; it exists so the card can be re-rendered if
the mark or the ground ever changes.

The card is the squared BIC mark and nothing else. Its letters already step down to
the right, so the diagonal is the whole composition — no title box, no icon strip,
no wordmark. At the size a link preview is actually shown, that is the only part
that stays readable anyway.

Uses `logo-squared-plain.svg`, not either of the `logo-squared` twins: both of
those bake film grain across their own 248x248 box, which prints the mark's square
onto the ground as a lighter patch. The plain mark is the same three letterforms
with that layer dropped, so the grain here is the page's single full-bleed layer,
as on the site.

The page carries the same 20% film grain as the site, full bleed, on `#d8ccbc`
(`--ground`).

Regenerate (Chrome headless, 2x for antialiasing, downscaled to 1200x630):

```sh
chrome --headless --disable-gpu --hide-scrollbars \
       --screenshot=card@2x.png --window-size=1200,630 \
       --force-device-scale-factor=2 --virtual-time-budget=8000 \
       og.html
python -c "from PIL import Image; i=Image.open('card@2x.png').convert('RGB'); \
           i.resize((1200,630), Image.LANCZOS).save('assets/og-image.png')"
```

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

`EMPTY`'s fields are genuinely empty strings (`""`), matching a real feed's
blank field. A truly empty `<td>` would otherwise lose its line box and its
39rem row height — see the `.log tbody td:empty::after` rule in `style.css`'s
`### The log table` section, which is what actually keeps a padded (or
blank-field) row banded.
