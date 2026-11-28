# Current-day NavIC acquisition and recency experiment

Run `20261128T015737014390Z-3f5671b0ac` · generated 2026-11-28T01:57:37.014390+00:00

Selected source: https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2026/332/BRDC00WRD_R_20263320000_01D_MN.rnx.gz
SHA-256: `3f5671b0acaa72fed13d35210c1840d4e1e0b0ad7a34747a4960045906390da2`. First received: 2026-11-28T01:57:34.560628+00:00.
Server Last-Modified: Sat, 28 Nov 2026 01:10:14 GMT. HTTP status: 200.
4 of 4 present satellites usable at the acquisition check time.

| PRN | Selected toe UTC | Age minutes | Health | URA m | Assessment |
|---|---|---|---|---|---|
| I02 | 2026-11-28T00:50:06.000Z | 67.5 | 0 | 2.0 | Usable under analysis policy |
| I09 | 2026-11-27T23:59:42.000Z | 117.9 | 0 | 2.0 | Usable under analysis policy |
| I10 | 2026-11-28T00:50:06.000Z | 67.5 | 0 | 2.0 | Usable under analysis policy |
| I12 | 2026-11-28T00:50:06.000Z | 67.5 | 0 | 2.8 | Usable under analysis policy |

## Validity and freshness

The filename and HTTP modification time do not establish ephemeris freshness. Records are checked individually for health, URA, issue consistency and absolute toe age. Limit: ±7200 seconds. Basis: Conservative analysis cutoff based on ISRO SPS ICD v1.1 section 6.2.1.3 nominal 2-hour update cadence; this is NOT an ICD fit-interval guarantee.. This remains a conservative **analysis policy**, not a verified ICD fit-interval guarantee. Unusable records are gaps, never extrapolated. Directory bodies, changed raw files and retrieval events are archived with hashes. A 304 response reuses only a checksum-verified archived body. Acquisition reports are also retained immutably under data/acquisitions.

## Controlled retrospective test

Broadcast agreement only. Current file receipt occurred after the retrospective forecast origin; this is not a verified live forecast or an absolute accuracy assessment.

Forecast origin: 2026-11-28T00:55:00.000Z. Common evaluation ends: 2026-11-28T01:55:00.000Z.
The fresh and delayed cohorts use the same 6-hour training length, optimizer and sampling; the delayed cohort's inputs stop 6 hours earlier. Each model is fitted at its own issue epoch and compared over identical later physical epochs. Training excludes records with toc after its cutoff. This controls numerical time leakage, but toc is not a transmission timestamp: the current file was obtained after the retrospective origin, so actual past availability is **unproven**. This is not a live forecast. Standard GP is frozen at the origin and included only when its snapshot receipt and element epoch both precede the origin.

| PRN | Reference epochs | Fresh model holdout RMS km | Delayed model holdout RMS km | Eligible standard GP RMS km | Reduction vs delayed |
|---|---|---|---|---|---|
| I02 | 13 | 0.4019 | 4.9288 | 1.1429 | 91.8% |
| I09 | 13 | 0.2274 | 5.0853 | 0.7465 | 95.5% |
| I10 | 13 | — | 4.3712 | 2.5197 | not comparable |
| I12 | 13 | — | — | — | not comparable |

These RMS values describe disagreement with valid broadcast trajectories, not absolute accuracy. The cohorts isolate an input-recency scenario; they do not prove universal improvement, calibrated uncertainty or future release validity. Preserve multiple dated snapshots for genuinely prospective validation. Benchmark OMMs are research artifacts and do not replace the daily accepted-model product.
