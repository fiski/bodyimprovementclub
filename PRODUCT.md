# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Members of the Body Improvement Club (a real, existing training group) and the wider public who land on the site via a shared link, search, or social preview. A member's core scenario is checking the shared, Strava-linked activity feed and feeling part of the club; a newcomer's is understanding what the club is and how to join (the Strava group link).

## Product Purpose

The site is the club's shared identity and hangout, not a marketing funnel. It exists to showcase the club's culture and celebrate members' activity ("gains") in an idiosyncratic, high-craft visual voice. Success is the club loving how it looks and feels - there is no conversion metric being optimized for.

## Positioning

Not a competitive product with a market position to defend. What makes it itself is that it's a real training club (running, lifting, cycling, swimming - see the activity feed) with its own deliberate, art-directed visual identity, transcribed pixel-for-pixel from Figma rather than assembled from templated fitness-brand design.

## Operating Context

- Static site, no build step, hosted at bodyimprovement.club via GitHub Pages (see `CNAME`).
- Figma file `BgBx1W0MizlqEKMRBrGjdk` is the design source of truth; `NOTES.md` documents every transcription decision (desktop node `33:945`/`5:653`, phone node `6:1847`) and must be read before editing `index.html`, `log-of-gains.html`, `shop.html`, `og.html`, `style.css`, `js/`, or `tools/`.
- `tools/verify.py` renders each page in headless Chrome and asserts pixel facts against the Figma frames - changes to these pages should stay verifiable this way.
- The activity feed (`log-of-gains.html`) currently reads placeholder data from `js/activities.js`. Real data is meant to come from Strava; because Strava needs OAuth and a token can't live in a static page, the likely integration is a generated JSON file rather than a client-side API call. `loadActivities()` in `js/log.js` is the one seam meant to change.
- The shop page (`shop.html`) previews club kit (a rotating wireframe tee) but has no committed e-commerce plan - it's a teaser, not a store in progress.

## Capabilities and Constraints

- Three pages - `index.html` (start), `log-of-gains.html`, `shop.html` - share `style.css` and one small script (`js/`), no framework, no build step.
- Desktop and phone are two distinct, fixed-size "poster" compositions transcribed from Figma (1440x1024 desktop, 390x1024 phone) that scale as a unit rather than reflow as a fluid grid.
- Brush-stroke borders are pre-rendered SVG exports (Figma's hand-drawn brush stroke style has no CSS equivalent), composited via `.stage::before` layers, not drawn as element borders.
- The log-of-gains table is fixed at 10 rows, sized to match a specific border SVG export; changing the row count requires re-exporting that border.
- Undecided: what real Strava integration looks like end-to-end (auth flow, token storage, refresh/regeneration cadence).

## Brand Commitments

- Name: Body Improvement Club (BIC).
- Tagline: "Enhancing muscle mass and celebrating all gains of life."
- Voice: dry, deadpan-earnest - all-lowercase tab labels, casual member-log phrasing ("morning shakeout", "pull day", "legs and lungs").
- Look: red-and-sand palette, hand-drawn brush-stroke borders, grainy paper ground, monospace/display type pairing (Overpass Mono, Major Mono Display, Bungee Shade).
- The club's real external home is its Strava group: https://strava.app.link/sbkteMcGZ5b.

## Evidence on Hand

- `js/activities.js` holds placeholder, not real, member activity data - future work must not treat it as genuine club data or fabricate additional activity, member counts, or testimonials beyond it.
- No real merch/kit exists yet; the rotating tee in `shop.html` is a design preview only, not a product for sale.
- The Figma frames referenced above are the authoritative visual reference; `NOTES.md` is the transcribed rationale for nearly every layout and styling decision on top of them.

## Product Principles

- Preserve the hand-crafted, Figma-transcribed visual identity exactly - it's a deliberate, high-craft aesthetic to protect, not a placeholder to genericize or "improve" toward convention.
- The club's culture and feel come first; don't introduce funnel or conversion framing (growth CTAs, urgency, sales copy) that isn't already native to the club's own dry voice.
- Keep the site static and buildless; any new capability should fit that constraint or call out the exception explicitly.
- Treat `NOTES.md` and `tools/verify.py` as living documentation and verification for this site - significant visual or structural changes should be checked against both and update `NOTES.md` when the reasoning changes.
- Don't build the shop toward checkout or inventory; it stays a teaser until the club actually decides to sell kit.
