# Current-day NavIC acquisition and recency experiment

Run `20261118T192500277882Z-cf8cd83c47` · generated 2026-11-18T19:25:00.277882+00:00

Selected source: https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2026/322/BRDC00WRD_R_20263220000_01D_MN.rnx.gz
SHA-256: `cf8cd83c47a10e4df7dec4a8029515a3f068ac871fc6c15a1d44ed7f41cc9688`. First received: 2026-11-18T19:24:57.983580+00:00.
Server Last-Modified: Wed, 18 Nov 2026 19:10:34 GMT. HTTP status: 200.
4 of 4 present satellites usable at the acquisition check time.

| PRN | Selected toe UTC | Age minutes | Health | URA m | Assessment |
|---|---|---|---|---|---|
| I02 | 2026-11-18T18:50:06.000Z | 34.9 | 0 | 2.0 | Usable under analysis policy |
| I09 | 2026-11-18T17:59:42.000Z | 85.3 | 0 | 2.0 | Usable under analysis policy |
| I10 | 2026-11-18T17:59:42.000Z | 85.3 | 0 | 2.0 | Usable under analysis policy |
| I12 | 2026-11-18T18:50:06.000Z | 34.9 | 0 | 2.0 | Usable under analysis policy |

## Validity and freshness

The filename and HTTP modification time do not establish ephemeris freshness. Records are checked individually for health, URA, issue consistency and absolute toe age. Limit: ±7200 seconds. Basis: Conservative analysis cutoff based on ISRO SPS ICD v1.1 section 6.2.1.3 nominal 2-hour update cadence; this is NOT an ICD fit-interval guarantee.. This remains a conservative **analysis policy**, not a verified ICD fit-interval guarantee. Unusable records are gaps, never extrapolated. Directory bodies, changed raw files and retrieval events are archived with hashes. A 304 response reuses only a checksum-verified archived body. Acquisition reports are also retained immutably under data/acquisitions.

## Controlled retrospective test

Broadcast agreement only. Current file receipt occurred after the retrospective forecast origin; this is not a verified live forecast or an absolute accuracy assessment.

Forecast origin: 2026-11-18T18:25:00.000Z. Common evaluation ends: 2026-11-18T19:25:00.000Z.
The fresh and delayed cohorts use the same 6-hour training length, optimizer and sampling; the delayed cohort's inputs stop 6 hours earlier. Each model is fitted at its own issue epoch and compared over identical later physical epochs. Training excludes records with toc after its cutoff. This controls numerical time leakage, but toc is not a transmission timestamp: the current file was obtained after the retrospective origin, so actual past availability is **unproven**. This is not a live forecast. Standard GP is frozen at the origin and included only when its snapshot receipt and element epoch both precede the origin.

| PRN | Reference epochs | Fresh model holdout RMS km | Delayed model holdout RMS km | Eligible standard GP RMS km | Reduction vs delayed |
|---|---|---|---|---|---|
| I02 | 13 | 0.0334 | — | — | not comparable |
| I09 | 13 | 0.1459 | — | 2.3533 | not comparable |
| I10 | 13 | 0.5837 | — | 1.1360 | not comparable |
| I12 | 13 | — | — | — | not comparable |

These RMS values describe disagreement with valid broadcast trajectories, not absolute accuracy. The cohorts isolate an input-recency scenario; they do not prove universal improvement, calibrated uncertainty or future release validity. Preserve multiple dated snapshots for genuinely prospective validation. Benchmark OMMs are research artifacts and do not replace the daily accepted-model product.
