# Prospective NavIC SGP4 validation

Updated 2026-11-08T22:36:00.200411Z. 6 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional.

Models issue every 30 minutes where fitting coverage and numerical checks permit. Each uses six hours of already received broadcast targets. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|
| I10 | 2026-11-08T22:36:00.143061Z | Waiting | 0 | — | 0 | 0 |
| I09 | 2026-11-08T22:36:00.026138Z | Waiting | 0 | — | 0 | 0 |
| I02 | 2026-11-08T22:35:59.850666Z | Waiting | 0 | — | 0 | 0 |
| I10 | 2026-11-08T20:35:50.210Z | Tracking | 8 | 1.4880 | 8 | 8 |
| I09 | 2026-11-08T20:35:49.991Z | Tracking | 8 | 0.5694 | 8 | 8 |
| I02 | 2026-11-08T20:35:49.678Z | Tracking | 22 | 0.1995 | 22 | 22 |

The Git-tracked history/prospective directory stores original RINEX/GP bytes, first receipts, parsed messages, frozen model documents, compressed pinned EOP/leap versions and immutable scoring chunks. GitHub caches are not the authoritative model archive. No automatic deletion is configured. Git repository size will grow; plan external archival storage as the history expands. The cumulative statistics CSV contains matched-epoch summaries; selected-model epoch CSVs and series JSON retain gaps and cohort identifiers. Blanks are gaps, not zero error.
