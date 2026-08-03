# Gauntlet — the Constellation (dmtatlas.com/explore.html)

## What the bar is, and what it is not

**There is no incumbent to capture.** Checked directly during the competitor
sweep: Erowid, PsychonautWiki, Effect Index and DMT-Nexus have no interactive
visualisation of this material at all — not a graph, not a map, not a timeline.
So the per-query incumbent capture the site gauntlet normally demands has no
subject here, and inventing one would be worse than admitting it.

That means **this round is scored against a written rubric on real captures of
our own artifact, before and after — not against a competitor screenshot, and
not against a northstar image I did not open.** Any number below that looked
like a head-to-head win would be fabricated. (See the `inches` gauntlet, where
scores were produced from no data at all.)

Rubric dimensions, fixed before the first change:
1. **Legibility** — can you read any given label without zooming?
2. **Hierarchy** — does the eye land on what matters, or is it uniform mush?
3. **Fidelity to the claim** — the page says the graph shows "the shape of the
   corpus" and that the most-reported figure is not the machine elves. Does the
   picture actually show that?
4. **Frame use** — does the artifact occupy its canvas?
5. **Pause value** — would a stranger stop on it for a second?

## Rounds

| # | Change | Legibility | Hierarchy | Fidelity | Frame | Pause |
|---|---|---|---|---|---|---|
| gate | *(capture invalid)* | — | — | — | — | — |
| 0 | baseline, as shipped | 1 | 2 | 2 | 3 | 2 |
| 1 | label collision rejection, importance-ordered | 4 | 3 | 2 | 1 | 2 |
| 2 | settled camera fit, subject-first labels | 4 | 4 | 3 | 2 | 3 |
| 3 | subject outranks sources (radius/alpha/glow) | 4 | 5 | 5 | 3 | 4 |
| 4 | percentile fit, mobile budget + font floor | 5 | 5 | 5 | 4 | 4 |

Scores are mine, one critic, stated as such. A three-critic panel on the final
pairing has **not** been run — on the EGM pass three critics scored one
unchanged PNG 5.50 / 6.05 / 3.60, a 2.45 spread, so a single set of numbers
here should be read as direction, not measurement.

## Round −1: the capture was invalid

First capture was the splash screen — the "Descend into the Atlas" gate, not the
graph. `svgNodes: 0` in the instrumentation was the tell, and it was ignored for
one round. Same failure the gauntlet file warns about from EGM's nickname modal.
**A screenshot of the gate is evidence about onboarding, and it is not the bar.**

## Round 0: a real defect, not an aesthetic one

With the gate dismissed, the baseline showed the article prose rendering **on
top of** the constellation. Cause: `#stage{position:fixed}` takes the canvas out
of flow, so `.atlas-text` began at document y=0 and painted over it — both at
`z-index:5`, the later DOM node winning. The copy in that overlapping text reads
"the map above". Fixed with `margin-top:100vh` and a gradient backdrop.

## Round 1: fixed the collision, lost the presence

`showLabel` included `nd.cat === "source"`, so **all ~103 sources were labelled
unconditionally** — a solid ring of colliding names. Replaced with a three-pass
render (edges → discs → labels) and rectangle-collision rejection in descending
importance.

Collision went to zero and the artifact got *worse*: 13 labels on a small dim
blob in an empty frame. Over-correction, the same shape as the demand filter
that deleted every "machine elves" thread an hour earlier.

## Round 3: the change that mattered

`n.r = (n.cat === "source" ? 7 : 5) + sqrt(deg)*2.4` gave sources **both** the
larger base radius **and** the higher degree. The orange evidence nodes were
therefore always the biggest, brightest things on screen, and the graph read as
a bibliography — directly contradicting the page's own claim about what it
shows. Inverted: subject `6.5 + sqrt(deg)*2.7`, sources `3.4 + sqrt(deg)*1.35`,
sources dimmer, glow restricted to subject hubs.

This is the round where fidelity moved 3 → 5, and it was a *content* judgement
wearing a visual-design costume.

## Round 4: frame and mobile

`fitView` fitted true min/max, so a few single-citation outliers held the whole
constellation at 45% scale. Fitting the 4th–96th percentile took it to 56% with
outliers still reachable by pan. Phone widths got a 12-label budget and an 8.5px
floor — at 390px the 34-label / 10px-floor settings buried the graph.

## Still open

- Frame use is 4, not 5: the layout is roughly square and the desktop viewport
  is 16:9, so side margins are geometric. Fixing it properly means an
  aspect-aware force layout, not more camera tuning.
- No three-critic panel, no smoothing pass.
- Motion was not touched. A slow ambient drift is the obvious next lever for
  "pause value" and cannot be judged from stills.
