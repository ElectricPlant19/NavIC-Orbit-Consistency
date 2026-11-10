# Prospective NavIC SGP4 validation

Updated 2026-11-10T12:37:27.509732Z. 36 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional. V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.

Models issue every 30 minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
| I10 | v2-message-state | 2026-11-10T12:37:27.496148Z | Waiting | 0 | — | 0 | 0 |
| I10 | v1-position-6h | 2026-11-10T12:37:27.427739Z | Waiting | 0 | — | 0 | 0 |
| I09 | v1-position-6h | 2026-11-10T12:37:27.299248Z | Waiting | 0 | — | 0 | 0 |
| I09 | v2-message-state | 2026-11-10T12:37:27.384056Z | Waiting | 0 | — | 0 | 0 |
| I02 | v2-message-state | 2026-11-10T12:37:27.161874Z | Waiting | 0 | — | 0 | 0 |
| I02 | v1-position-6h | 2026-11-10T12:37:27.068032Z | Waiting | 0 | — | 0 | 0 |
| I10 | v1-position-6h | 2026-11-10T03:50:44.444496Z | Tracking | 104 | 1.0655 | 104 | 104 |
| I09 | v2-message-state | 2026-11-10T03:50:44.368827Z | Tracking | 103 | 1.2342 | 103 | 103 |
| I09 | v1-position-6h | 2026-11-10T03:50:44.132839Z | Tracking | 103 | 4.3871 | 103 | 103 |
| I02 | v1-position-6h | 2026-11-10T03:50:43.671047Z | Tracking | 79 | 4.1603 | 0 | 0 |
| I02 | v2-message-state | 2026-11-10T03:50:43.890411Z | Tracking | 79 | 1.0078 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T21:38:52.645306Z | Review | 175 | 7.9930 | 175 | 175 |
| I09 | v1-position-6h | 2026-11-09T21:38:52.360083Z | Tracking | 162 | 3.5823 | 162 | 162 |
| I09 | v2-message-state | 2026-11-09T21:38:52.496939Z | Tracking | 162 | 7.6139 | 162 | 162 |
| I02 | v1-position-6h | 2026-11-09T21:38:51.906714Z | Review | 147 | 13.3474 | 0 | 0 |
| I02 | v2-message-state | 2026-11-09T21:38:52.123974Z | Review | 147 | 12.2886 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T11:27:48.642898Z | Tracking | 300 | 2.6910 | 300 | 300 |
| I09 | v1-position-6h | 2026-11-09T11:27:48.526675Z | Review | 300 | 11.7859 | 300 | 300 |
| I02 | v2-message-state | 2026-11-09T11:27:48.450535Z | Review | 219 | 9.4525 | 219 | 54 |
| I02 | v1-position-6h | 2026-11-09T11:27:48.202640Z | Review | 219 | 23.9474 | 219 | 54 |
| I10 | v1-position-6h | 2026-11-09T07:30:03.077172Z | Review | 344 | 17.7606 | 344 | 344 |
| I09 | v1-position-6h | 2026-11-09T07:30:02.965468Z | Tracking | 344 | 3.5334 | 344 | 342 |
| I02 | v1-position-6h | 2026-11-09T07:30:02.661693Z | Review | 282 | 10.8594 | 282 | 116 |
| I02 | v2-message-state | 2026-11-09T07:30:02.892434Z | Review | 282 | 24.6038 | 282 | 116 |
| I10 | v1-position-6h | 2026-11-09T02:59:21.767924Z | Review | 391 | 8.8285 | 391 | 391 |
| I09 | v1-position-6h | 2026-11-09T02:59:21.651496Z | Tracking | 391 | 5.7525 | 391 | 389 |
| I02 | v1-position-6h | 2026-11-09T02:59:21.475281Z | Tracking | 336 | 6.7150 | 336 | 171 |
| I10 | v1-position-6h | 2026-11-08T23:12:00.859398Z | Tracking | 440 | 2.5314 | 440 | 440 |
| I09 | v1-position-6h | 2026-11-08T23:12:00.753567Z | Review | 440 | 14.8161 | 440 | 438 |
| I02 | v1-position-6h | 2026-11-08T23:12:00.588965Z | Review | 382 | 28.9192 | 382 | 216 |
| I10 | v1-position-6h | 2026-11-08T22:36:00.143061Z | Tracking | 440 | 3.7811 | 440 | 440 |
| I09 | v1-position-6h | 2026-11-08T22:36:00.026138Z | Review | 440 | 13.4219 | 440 | 438 |
| I02 | v1-position-6h | 2026-11-08T22:35:59.850666Z | Review | 388 | 29.8955 | 388 | 222 |
| I10 | v1-position-6h | 2026-11-08T20:35:50.210Z | Review | 464 | 17.0960 | 464 | 464 |
| I09 | v1-position-6h | 2026-11-08T20:35:49.991Z | Tracking | 464 | 4.1525 | 464 | 462 |
| I02 | v1-position-6h | 2026-11-08T20:35:49.678Z | Review | 412 | 24.1533 | 412 | 246 |

The Git-tracked history/prospective directory stores original RINEX/GP bytes, first receipts, parsed messages, frozen model documents, compressed pinned EOP/leap versions and immutable scoring chunks. GitHub caches are not the authoritative model archive. No automatic deletion is configured. Git repository size will grow; plan external archival storage as the history expands. The cumulative statistics CSV contains matched-epoch summaries; selected-model epoch CSVs and series JSON retain gaps and cohort identifiers. Blanks are gaps, not zero error.
