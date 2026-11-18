# Current-day NavIC acquisition and recency experiment

Run `20261118T104449153678Z-0625bdf987` · generated 2026-11-18T10:44:49.153678+00:00

Selected source: https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2026/322/BRDC00WRD_S_20263220000_01D_MN.rnx.gz
SHA-256: `0625bdf9872550fec1e1cf3ebd4e5b6a5add7764cbc9dacd820068c9027105ad`. First received: 2026-11-18T10:44:46.363762+00:00.
Server Last-Modified: Wed, 18 Nov 2026 10:40:15 GMT. HTTP status: 200.
4 of 7 present satellites usable at the acquisition check time.

| PRN | Selected toe UTC | Age minutes | Health | URA m | Assessment |
|---|---|---|---|---|---|
| I02 | 2026-11-18T10:20:30.000Z | 24.3 | 0 | 2.0 | Usable under analysis policy |
| I04 | 2026-11-18T09:50:06.000Z | 54.7 | 0 | 8192.0 | broadcast_ura_unavailable |
| I08 | 2026-11-18T09:50:06.000Z | 54.7 | 0 | 8192.0 | broadcast_ura_unavailable |
| I09 | 2026-11-18T09:59:42.000Z | 45.1 | 0 | 2.0 | Usable under analysis policy |
| I10 | 2026-11-18T09:59:42.000Z | 45.1 | 0 | 2.0 | Usable under analysis policy |
| I11 | 2026-11-18T10:20:30.000Z | 24.3 | 0 | 8192.0 | broadcast_ura_unavailable |
| I12 | 2026-11-18T10:20:30.000Z | 24.3 | 0 | 5.7 | Usable under analysis policy |

## Validity and freshness

The filename and HTTP modification time do not establish ephemeris freshness. Records are checked individually for health, URA, issue consistency and absolute toe age. Limit: ±7200 seconds. Basis: Conservative analysis cutoff based on ISRO SPS ICD v1.1 section 6.2.1.3 nominal 2-hour update cadence; this is NOT an ICD fit-interval guarantee.. This remains a conservative **analysis policy**, not a verified ICD fit-interval guarantee. Unusable records are gaps, never extrapolated. Directory bodies, changed raw files and retrieval events are archived with hashes. A 304 response reuses only a checksum-verified archived body. Acquisition reports are also retained immutably under data/acquisitions.

## Controlled retrospective test

Broadcast agreement only. Current file receipt occurred after the retrospective forecast origin; this is not a verified live forecast or an absolute accuracy assessment.

Forecast origin: 2026-11-18T09:40:00.000Z. Common evaluation ends: 2026-11-18T10:40:00.000Z.
The fresh and delayed cohorts use the same 6-hour training length, optimizer and sampling; the delayed cohort's inputs stop 6 hours earlier. Each model is fitted at its own issue epoch and compared over identical later physical epochs. Training excludes records with toc after its cutoff. This controls numerical time leakage, but toc is not a transmission timestamp: the current file was obtained after the retrospective origin, so actual past availability is **unproven**. This is not a live forecast. Standard GP is frozen at the origin and included only when its snapshot receipt and element epoch both precede the origin.

| PRN | Reference epochs | Fresh model holdout RMS km | Delayed model holdout RMS km | Eligible standard GP RMS km | Reduction vs delayed |
|---|---|---|---|---|---|
| I02 | 13 | 0.2003 | 0.4638 | — | 56.8% |
| I04 | 0 | — | — | — | not comparable |
| I08 | 0 | — | — | — | not comparable |
| I09 | 13 | 0.3873 | 2.5236 | 1.3617 | 84.7% |
| I10 | 13 | 0.4641 | 6.8769 | 1.0825 | 93.3% |
| I11 | 0 | — | — | — | not comparable |
| I12 | 9 | — | — | — | not comparable |

These RMS values describe disagreement with valid broadcast trajectories, not absolute accuracy. The cohorts isolate an input-recency scenario; they do not prove universal improvement, calibrated uncertainty or future release validity. Preserve multiple dated snapshots for genuinely prospective validation. Benchmark OMMs are research artifacts and do not replace the daily accepted-model product.
