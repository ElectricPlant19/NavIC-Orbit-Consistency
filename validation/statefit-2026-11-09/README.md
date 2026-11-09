# Latest-message state fitter: development and chronological replay

This study motivates an **experimental V2 challenger**, not a replacement declared superior in advance. Its scores here are retrospective replay results. They are never inserted into the live prospective history.

## What changed

V1 fits six hours of broadcast-derived positions, using a succession of navigation messages. V2 selects one healthy message at the fitting cutoff, with toc no later than that cutoff, from inputs already received then. It fits the position and motion implied by that message over cutoff ±1 hour at 60-second spacing. Forward targets are predictions from this already-known message, **not later messages or observations**. All targets, including the ±0.5-second velocity differentiation stencil, must remain inside the ±7200-second toe analysis cutoff. At least 80% of the requested arc and 12 targets are required. This cutoff is not an independently verified ICD fit-interval guarantee.

The least-squares residual concatenates TEME position differences in km and trajectory-velocity differences in km/s multiplied by 10,000 seconds. This number balances position and motion in the objective; it is not a prediction horizon, a physical uncertainty, or a calibrated statistical weight. Both models use one-second central differences of propagated positions for the SGP4 trajectory velocity, rather than assuming its reported velocity equals the derivative of its positions. Broadcast target velocity includes the rotating-frame transformation. The six nonsingular parameters, WGS72 deep-space SGP4, fixed zero Bstar and derivatives, bounded optimizer, and OMM round-trip checks remain in place.

The rationale is to reduce release-state bias and avoid blending different uploads. It does not prove that message blending caused every observed drift, or remove SGP4's dynamical/model limitations.

## Results: identical future reference epochs within each row

All entries are 3D RMS disagreement with later valid broadcast trajectories, in kilometres. V1 is the actual archived exported OMM; V2 is refitted using only receipt-eligible historical inputs and then exported/re-imported before scoring. The GP column uses the CelesTrak element set frozen at the original issue.

| Period | Satellite | Samples | V1 RMS | V2 RMS | Frozen GP RMS |
|---|---|---:|---:|---:|---:|
| Development: Nov 8, 20:35 UTC issue, next 6 h | I02 | 70 | 0.919 | 1.255 | 7.454 |
| Development | I09 | 56 | 1.554 | 0.406 | 0.834 |
| Development | I10 | 56 | 4.721 | 1.459 | 1.113 |
| Later check: Nov 9, 02:59 UTC issue, next 4 h | I02 | 47 | 2.599 | 0.501 | 5.094 |
| Later check | I09 | 36 | 1.709 | 0.388 | 2.321 |
| Later check | I10 | 36 | 0.763 | 0.216 | 1.226 |

V2 reduced the later-check RMS by about 81%, 77% and 72% relative to V1. **It worsened I02 by 37% in the development period**, and its I10 development RMS exceeded frozen GP. No claim of universal improvement is supported.

## Selection and limitations

The initial sweep explored 20 position/weak-motion/longer-arc configurations. It produced no material common improvement. A second sweep explored 21 short-arc and coherent-message configurations. Its selected candidate minimizes the worst V2/V1 RMS ratio across the three satellites in the development period, with mean ratio as tie-breaker. That worst ratio was still above one. Full candidate results are retained in `sweep.json` and `state-sweep.json`; do not present only the favourable rows.

The selected settings were then checked on a later chronological interval whose evaluation epochs start after the development interval ends. The later period had already been inspected during the initial sweep, so this is **not a pristine blind test**. These are two short windows on only three satellites. Navigation-message biases are shared with the fitted targets. The many parameter trials increase selection risk; samples and satellite errors are correlated. There are no calibrated uncertainty bounds or operator-orbit accuracy claims. Longer prediction ages, more orbital phases, maneuvers and repeated days remain untested.

For that reason, new V1 control and V2 experimental issues are frozen side by side in production, with version-separated dashboard summaries. Old issue documents and immutable scores remain unchanged. Prospective evidence must accumulate after the real V2 release; fitting settings must not be retuned from those future scores without assigning another version.

## Reproduction

From the repository root, with the locked dependencies installed:

```powershell
python validation/replay_statefit.py
python -m pytest -q --basetemp=.test-tmp/statefit-check
node --test tests/test_dashboard_loader.cjs tests/test_prospective_dashboard.cjs
```

The replay makes no network requests and never writes production history. `replay-inputs.json.gz` pins the canonical parsed records, earliest receipts, six original issue documents, as-of time, orientation identifiers and configuration. Record payload hashes are checked. Original orientation bytes are restored from the immutable `history/prospective/orientation` archive and hash-checked. `replay-results.json` includes exact epoch residuals, reference record IDs, optimizer diagnostics and serialized V2 OMMs. `checksums.json` pins the study artifacts. The fresh RINEX parse was performed before packaging; this replay begins at the canonical parsed-record stage, not the raw-file parser. Solver results can differ slightly across software versions/platforms.

Method background: [Vallado and Crawford, SGP4 Orbit Determination](https://celestrak.org/publications/AIAA/2008-6770/), [SciPy bounded least squares](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html).
