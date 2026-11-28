# Current-day NavIC acquisition and recency experiment

Run `20261128T183041111510Z-6d666a7846` · generated 2026-11-28T18:30:41.111510+00:00

Selected source: https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2026/332/BRDC00WRD_S_20263320000_01D_MN.rnx.gz
SHA-256: `6d666a7846813ba918d2af540d7fc8f724e2e339b695f572669818f43c075489`. First received: 2026-11-28T18:30:34.936586+00:00.
Server Last-Modified: Sat, 28 Nov 2026 18:25:22 GMT. HTTP status: 200.
2 of 4 present satellites usable at the acquisition check time.

| PRN | Selected toe UTC | Age minutes | Health | URA m | Assessment |
|---|---|---|---|---|---|
| I02 | 2026-11-28T00:50:06.000Z | 1060.5 | 0 | 2.0 | broadcast_gap |
| I09 | 2026-11-28T17:59:42.000Z | 30.9 | 0 | 2.0 | Usable under analysis policy |
| I11 | 2026-11-28T12:20:30.000Z | 370.1 | 0 | 8192.0 | broadcast_gap, broadcast_ura_unavailable |
| I12 | 2026-11-28T18:05:18.000Z | 25.3 | 0 | 2.0 | Usable under analysis policy |

## Validity and freshness

The filename and HTTP modification time do not establish ephemeris freshness. Records are checked individually for health, URA, issue consistency and absolute toe age. Limit: ±7200 seconds. Basis: Conservative analysis cutoff based on ISRO SPS ICD v1.1 section 6.2.1.3 nominal 2-hour update cadence; this is NOT an ICD fit-interval guarantee.. This remains a conservative **analysis policy**, not a verified ICD fit-interval guarantee. Unusable records are gaps, never extrapolated. Directory bodies, changed raw files and retrieval events are archived with hashes. A 304 response reuses only a checksum-verified archived body. Acquisition reports are also retained immutably under data/acquisitions.

## Controlled retrospective test

Broadcast agreement only. Current file receipt occurred after the retrospective forecast origin; this is not a verified live forecast or an absolute accuracy assessment.

Forecast origin: 2026-11-28T17:30:00.000Z. Common evaluation ends: 2026-11-28T18:30:00.000Z.
The fresh and delayed cohorts use the same 6-hour training length, optimizer and sampling; the delayed cohort's inputs stop 6 hours earlier. Each model is fitted at its own issue epoch and compared over identical later physical epochs. Training excludes records with toc after its cutoff. This controls numerical time leakage, but toc is not a transmission timestamp: the current file was obtained after the retrospective origin, so actual past availability is **unproven**. This is not a live forecast. Standard GP is frozen at the origin and included only when its snapshot receipt and element epoch both precede the origin.

| PRN | Reference epochs | Fresh model holdout RMS km | Delayed model holdout RMS km | Eligible standard GP RMS km | Reduction vs delayed |
|---|---|---|---|---|---|
| I02 | 0 | — | — | — | not comparable |
| I09 | 13 | 0.4857 | 1.9886 | — | 75.6% |
| I11 | 0 | — | — | — | not comparable |
| I12 | 13 | — | — | — | not comparable |

These RMS values describe disagreement with valid broadcast trajectories, not absolute accuracy. The cohorts isolate an input-recency scenario; they do not prove universal improvement, calibrated uncertainty or future release validity. Preserve multiple dated snapshots for genuinely prospective validation. Benchmark OMMs are research artifacts and do not replace the daily accepted-model product.
