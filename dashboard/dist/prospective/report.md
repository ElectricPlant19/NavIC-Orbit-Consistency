# Prospective NavIC SGP4 validation

Updated 2026-11-11T07:13:00.595439Z. 52 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional. V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.

Models issue every 30 minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
| I10 | v2-message-state | 2026-11-11T07:13:00.570907Z | Waiting | 0 | — | 0 | 0 |
| I10 | v1-position-6h | 2026-11-11T07:13:00.421414Z | Waiting | 0 | — | 0 | 0 |
| I09 | v2-message-state | 2026-11-11T07:13:00.354391Z | Waiting | 0 | — | 0 | 0 |
| I09 | v1-position-6h | 2026-11-11T07:13:00.161717Z | Waiting | 0 | — | 0 | 0 |
| I02 | v1-position-6h | 2026-11-11T07:12:59.730123Z | Waiting | 0 | — | 0 | 0 |
| I02 | v2-message-state | 2026-11-11T07:12:59.921559Z | Waiting | 0 | — | 0 | 0 |
| I10 | v2-message-state | 2026-11-11T00:41:28.576728Z | Tracking | 63 | 0.4944 | 63 | 63 |
| I09 | v2-message-state | 2026-11-11T00:41:28.500797Z | Tracking | 77 | 1.3700 | 77 | 77 |
| I09 | v1-position-6h | 2026-11-11T00:41:28.358733Z | Tracking | 77 | 2.1159 | 77 | 77 |
| I02 | v1-position-6h | 2026-11-11T00:41:28.141647Z | Tracking | 77 | 4.1313 | 0 | 0 |
| I02 | v2-message-state | 2026-11-11T00:41:28.282548Z | Tracking | 77 | 1.6161 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-10T20:01:26.491960Z | Review | 87 | 11.3215 | 87 | 87 |
| I09 | v2-message-state | 2026-11-10T20:01:26.416695Z | Tracking | 86 | 1.5541 | 86 | 86 |
| I09 | v1-position-6h | 2026-11-10T20:01:26.241893Z | Tracking | 86 | 3.2009 | 86 | 86 |
| I02 | v2-message-state | 2026-11-10T20:01:25.896612Z | Tracking | 93 | 5.2069 | 0 | 0 |
| I02 | v1-position-6h | 2026-11-10T20:01:25.718756Z | Tracking | 93 | 1.8997 | 0 | 0 |
| I10 | v2-message-state | 2026-11-10T12:37:27.496148Z | Review | 159 | 5.2747 | 159 | 159 |
| I10 | v1-position-6h | 2026-11-10T12:37:27.427739Z | Tracking | 159 | 3.4463 | 159 | 159 |
| I09 | v1-position-6h | 2026-11-10T12:37:27.299248Z | Review | 191 | 12.6358 | 191 | 191 |
| I09 | v2-message-state | 2026-11-10T12:37:27.384056Z | Tracking | 191 | 6.9550 | 191 | 191 |
| I02 | v2-message-state | 2026-11-10T12:37:27.161874Z | Tracking | 199 | 3.7216 | 0 | 0 |
| I02 | v1-position-6h | 2026-11-10T12:37:27.068032Z | Review | 199 | 14.6693 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-10T03:50:44.444496Z | Review | 279 | 8.2966 | 279 | 279 |
| I09 | v2-message-state | 2026-11-10T03:50:44.368827Z | Tracking | 296 | 2.4420 | 296 | 296 |
| I09 | v1-position-6h | 2026-11-10T03:50:44.132839Z | Tracking | 296 | 4.9829 | 296 | 296 |
| I02 | v1-position-6h | 2026-11-10T03:50:43.671047Z | Tracking | 279 | 2.8790 | 0 | 0 |
| I02 | v2-message-state | 2026-11-10T03:50:43.890411Z | Tracking | 279 | 5.0392 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T21:38:52.645306Z | Review | 350 | 10.3945 | 350 | 350 |
| I09 | v1-position-6h | 2026-11-09T21:38:52.360083Z | Tracking | 355 | 6.9250 | 355 | 355 |
| I09 | v2-message-state | 2026-11-09T21:38:52.496939Z | Review | 355 | 14.3468 | 355 | 355 |
| I02 | v1-position-6h | 2026-11-09T21:38:51.906714Z | Review | 348 | 21.8470 | 0 | 0 |
| I02 | v2-message-state | 2026-11-09T21:38:52.123974Z | Review | 348 | 20.0233 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T11:27:48.642898Z | Tracking | 476 | 3.2163 | 476 | 476 |
| I09 | v1-position-6h | 2026-11-09T11:27:48.526675Z | Review | 494 | 18.1435 | 494 | 494 |
| I02 | v2-message-state | 2026-11-09T11:27:48.450535Z | Review | 421 | 13.7012 | 421 | 54 |
| I02 | v1-position-6h | 2026-11-09T11:27:48.202640Z | Review | 421 | 35.5615 | 421 | 54 |
| I10 | v1-position-6h | 2026-11-09T07:30:03.077172Z | Review | 519 | 26.2116 | 519 | 519 |
| I09 | v1-position-6h | 2026-11-09T07:30:02.965468Z | Tracking | 537 | 4.7152 | 537 | 535 |
| I02 | v1-position-6h | 2026-11-09T07:30:02.661693Z | Review | 483 | 16.7772 | 483 | 116 |
| I02 | v2-message-state | 2026-11-09T07:30:02.892434Z | Review | 483 | 38.6886 | 483 | 116 |
| I10 | v1-position-6h | 2026-11-09T02:59:21.767924Z | Review | 516 | 12.3925 | 516 | 516 |
| I09 | v1-position-6h | 2026-11-09T02:59:21.651496Z | Complete | 534 | 6.8891 | 534 | 532 |
| I02 | v1-position-6h | 2026-11-09T02:59:21.475281Z | Complete | 487 | 7.5509 | 487 | 171 |
| I10 | v1-position-6h | 2026-11-08T23:12:00.859398Z | Complete | 528 | 2.6409 | 528 | 528 |
| I09 | v1-position-6h | 2026-11-08T23:12:00.753567Z | Review | 547 | 18.8040 | 547 | 545 |
| I02 | v1-position-6h | 2026-11-08T23:12:00.588965Z | Review | 494 | 36.2565 | 494 | 216 |
| I10 | v1-position-6h | 2026-11-08T22:36:00.143061Z | Complete | 528 | 3.6074 | 528 | 528 |
| I09 | v1-position-6h | 2026-11-08T22:36:00.026138Z | Review | 547 | 17.1472 | 547 | 545 |
| I02 | v1-position-6h | 2026-11-08T22:35:59.850666Z | Review | 499 | 37.4819 | 499 | 222 |
| I10 | v1-position-6h | 2026-11-08T20:35:50.210Z | Review | 552 | 18.7730 | 552 | 552 |
| I09 | v1-position-6h | 2026-11-08T20:35:49.991Z | Complete | 560 | 5.6421 | 560 | 558 |
| I02 | v1-position-6h | 2026-11-08T20:35:49.678Z | Review | 508 | 29.7758 | 508 | 246 |

The Git-tracked history/prospective directory stores original RINEX/GP bytes, first receipts, parsed messages, frozen model documents, compressed pinned EOP/leap versions and immutable scoring chunks. GitHub caches are not the authoritative model archive. No automatic deletion is configured. Git repository size will grow; plan external archival storage as the history expands. The cumulative statistics CSV contains matched-epoch summaries; selected-model epoch CSVs and series JSON retain gaps and cohort identifiers. Blanks are gaps, not zero error.
