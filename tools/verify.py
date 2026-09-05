#!/usr/bin/env python
"""Render each page headless and assert measured pixel facts about it.

Every expected number here is a raw Figma pixel, which is also a CSS px at the
1440x1024 desktop render size, because .stage is scaled so 1rem == 1px there.

The phone render is different: Chrome (Windows) clamps windows to a ~500px
minimum and subtracts 22px of chrome, so a naive --window-size=380 yields a
512px viewport and silently renders the phone stage zoomed and clipped rather
than at 1rem == 1px. See PHONE and PHONE_SCALE below.
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

# The phone render size was empirically measured, not assumed. --window-size
# is unreliable here in two different ways depending on how you probe it:
#   - via --dump-dom, Chrome reports a *reduced* innerWidth (e.g. request 380
#     comes back as 512, request 760 comes back as 738) -- some ~22px of
#     window chrome being subtracted.
#   - but via the --screenshot flag this codebase actually uses, that
#     reduction does NOT apply to layout/media-query evaluation: the raster
#     is produced at the *requested* width taken literally. So requesting
#     782 (380 + 22, to "net" 760 after the dump-dom-measured subtraction)
#     instead lands on 782 literal CSS px -- which is >= the 768 breakpoint,
#     silently flipping the page into its *desktop* layout while every mobile
#     rem coordinate is still what gets asserted against, producing a
#     wholesale mismatch that looks like "everything is wrong" rather than a
#     clean off-by-some-scale error.
#   Requesting exactly 760 (2 x the 380rem stage width, comfortably under
#   768) was verified with painted marker divs at known rem coordinates: the
#   screenshot places them at their rem value x 2 to within a couple of px,
#   with no clipping and no crossover into the desktop rules. Height just
#   needs headroom past the stage's 1018rem x 2 = 2036px bottom.
#   If this ever needs re-measuring: paint absolutely-positioned marker divs
#   at known rem coordinates into a copy of index.html, screenshot it at a
#   candidate --window-size, and look for a request where marker positions
#   land at rem x SCALE -- not some other size where they silently shift to
#   desktop coordinates or a fractional scale.
PHONE = (760, 2040)
PHONE_SCALE = 2

# Tab-strip geometry (desktop). Everything that samples a tab cell derives
# its window from these constants so a retune is one edit.
TAB_STRIP_LEFT = 324      # desktop x of the strip's left edge (settled)
TAB_CELL_W = 122          # per-cell width (settled)
TAB_SAMPLE_INSET = 6      # inset from each cell edge when sampling its fill

# Content box's top brush line (desktop). A hand-drawn brush stroke wobbles a
# couple of px along its length rather than holding a fixed row, so checks for
# it scan a short band and take the reddest row rather than sampling one fixed
# 2px band - see check_shell.
BOX_TOP = 286        # y of the content box's top edge
BOX_LINE_SCAN = 3    # rows to scan; the brush line wobbles 1-2px along its length


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


def spread(im, x0, x1, y0, y1):
    """Population std of the red channel over a window.

    The film grain is what this measures. A window of untouched paper reads
    ~5.5; a flat fill painted over the paper reads 0.00. Red because the band
    leaves R and G alone (differencing against pure blue only touches B), so
    R carries the grain identically inside and outside a band.
    """
    px = [im.getpixel((x, y))[0] for y in range(y0, y1) for x in range(x0, x1)]
    return st.pstdev(px)


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
    # A hand-drawn brush stroke wobbles a couple of px along its length rather
    # than holding a fixed row, so this scans a short band below BOX_TOP and
    # takes the reddest row - but the scan must START at BOX_TOP and never
    # look above it: the active tab's red fill ends just above BOX_TOP, and
    # scanning into it would make this check pass on that fill instead of the
    # line, which is vacuous under exactly the cell where it matters most.
    for label, x0, x1 in [("under tab 1", 330, 440),
                          ("under tab 2", 452, 562),
                          ("under tab 3", 574, 684),
                          ("right of strip", 900, 1000)]:
        best = max((median(im, x0, x1, y, y + 1)
                    for y in range(BOX_TOP, BOX_TOP + BOX_LINE_SCAN)),
                   key=redness)
        r.check(redness(best) > 25,
                f"{page}: top brush line present {label}", hexof(best), "reddish")


def tab_sample_window(cell):
    """The x-range to sample a tab cell's fill, inset from its own edges."""
    left = TAB_STRIP_LEFT + cell * TAB_CELL_W
    return left + TAB_SAMPLE_INSET, left + TAB_CELL_W - TAB_SAMPLE_INSET


