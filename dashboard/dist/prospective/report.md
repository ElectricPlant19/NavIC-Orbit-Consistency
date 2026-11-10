# Prospective NavIC SGP4 validation

Updated 2026-11-10T03:50:44.520599Z. 30 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional. V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.

Models issue every 30 minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
| I10 | v1-position-6h | 2026-11-10T03:50:44.444496Z | Waiting | 0 | — | 0 | 0 |
| I09 | v2-message-state | 2026-11-10T03:50:44.368827Z | Waiting | 0 | — | 0 | 0 |
| I09 | v1-position-6h | 2026-11-10T03:50:44.132839Z | Waiting | 0 | — | 0 | 0 |
| I02 | v1-position-6h | 2026-11-10T03:50:43.671047Z | Waiting | 0 | — | 0 | 0 |
| I02 | v2-message-state | 2026-11-10T03:50:43.890411Z | Waiting | 0 | — | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T21:38:52.645306Z | Tracking | 70 | 4.0638 | 70 | 70 |
| I09 | v1-position-6h | 2026-11-09T21:38:52.360083Z | Tracking | 57 | 1.1061 | 57 | 57 |
| I09 | v2-message-state | 2026-11-09T21:38:52.496939Z | Tracking | 57 | 0.5617 | 57 | 57 |
| I02 | v1-position-6h | 2026-11-09T21:38:51.906714Z | Tracking | 57 | 1.8862 | 0 | 0 |
| I02 | v2-message-state | 2026-11-09T21:38:52.123974Z | Tracking | 57 | 1.6325 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T11:27:48.642898Z | Tracking | 195 | 3.0555 | 195 | 195 |
| I09 | v1-position-6h | 2026-11-09T11:27:48.526675Z | Review | 195 | 9.6276 | 195 | 195 |
| I02 | v2-message-state | 2026-11-09T11:27:48.450535Z | Review | 129 | 9.4654 | 129 | 54 |
| I02 | v1-position-6h | 2026-11-09T11:27:48.202640Z | Review | 129 | 21.6696 | 129 | 54 |
| I10 | v1-position-6h | 2026-11-09T07:30:03.077172Z | Review | 239 | 15.9350 | 239 | 239 |
| I09 | v1-position-6h | 2026-11-09T07:30:02.965468Z | Tracking | 239 | 3.6843 | 239 | 237 |
| I02 | v1-position-6h | 2026-11-09T07:30:02.661693Z | Review | 192 | 8.9956 | 192 | 116 |
| I02 | v2-message-state | 2026-11-09T07:30:02.892434Z | Review | 192 | 20.6825 | 192 | 116 |
| I10 | v1-position-6h | 2026-11-09T02:59:21.767924Z | Review | 286 | 7.9218 | 286 | 286 |
| I09 | v1-position-6h | 2026-11-09T02:59:21.651496Z | Tracking | 286 | 4.8961 | 286 | 284 |
| I02 | v1-position-6h | 2026-11-09T02:59:21.475281Z | Tracking | 246 | 4.7979 | 246 | 171 |
| I10 | v1-position-6h | 2026-11-08T23:12:00.859398Z | Tracking | 334 | 2.4063 | 334 | 334 |
| I09 | v1-position-6h | 2026-11-08T23:12:00.753567Z | Review | 334 | 12.0327 | 334 | 332 |
| I02 | v1-position-6h | 2026-11-08T23:12:00.588965Z | Review | 291 | 21.4680 | 291 | 216 |
| I10 | v1-position-6h | 2026-11-08T22:36:00.143061Z | Tracking | 334 | 3.1524 | 334 | 334 |
| I09 | v1-position-6h | 2026-11-08T22:36:00.026138Z | Review | 334 | 10.9644 | 334 | 332 |
| I02 | v1-position-6h | 2026-11-08T22:35:59.850666Z | Review | 297 | 22.1495 | 297 | 222 |
| I10 | v1-position-6h | 2026-11-08T20:35:50.210Z | Review | 358 | 13.0964 | 358 | 358 |
| I09 | v1-position-6h | 2026-11-08T20:35:49.991Z | Tracking | 358 | 3.8888 | 358 | 356 |
| I02 | v1-position-6h | 2026-11-08T20:35:49.678Z | Review | 321 | 17.7073 | 321 | 246 |

The Git-tracked history/prospective directory stores original RINEX/GP bytes, first receipts, parsed messages, frozen model documents, compressed pinned EOP/leap versions and immutable scoring chunks. GitHub caches are not the authoritative model archive. No automatic deletion is configured. Git repository size will grow; plan external archival storage as the history expands. The cumulative statistics CSV contains matched-epoch summaries; selected-model epoch CSVs and series JSON retain gaps and cohort identifiers. Blanks are gaps, not zero error.
