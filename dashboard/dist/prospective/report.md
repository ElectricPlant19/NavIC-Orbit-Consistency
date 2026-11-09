# Prospective NavIC SGP4 validation

Updated 2026-11-09T02:59:21.826438Z. 12 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional.

Models issue every 30 minutes where fitting coverage and numerical checks permit. Each uses six hours of already received broadcast targets. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|
| I10 | 2026-11-09T02:59:21.767924Z | Waiting | 0 | — | 0 | 0 |
| I09 | 2026-11-09T02:59:21.651496Z | Waiting | 0 | — | 0 | 0 |
| I02 | 2026-11-09T02:59:21.475281Z | Waiting | 0 | — | 0 | 0 |
| I10 | 2026-11-08T23:12:00.859398Z | Tracking | 36 | 2.0175 | 36 | 36 |
| I09 | 2026-11-08T23:12:00.753567Z | Tracking | 36 | 0.5554 | 36 | 36 |
| I02 | 2026-11-08T23:12:00.588965Z | Tracking | 44 | 1.7276 | 44 | 44 |
| I10 | 2026-11-08T22:36:00.143061Z | Tracking | 36 | 2.7337 | 36 | 36 |
| I09 | 2026-11-08T22:36:00.026138Z | Tracking | 36 | 0.6615 | 36 | 36 |
| I02 | 2026-11-08T22:35:59.850666Z | Tracking | 50 | 1.7688 | 50 | 50 |
| I10 | 2026-11-08T20:35:50.210Z | Review | 60 | 5.0704 | 60 | 60 |
| I09 | 2026-11-08T20:35:49.991Z | Tracking | 60 | 1.6576 | 60 | 60 |
| I02 | 2026-11-08T20:35:49.678Z | Tracking | 74 | 1.0915 | 74 | 74 |

The Git-tracked history/prospective directory stores original RINEX/GP bytes, first receipts, parsed messages, frozen model documents, compressed pinned EOP/leap versions and immutable scoring chunks. GitHub caches are not the authoritative model archive. No automatic deletion is configured. Git repository size will grow; plan external archival storage as the history expands. The cumulative statistics CSV contains matched-epoch summaries; selected-model epoch CSVs and series JSON retain gaps and cohort identifiers. Blanks are gaps, not zero error.