def check_active_tab(r, im, page, cell):
    """Cell 0/1/2 is the active one: colour-burned red fill, ending at y=285."""
    x0, x1 = tab_sample_window(cell)
    fill = median(im, x0, x1, 250, 284)
    r.check(near(fill, (209, 0, 0), tol=12),
            f"{page}: active tab {cell} is colour-burned red", hexof(fill), "#d10000")
    # Guard: nothing else here confirms the fill actually STOPS above the
    # box's top line. If `.tabs`' 50rem height ever drifted, the fill would
    # run past y=286 and check_shell's "top brush line present" checks would
    # then pass on the fill itself rather than the line -- a false pass on
    # the very check meant to catch this. Sample just below the line (the
    # line itself lives in BOX_TOP..BOX_TOP+BOX_LINE_SCAN, i.e. 286-288) and
    # confirm it reads ground, not fill.
    below_line = median(im, x0, x1, 291, 295)
    r.check(near(below_line, (214, 202, 188), tol=12),
            f"{page}: active tab {cell} fill stops above the box's top line",
            hexof(below_line), "ground")
    for other in range(3):
        if other == cell:
            continue
        ox0, ox1 = tab_sample_window(other)
        inactive = median(im, ox0, ox1, 250, 284)
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

    # The band must carry the film grain, not just the grain's average colour.
    # Figma paints the row's blue fill with `background-blend-mode: difference`
    # against the composition beneath it, which is Film_Grain over the ground,
    # so the texture runs through the band at full strength: the frame measures
    # std 5.38 on the band against 5.55 on the ground beside it. Differencing
    # against a flat --ground swatch instead gives the right mean (#d8cc43) and
    # a dead-flat slab -- std 0.00 -- which is a defect no colour check can see,
    # since every sample in this file is a median or a mean. Sample the row's
    # own 8rem top padding, which carries no glyphs whatever the feed says.
    for i in (1, 3, 5, 7, 9):
        top = 381 + i * 39
        band = spread(im, 400, 1080, top + 1, top + 7)
        paper = spread(im, 400, 1080, top + 40, top + 46)
        r.check(band > 3.0,
                f"log: row {i + 1} band carries the grain, not a flat fill",
                "std %.2f" % band, "> 3.0 (paper beside it: %.2f)" % paper)

    bottom = median(im, 550, 566, 800, 806)
    r.check(near(bottom, (216, 204, 188), tol=10),
            "log: no 11th row below y=800", hexof(bottom), "ground")

    # The band must paint BENEATH the text: an inverted #7f1010 reads #7f10ef.
    # B=16 dark red vs B=239 inverted, so the blue channel separates them cleanly.
    for i in (1, 3, 5, 7, 9):                 # banded rows, 0-indexed
        top = 381 + i * 39
        ink = min((im.getpixel((x, y)) for y in range(top + 4, top + 31)
                   for x in range(348, 500)), key=sum)
        # No `sum(ink) < 300` term here (unlike the phone check below): this band is
        # the cell's own `background-image`, and an element's own background always
        # paints beneath its own text, so full occlusion can't happen -- only
        # recolouring (#7f10ef) is reachable. Reconsider if this ever moves off
        # `background-image`.
        r.check(ink[2] < 100,
                f"log: row {i + 1} text is not inverted by the band", hexof(ink), "#7f1010-ish")

    # No cell text may spill past the box interior's right edge (x=1091).
    # sum < 400 catches dark glyph ink without tripping on the washed pink border (~577).
    spill = [x for x in range(1092, 1140)
             if any(sum(im.getpixel((x, y))) < 400 for y in range(381, 771))]
    r.check(not spill, "log: no cell text spills past the box interior", spill[:6], "[]")


