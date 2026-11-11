# Current-day NavIC acquisition and recency experiment

Run `20261111T153815270665Z-df992b30ee` · generated 2026-11-11T15:38:15.270665+00:00

Selected source: https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2026/315/BRDC00WRD_S_20263150000_01D_MN.rnx.gz
SHA-256: `df992b30ee27528b99f0cbae63d69fadb86e7a715f7dd547cb8b8dfe211e9d6b`. First received: 2026-11-11T15:38:12.399417+00:00.
Server Last-Modified: Wed, 11 Nov 2026 15:25:01 GMT. HTTP status: 200.
3 of 5 present satellites usable at the acquisition check time.

| PRN | Selected toe UTC | Age minutes | Health | URA m | Assessment |
|---|---|---|---|---|---|
| I02 | 2026-11-11T15:05:18.000Z | 32.9 | 0 | 2.0 | Usable under analysis policy |
| I03 | 2026-11-12T01:05:02.000Z | -566.8 | 1 | 11.3 | broadcast_gap, broadcast_unhealthy |
| I09 | 2026-11-11T15:05:18.000Z | 32.9 | 0 | 2.0 | Usable under analysis policy |
| I10 | 2026-11-11T13:59:42.000Z | 98.5 | 0 | 2.0 | Usable under analysis policy |
| I11 | 2026-11-12T01:05:02.000Z | -566.8 | 1 | 11.3 | broadcast_gap, broadcast_unhealthy |

## Validity and freshness

The filename and HTTP modification time do not establish ephemeris freshness. Records are checked individually for health, URA, issue consistency and absolute toe age. Limit: ±7200 seconds. Basis: Conservative analysis cutoff based on ISRO SPS ICD v1.1 section 6.2.1.3 nominal 2-hour update cadence; this is NOT an ICD fit-interval guarantee.. This remains a conservative **analysis policy**, not a verified ICD fit-interval guarantee. Unusable records are gaps, never extrapolated. Directory bodies, changed raw files and retrieval events are archived with hashes. A 304 response reuses only a checksum-verified archived body. Acquisition reports are also retained immutably under data/acquisitions.

## Controlled retrospective test

Broadcast agreement only. Current file receipt occurred after the retrospective forecast origin; this is not a verified live forecast or an absolute accuracy assessment.

Forecast origin: 2026-11-11T14:35:00.000Z. Common evaluation ends: 2026-11-11T15:35:00.000Z.
The fresh and delayed cohorts use the same 6-hour training length, optimizer and sampling; the delayed cohort's inputs stop 6 hours earlier. Each model is fitted at its own issue epoch and compared over identical later physical epochs. Training excludes records with toc after its cutoff. This controls numerical time leakage, but toc is not a transmission timestamp: the current file was obtained after the retrospective origin, so actual past availability is **unproven**. This is not a live forecast. Standard GP is frozen at the origin and included only when its snapshot receipt and element epoch both precede the origin.

| PRN | Reference epochs | Fresh model holdout RMS km | Delayed model holdout RMS km | Eligible standard GP RMS km | Reduction vs delayed |
|---|---|---|---|---|---|
| I02 | 13 | 0.5957 | 1.1204 | — | 46.8% |
| I03 | 0 | — | — | — | not comparable |
| I09 | 13 | 0.4158 | 1.9405 | 0.9700 | 78.6% |
| I10 | 13 | 0.4637 | 8.1358 | 1.4437 | 94.3% |
| I11 | 0 | — | — | — | not comparable |

These RMS values describe disagreement with valid broadcast trajectories, not absolute accuracy. The cohorts isolate an input-recency scenario; they do not prove universal improvement, calibrated uncertainty or future release validity. Preserve multiple dated snapshots for genuinely prospective validation. Benchmark OMMs are research artifacts and do not replace the daily accepted-model product.
