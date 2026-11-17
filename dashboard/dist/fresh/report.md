# Current-day NavIC acquisition and recency experiment

Run `20261117T020651327856Z-86d99ae8a9` · generated 2026-11-17T02:06:51.327856+00:00

Selected source: https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2026/321/BRDC00WRD_S_20263210000_01D_MN.rnx.gz
SHA-256: `86d99ae8a9a696912b2253ff23c7f055d12503f4c21e941198e576fb76f75366`. First received: 2026-11-17T02:06:46.289928+00:00.
Server Last-Modified: Tue, 17 Nov 2026 01:55:20 GMT. HTTP status: 200.
2 of 3 present satellites usable at the acquisition check time.

| PRN | Selected toe UTC | Age minutes | Health | URA m | Assessment |
|---|---|---|---|---|---|
| I02 | 2026-11-17T01:35:42.000Z | 31.1 | 0 | 2.0 | Usable under analysis policy |
| I09 | 2026-11-17T01:35:42.000Z | 31.1 | 0 | 2.0 | Usable under analysis policy |
| I10 | 2026-11-16T23:59:42.000Z | 127.1 | 0 | 2.0 | broadcast_gap |

## Validity and freshness

The filename and HTTP modification time do not establish ephemeris freshness. Records are checked individually for health, URA, issue consistency and absolute toe age. Limit: ±7200 seconds. Basis: Conservative analysis cutoff based on ISRO SPS ICD v1.1 section 6.2.1.3 nominal 2-hour update cadence; this is NOT an ICD fit-interval guarantee.. This remains a conservative **analysis policy**, not a verified ICD fit-interval guarantee. Unusable records are gaps, never extrapolated. Directory bodies, changed raw files and retrieval events are archived with hashes. A 304 response reuses only a checksum-verified archived body. Acquisition reports are also retained immutably under data/acquisitions.

## Controlled retrospective test

Broadcast agreement only. Current file receipt occurred after the retrospective forecast origin; this is not a verified live forecast or an absolute accuracy assessment.

Forecast origin: 2026-11-17T01:05:00.000Z. Common evaluation ends: 2026-11-17T02:05:00.000Z.
The fresh and delayed cohorts use the same 6-hour training length, optimizer and sampling; the delayed cohort's inputs stop 6 hours earlier. Each model is fitted at its own issue epoch and compared over identical later physical epochs. Training excludes records with toc after its cutoff. This controls numerical time leakage, but toc is not a transmission timestamp: the current file was obtained after the retrospective origin, so actual past availability is **unproven**. This is not a live forecast. Standard GP is frozen at the origin and included only when its snapshot receipt and element epoch both precede the origin.

| PRN | Reference epochs | Fresh model holdout RMS km | Delayed model holdout RMS km | Eligible standard GP RMS km | Reduction vs delayed |
|---|---|---|---|---|---|
| I02 | 13 | — | 0.5139 | — | not comparable |
| I09 | 13 | — | 6.6658 | 0.3147 | not comparable |
| I10 | 11 | — | 3.4773 | 1.7271 | not comparable |

These RMS values describe disagreement with valid broadcast trajectories, not absolute accuracy. The cohorts isolate an input-recency scenario; they do not prove universal improvement, calibrated uncertainty or future release validity. Preserve multiple dated snapshots for genuinely prospective validation. Benchmark OMMs are research artifacts and do not replace the daily accepted-model product.
