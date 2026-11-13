# Current-day NavIC acquisition and recency experiment

Run `20261113T221157111522Z-dfd4b5b5dc` · generated 2026-11-13T22:11:57.111522+00:00

Selected source: https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2026/317/BRDC00WRD_R_20263170000_01D_MN.rnx.gz
SHA-256: `dfd4b5b5dccd379a832426145e89a7cbf185aaf2c9e54efd3570afab3ecd9ad5`. First received: 2026-11-13T22:11:55.726119+00:00.
Server Last-Modified: Fri, 13 Nov 2026 22:10:44 GMT. HTTP status: 200.
2 of 3 present satellites usable at the acquisition check time.

| PRN | Selected toe UTC | Age minutes | Health | URA m | Assessment |
|---|---|---|---|---|---|
| I02 | 2026-11-13T21:50:06.000Z | 21.8 | 0 | 2.0 | Usable under analysis policy |
| I09 | 2026-11-13T21:50:06.000Z | 21.8 | 0 | 2.0 | Usable under analysis policy |
| I10 | 2026-11-13T19:59:42.000Z | 132.2 | 0 | 2.0 | broadcast_gap |

## Validity and freshness

The filename and HTTP modification time do not establish ephemeris freshness. Records are checked individually for health, URA, issue consistency and absolute toe age. Limit: ±7200 seconds. Basis: Conservative analysis cutoff based on ISRO SPS ICD v1.1 section 6.2.1.3 nominal 2-hour update cadence; this is NOT an ICD fit-interval guarantee.. This remains a conservative **analysis policy**, not a verified ICD fit-interval guarantee. Unusable records are gaps, never extrapolated. Directory bodies, changed raw files and retrieval events are archived with hashes. A 304 response reuses only a checksum-verified archived body. Acquisition reports are also retained immutably under data/acquisitions.

## Controlled retrospective test

Broadcast agreement only. Current file receipt occurred after the retrospective forecast origin; this is not a verified live forecast or an absolute accuracy assessment.

Forecast origin: 2026-11-13T21:10:00.000Z. Common evaluation ends: 2026-11-13T22:10:00.000Z.
The fresh and delayed cohorts use the same 6-hour training length, optimizer and sampling; the delayed cohort's inputs stop 6 hours earlier. Each model is fitted at its own issue epoch and compared over identical later physical epochs. Training excludes records with toc after its cutoff. This controls numerical time leakage, but toc is not a transmission timestamp: the current file was obtained after the retrospective origin, so actual past availability is **unproven**. This is not a live forecast. Standard GP is frozen at the origin and included only when its snapshot receipt and element epoch both precede the origin.

| PRN | Reference epochs | Fresh model holdout RMS km | Delayed model holdout RMS km | Eligible standard GP RMS km | Reduction vs delayed |
|---|---|---|---|---|---|
| I02 | 13 | 0.1291 | — | — | not comparable |
| I09 | 13 | — | — | 0.3882 | not comparable |
| I10 | 10 | 0.2213 | — | 1.0015 | not comparable |

These RMS values describe disagreement with valid broadcast trajectories, not absolute accuracy. The cohorts isolate an input-recency scenario; they do not prove universal improvement, calibrated uncertainty or future release validity. Preserve multiple dated snapshots for genuinely prospective validation. Benchmark OMMs are research artifacts and do not replace the daily accepted-model product.
