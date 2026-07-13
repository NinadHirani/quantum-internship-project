# Doc Cleanup Spec — Fix Stale "p=1" References in report.md

## Problem
`docs/report.md` describes the QAOA config as **p=1** in several places, but the actual pipeline (`run_all.py` default, `qaoa_solver.py`, and the regenerated `results/benchmark_table.csv`) uses **p=2**. This is leftover text from before the p=2 config was set — a smaller version of the same "docs describe a different run than the code produces" issue from the last fix pass.

## Fix
Open `docs/report.md` and correct every reference below from p=1 to p=2. Read the surrounding sentence each time — a couple of these aren't a clean find-replace, they're written as explanatory prose about *why* p=1 was chosen, so the reasoning has to be reworded to justify p=2 instead, not just the digit swapped.

- **Line 158** — "QAOA with p=1 produces solutions that may or may not satisfy..." → change to p=2.
- **Line 169** — "The shallow circuit depth (p=1 limits the algorithm's approximation power)" → update to reflect p=2's actual circuit depth/approximation power, not just swap the number.
- **Line 194** — item under limitations describing default config as p=1 → change to p=2.
- **Line 198** — "We use p=1 QAOA layer. More layers (p ≥ 3) would improve..." → change to "We use p=2 QAOA layers. More layers (p ≥ 3) would improve..." (note: also fix "layer" → "layers" for grammar).

## Also check while in there
- Search the whole file for any other bare `p=1` or "1 layer" mentions the grep above may have missed (do a manual read of the QAOA sections, not just a search — some references may be phrased without literally saying "p=1", e.g. "single-layer QAOA").
- Confirm `docs/math_derivation.md` and any slide/deck files don't repeat the same p=1 claim.

## Acceptance check
```bash
grep -n "p=1\|p = 1\|single.layer" docs/report.md docs/math_derivation.md
```
Returns nothing that contradicts the actual p=2 default — or only intentional generic explanations of what p=1 *would* mean in QAOA theory (fine to keep those if clearly framed as general background, not as "this is what we did").
