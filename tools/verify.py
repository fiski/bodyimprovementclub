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

# Tab-strip geometry (desktop). TAB_CELL_W is under active review against the
# Figma source and may change (e.g. to 144.128) — everything that samples a
# tab cell derives its window from these constants so a retune is one edit.
TAB_STRIP_LEFT = 324      # desktop x of the strip's left edge (settled)
TAB_CELL_W = 122          # per-cell width — UNDER REVIEW, may change
TAB_SAMPLE_INSET = 6      # inset from each cell edge when sampling its fill

# Content box's top brush line (desktop). A hand-drawn brush stroke wobbles a
# couple of px along its length rather than holding a fixed row, so checks for
# it scan a short band and take the reddest row rather than sampling one fixed
# 2px band — see check_shell.
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
    # takes the reddest row — but the scan must START at BOX_TOP and never
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
