# Current-day NavIC acquisition and recency experiment

Run `20261115T210218207790Z-0a4aca7791` · generated 2026-11-15T21:02:18.207790+00:00

Selected source: https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2026/319/BRDC00WRD_S_20263190000_01D_MN.rnx.gz
SHA-256: `0a4aca77912ddab51668edbb90775cf89a6bf3abcee8a67167c00bc83ce2850f`. First received: 2026-11-15T21:02:15.220390+00:00.
Server Last-Modified: Sun, 15 Nov 2026 20:55:14 GMT. HTTP status: 200.
3 of 4 present satellites usable at the acquisition check time.

| PRN | Selected toe UTC | Age minutes | Health | URA m | Assessment |
|---|---|---|---|---|---|
| I02 | 2026-11-15T20:35:42.000Z | 26.6 | 0 | 2.0 | Usable under analysis policy |
| I09 | 2026-11-15T20:35:42.000Z | 26.6 | 0 | 2.0 | Usable under analysis policy |
| I10 | 2026-11-15T19:59:42.000Z | 62.6 | 0 | 2.0 | Usable under analysis policy |
| I11 | 2026-11-15T14:35:42.000Z | 386.6 | 0 | 8192.0 | broadcast_gap, broadcast_ura_unavailable |

## Validity and freshness

The filename and HTTP modification time do not establish ephemeris freshness. Records are checked individually for health, URA, issue consistency and absolute toe age. Limit: ±7200 seconds. Basis: Conservative analysis cutoff based on ISRO SPS ICD v1.1 section 6.2.1.3 nominal 2-hour update cadence; this is NOT an ICD fit-interval guarantee.. This remains a conservative **analysis policy**, not a verified ICD fit-interval guarantee. Unusable records are gaps, never extrapolated. Directory bodies, changed raw files and retrieval events are archived with hashes. A 304 response reuses only a checksum-verified archived body. Acquisition reports are also retained immutably under data/acquisitions.

## Controlled retrospective test

Broadcast agreement only. Current file receipt occurred after the retrospective forecast origin; this is not a verified live forecast or an absolute accuracy assessment.

Forecast origin: 2026-11-15T20:00:00.000Z. Common evaluation ends: 2026-11-15T21:00:00.000Z.
The fresh and delayed cohorts use the same 6-hour training length, optimizer and sampling; the delayed cohort's inputs stop 6 hours earlier. Each model is fitted at its own issue epoch and compared over identical later physical epochs. Training excludes records with toc after its cutoff. This controls numerical time leakage, but toc is not a transmission timestamp: the current file was obtained after the retrospective origin, so actual past availability is **unproven**. This is not a live forecast. Standard GP is frozen at the origin and included only when its snapshot receipt and element epoch both precede the origin.

| PRN | Reference epochs | Fresh model holdout RMS km | Delayed model holdout RMS km | Eligible standard GP RMS km | Reduction vs delayed |
|---|---|---|---|---|---|
| I02 | 13 | 0.1130 | 1.7338 | — | 93.5% |
| I09 | 13 | 0.6226 | 3.5640 | 0.8978 | 82.5% |
| I10 | 13 | 0.2502 | 4.7567 | 1.2139 | 94.7% |
| I11 | 0 | — | — | — | not comparable |

These RMS values describe disagreement with valid broadcast trajectories, not absolute accuracy. The cohorts isolate an input-recency scenario; they do not prove universal improvement, calibrated uncertainty or future release validity. Preserve multiple dated snapshots for genuinely prospective validation. Benchmark OMMs are research artifacts and do not replace the daily accepted-model product.
