# Driving the beings with a real fly connectome

A depicted being in `/world/` moves because a sine wave tells it to. This module replaces that
sine wave with a slice of an actual brain.

```
distance  ->  looming drive  ->  FlyWire slice (leaky integrate-and-fire)  ->  descending rate  ->  cited action
```

**The fly decides when and how hard. The atlas decides what.** Every action a being performs is
a verbatim phrase from that entity's own record in `data/atlas.json`, carrying its citation.
The simulation supplies one number — how hard the descending population is driving — and that
number selects which cited phrase is currently true. Nothing here writes a behaviour.

## What this is not

This is **not** a claim that DMT entities are insects, that a fly brain explains anything about
them, or that any of this is evidence about what people encounter. It is a way of making a
depicted figure move from measured biology instead of from a hand-tuned oscillator. Anywhere
this drives something a visitor can see, the page has to say so plainly.

It is also **not** a named circuit. The export carries no canonical cell-type labels — no LC4,
no LPLC2, no DNp01 — so nothing here may be described as "the looming escape pathway" or any
other named result. It is a pathway at the level of FlyWire's own `super_class` annotation,
and that is how it is described throughout.

## The slice

Taken by FlyWire's own classification, not by hand:

| layer | what it is | neurons |
|---|---|---|
| `visual_projection` | optic lobe output entering the central brain | 7,452 |
| central bridge | central neurons that BOTH receive from visual projection AND project to descending | 4,416 |
| `descending` | commands leaving the brain for the nerve cord | 1,236 |

13,104 neurons and 295,075 connections at a 5-synapse threshold, 1.7 MB gzipped. Sign comes
from the measured transmitter: acetylcholine excitatory, GABA and glutamate inhibitory, which
is the usual Drosophila case because glutamate gates a chloride channel there.

Propagation is event-driven — only neurons that actually spiked push charge — so cost tracks
activity rather than the size of the wiring diagram. That is what makes this affordable next
to a WebGL scene.

## It is tested, and the tests can fail

`node selftest.js` checks three things, because a simulation that cannot fail is a screensaver:

1. **Descending output tracks visual drive.** Monotonic, silent below threshold, rising to
   ~0.077.
2. **The real wiring matters.** Against a degree- and weight-preserving shuffle of the same
   connections, the real connectome is markedly more *selective* — shuffling more than doubles
   descending activation. Structure gates output; random wiring of identical statistics floods
   it.
3. **It runs in budget.** ~0.2 ms/step, roughly 80 steps inside a 60 fps frame.

`node approach.js <being>` walks a traveller in from 14 units and prints which cited action is
active at each distance.

## Calibration is measured, not assumed

The first ladder spread rungs evenly in descending-rate. That looked reasonable and was wrong:
rate against distance is steeply nonlinear, so most of the walk collapsed into the top rung and
two of the elf's five cited actions were unreachable at any distance. `calibrate.js` sweeps the
real slice across the real approach and sets each threshold at the rate the circuit actually
produces at that point in the walk.

## Files

| file | role |
|---|---|
| `sim.js` | the LIF simulation; runs in a worker or in node |
| `data/circuit.bin.gz` | the packed slice, 1.7 MB |
| `build_behaviour.py` | cited actions -> ladder, from `data/atlas.json` |
| `calibrate.js` | sets thresholds from a measured sweep |
| `selftest.js` | proves the slice responds, the wiring matters, it fits the budget |
| `approach.js` | the full chain, end to end |
| `behaviour.json` / `.js` | the generated ladders |

## Attribution — required

Connectome data is **FlyWire FAFB v783**, released under **CC BY-NC 4.0**: non-commercial use
with attribution. dmtatlas.com carries no advertising, affiliate links or payments, which is
what makes this use permissible. **If the site is ever monetised, this data has to come out.**

Cite:

- Dorkenwald, S. et al. *Neuronal wiring diagram of an adult brain.* Nature (2024).
- Schlegel, P. et al. *Whole-brain annotation and multi-connectome cell typing of Drosophila.*
  Nature (2024).
- FlyWire Codex — https://codex.flywire.ai/

The tabular export used here was obtained via the MIT-licensed
[snedea/flybrain](https://github.com/snedea/flybrain) mirror of the FlyWire CSVs; the slice,
packing, simulation and calibration in this directory are our own.
