# Prospective NavIC SGP4 validation

Updated 2026-11-09T07:30:03.142474Z. 16 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional. V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.

Models issue every 30 minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
| I10 | v1-position-6h | 2026-11-09T07:30:03.077172Z | Waiting | 0 | — | 0 | 0 |
| I09 | v1-position-6h | 2026-11-09T07:30:02.965468Z | Waiting | 0 | — | 0 | 0 |
| I02 | v1-position-6h | 2026-11-09T07:30:02.661693Z | Waiting | 0 | — | 0 | 0 |
| I02 | v2-message-state | 2026-11-09T07:30:02.892434Z | Waiting | 0 | — | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T02:59:21.767924Z | Tracking | 42 | 0.8198 | 42 | 42 |
| I09 | v1-position-6h | 2026-11-09T02:59:21.651496Z | Tracking | 42 | 1.9734 | 42 | 42 |
| I02 | v1-position-6h | 2026-11-09T02:59:21.475281Z | Tracking | 53 | 2.9378 | 53 | 53 |
| I10 | v1-position-6h | 2026-11-08T23:12:00.859398Z | Tracking | 90 | 3.1187 | 90 | 90 |
| I09 | v1-position-6h | 2026-11-08T23:12:00.753567Z | Tracking | 90 | 2.4098 | 90 | 90 |
| I02 | v1-position-6h | 2026-11-08T23:12:00.588965Z | Tracking | 98 | 7.1829 | 98 | 98 |
| I10 | v1-position-6h | 2026-11-08T22:36:00.143061Z | Tracking | 90 | 4.2964 | 90 | 90 |
| I09 | v1-position-6h | 2026-11-08T22:36:00.026138Z | Tracking | 90 | 2.0886 | 90 | 90 |
| I02 | v1-position-6h | 2026-11-08T22:35:59.850666Z | Tracking | 104 | 7.3278 | 104 | 104 |
| I10 | v1-position-6h | 2026-11-08T20:35:50.210Z | Review | 114 | 9.2698 | 114 | 114 |
| I09 | v1-position-6h | 2026-11-08T20:35:49.991Z | Tracking | 114 | 2.4795 | 114 | 114 |
| I02 | v1-position-6h | 2026-11-08T20:35:49.678Z | Tracking | 128 | 5.4913 | 128 | 128 |

The Git-tracked history/prospective directory stores original RINEX/GP bytes, first receipts, parsed messages, frozen model documents, compressed pinned EOP/leap versions and immutable scoring chunks. GitHub caches are not the authoritative model archive. No automatic deletion is configured. Git repository size will grow; plan external archival storage as the history expands. The cumulative statistics CSV contains matched-epoch summaries; selected-model epoch CSVs and series JSON retain gaps and cohort identifiers. Blanks are gaps, not zero error.