def check_shop(r):
    im = shot("shop.html", DESKTOP)
    check_shell(r, im, "shop")
    check_active_tab(r, im, "shop", 2)


def check_phone(r):
    # Expectations are written in rem (the page's own units) and scaled to px
    # at the point of use, since PHONE renders at exactly PHONE_SCALE px/rem.
    #
    # .stage carries `transform: translateX(-5rem)` on phone (unlike desktop,
    # where it's none), which shifts every x-coordinate in the render left by
    # 5rem relative to the box's own left/width numbers. y is untouched.
    STAGE_SHIFT_X_REM = -5

    for page in ("index.html", "log-of-gains.html", "shop.html"):
        im = shot(page, PHONE)

        runs = ink_runs(im, 300 * PHONE_SCALE, 0, PHONE[0])
        edges = (runs[0][0], runs[-1][-1]) if len(runs) >= 2 else None
        want = ((12 + STAGE_SHIFT_X_REM) * PHONE_SCALE,
                (378 + STAGE_SHIFT_X_REM) * PHONE_SCALE)
        r.check(edges is not None and abs(edges[0] - want[0]) <= 4 * PHONE_SCALE
                and abs(edges[1] - want[1]) <= 4 * PHONE_SCALE,
                f"phone {page}: box spans x=12..378rem (shifted {STAGE_SHIFT_X_REM}rem by .stage)",
                edges, want)

        # Guard: the two checks above only make sense if the render actually
        # achieved PHONE_SCALE px/rem. Anchor this on the box's rendered
        # WIDTH (366rem), not either edge: an edge sits close to the
        # translateX origin (the left edge is only 7rem from it), so a
        # proportional scale error barely moves it -- a 3% scale error (1.942
        # vs 2.0 px/rem) shifts the left edge by under half a px, comfortably
        # inside a few-px tolerance, and would pass while every downstream
        # measurement is silently wrong. The 366rem span moves ~22px for that
        # same 3% error, and is independent of STAGE_SHIFT_X_REM entirely, so
        # a wrong shift constant can't mask a wrong scale either. The ±3px
        # tolerance here is deliberately tighter than the box-span check's
        # 4 * PHONE_SCALE (roughly 0.4% of the 732px span vs that check's
        # looser position tolerance) -- this check exists to catch scale
        # drift specifically, so it holds a stricter bar on purpose.
        want_span = 366 * PHONE_SCALE
        span = edges[1] - edges[0] if edges else None
        r.check(span is not None and abs(span - want_span) <= 3,
                f"phone {page}: render achieves {PHONE_SCALE}px/rem "
                f"(box spans 366rem == {want_span}px) -- if this fails, "
                "Chrome's window sizing has changed; re-measure PHONE",
                span, want_span)

        # The strip's cells are 122rem wide here too, so cell 2 starts at
        # 12+244rem. A run count alone is not enough: label glyphs on the
        # inactive tabs can themselves produce >=4 ink runs on this scanline,
        # so a strip rendered far too narrow (or too wide) could still pass
        # a bare count check. Mirror the box-span check above and assert the
        # strip's actual extent instead; keep the count as a secondary guard.
        strip = ink_runs(im, 260 * PHONE_SCALE, 0, PHONE[0])
        strip_edges = (strip[0][0], strip[-1][-1]) if strip else None
        want_strip = ((12 + STAGE_SHIFT_X_REM) * PHONE_SCALE,
                      (378 + STAGE_SHIFT_X_REM) * PHONE_SCALE)
        r.check(strip_edges is not None
                and abs(strip_edges[0] - want_strip[0]) <= 4 * PHONE_SCALE
                and abs(strip_edges[1] - want_strip[1]) <= 4 * PHONE_SCALE,
                f"phone {page}: strip spans x=12..378rem (shifted {STAGE_SHIFT_X_REM}rem by .stage)",
                strip_edges, want_strip)
        r.check(len(strip) >= 4,
                f"phone {page}: strip shows three cells at y=260rem", strip, ">=4 runs")

        # The strip sits ON the box: its bottom edge is the box's top edge.
        # The border artwork's stroke anti-aliases across this boundary, so a
        # narrow 2rem band can land squarely on a thin (near-empty) row of it;
        # scan a slightly wider 4rem band centred on the seam so a single such
        # row can't sink the median.
        seam = median(im, 40 * PHONE_SCALE, 340 * PHONE_SCALE,
                      285 * PHONE_SCALE, 289 * PHONE_SCALE)
        r.check(redness(seam) > 25,
                f"phone {page}: strip/box seam inked at y=286rem", hexof(seam), "reddish")

        if page == "log-of-gains.html":
            # The phone reflow moved the band from the desktop's per-cell
            # background to a row-level ::after -- a positioned pseudo-
            # element, the same construct class as the bug check_log guards
            # against (an inverted #7f1010 reading as #7f10ef). Mirror
            # check_log's two assertions here so the riskier mechanism gets
            # the same coverage as the proven one.
            #
            # Box interior: box top 286rem + 40rem top padding = row 1 at
            # y=326rem; each row is an 8rem pad + two 20rem lines + an 8rem
            # pad = 56rem pitch; banded rows are nth-child(even), i.e. 0-
            # indexed i in {1,3,5,7,9}.
            ROWS_TOP = 286 + 40
            ROW_PITCH = 56
            INTERIOR_LEFT = 12 + 24  # box left + left padding

            for i in (1, 3, 5, 7, 9):
                row_top = ROWS_TOP + i * ROW_PITCH

                # Sample inside the row's own top padding (8rem): it never
                # carries glyph content regardless of row text, so this reads
                # the band colour clear of any text -- the difference blend
                # must land on #d8cc43.
                bx0 = (INTERIOR_LEFT + STAGE_SHIFT_X_REM) * PHONE_SCALE
                bx1 = (INTERIOR_LEFT + 280 + STAGE_SHIFT_X_REM) * PHONE_SCALE
                by0 = (row_top + 2) * PHONE_SCALE
                by1 = (row_top + 6) * PHONE_SCALE
                band = median(im, bx0, bx1, by0, by1)
                r.check(near(band, (216, 204, 67), tol=10),
                        f"phone log-of-gains.html: row {i + 1} banded #d8cc43",
                        hexof(band), "#d8cc43")

                # Same grain assertion as check_log, on the phone's separate
                # band mechanism (a row-level ::after rather than a per-cell
                # background). The threshold is lower than the desktop's 3.0
                # because this render is 2px/rem: each grain pixel covers four
                # output pixels, which halves the measured spread.
                texture = spread(im, bx0, bx1, by0, by1)
                r.check(texture > 1.5,
                        f"phone log-of-gains.html: row {i + 1} band carries the grain",
                        "std %.2f" % texture, "> 1.5")

                # The band must paint BENEATH the member-column text (the
                # row's first line): an inverted #7f1010 reads #7f10ef, and
                # B=16 vs B=239 separates them cleanly. B alone is not enough
                # here, though: this mechanism is a positioned ::after, so a
                # missing/wrong z-index doesn't recolour the glyphs the way
                # the desktop mix-blend-mode bug does -- it paints the whole
                # opaque #d8cc43 band ON TOP, occluding the text entirely,
                # and #d8cc43's own B=67 would slip past a bare `< 100` (this
                # was verified empirically: measured (127,16,15) sum=158 for
                # real ink vs (216,204,67) sum=487 for an occluding band, so
                # a sum cap also catches full occlusion that channel-only
                # would miss).
                tx0 = (INTERIOR_LEFT + STAGE_SHIFT_X_REM) * PHONE_SCALE
                tx1 = (INTERIOR_LEFT + 150 + STAGE_SHIFT_X_REM) * PHONE_SCALE
                ty0 = (row_top + 10) * PHONE_SCALE
                ty1 = (row_top + 26) * PHONE_SCALE
                ink = min((im.getpixel((x, y)) for y in range(ty0, ty1)
                           for x in range(tx0, tx1)), key=sum)
                r.check(ink[2] < 100 and sum(ink) < 300,
                        f"phone log-of-gains.html: row {i + 1} text is not inverted/occluded by the band",
                        hexof(ink), "#7f1010-ish")


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
