# Prospective NavIC SGP4 validation

Updated 2026-11-11T22:17:40.313151Z. 57 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional. V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.

Models issue every 30 minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
| I10 | v1-position-6h | 2026-11-11T15:38:21.831087Z | Waiting | 0 | — | 0 | 0 |
| I09 | v2-message-state | 2026-11-11T15:38:21.778524Z | Waiting | 0 | — | 0 | 0 |
| I09 | v1-position-6h | 2026-11-11T15:38:21.584895Z | Waiting | 0 | — | 0 | 0 |
| I02 | v1-position-6h | 2026-11-11T15:38:21.214711Z | Waiting | 0 | — | 0 | 0 |
| I02 | v2-message-state | 2026-11-11T15:38:21.394006Z | Waiting | 0 | — | 0 | 0 |
| I10 | v2-message-state | 2026-11-11T07:13:00.570907Z | Tracking | 96 | 3.4673 | 96 | 96 |
| I10 | v1-position-6h | 2026-11-11T07:13:00.421414Z | Review | 96 | 5.5432 | 96 | 96 |
| I09 | v2-message-state | 2026-11-11T07:13:00.354391Z | Tracking | 117 | 0.5331 | 117 | 117 |
| I09 | v1-position-6h | 2026-11-11T07:13:00.161717Z | Tracking | 117 | 1.8944 | 117 | 117 |
| I02 | v1-position-6h | 2026-11-11T07:12:59.730123Z | Tracking | 117 | 1.8095 | 0 | 28 |
| I02 | v2-message-state | 2026-11-11T07:12:59.921559Z | Tracking | 117 | 1.5335 | 0 | 28 |
| I10 | v2-message-state | 2026-11-11T00:41:28.576728Z | Tracking | 168 | 1.6455 | 168 | 168 |
| I09 | v2-message-state | 2026-11-11T00:41:28.500797Z | Review | 195 | 8.0048 | 195 | 195 |
| I09 | v1-position-6h | 2026-11-11T00:41:28.358733Z | Review | 195 | 11.7434 | 195 | 195 |
| I02 | v1-position-6h | 2026-11-11T00:41:28.141647Z | Review | 195 | 13.4845 | 0 | 28 |
| I02 | v2-message-state | 2026-11-11T00:41:28.282548Z | Tracking | 195 | 4.6921 | 0 | 28 |
| I10 | v1-position-6h | 2026-11-10T20:01:26.491960Z | Review | 192 | 16.0812 | 192 | 192 |
| I09 | v2-message-state | 2026-11-10T20:01:26.416695Z | Review | 204 | 10.0708 | 204 | 204 |
| I09 | v1-position-6h | 2026-11-10T20:01:26.241893Z | Tracking | 204 | 2.8350 | 204 | 204 |
| I02 | v2-message-state | 2026-11-10T20:01:25.896612Z | Review | 211 | 17.0965 | 0 | 28 |
| I02 | v1-position-6h | 2026-11-10T20:01:25.718756Z | Review | 211 | 8.1139 | 0 | 28 |
| I10 | v2-message-state | 2026-11-10T12:37:27.496148Z | Review | 264 | 9.2431 | 264 | 264 |
| I10 | v1-position-6h | 2026-11-10T12:37:27.427739Z | Tracking | 264 | 2.8572 | 264 | 264 |
| I09 | v1-position-6h | 2026-11-10T12:37:27.299248Z | Review | 309 | 14.9398 | 309 | 309 |
| I09 | v2-message-state | 2026-11-10T12:37:27.384056Z | Tracking | 309 | 7.4603 | 309 | 309 |
| I02 | v2-message-state | 2026-11-10T12:37:27.161874Z | Tracking | 317 | 3.8298 | 0 | 28 |
| I02 | v1-position-6h | 2026-11-10T12:37:27.068032Z | Review | 317 | 17.0264 | 0 | 28 |
| I10 | v1-position-6h | 2026-11-10T03:50:44.444496Z | Review | 384 | 10.1493 | 384 | 384 |
| I09 | v2-message-state | 2026-11-10T03:50:44.368827Z | Tracking | 414 | 2.4619 | 414 | 414 |
| I09 | v1-position-6h | 2026-11-10T03:50:44.132839Z | Tracking | 414 | 6.7891 | 414 | 414 |
| I02 | v1-position-6h | 2026-11-10T03:50:43.671047Z | Tracking | 397 | 3.6852 | 0 | 28 |
| I02 | v2-message-state | 2026-11-10T03:50:43.890411Z | Tracking | 397 | 6.1131 | 0 | 28 |
| I10 | v1-position-6h | 2026-11-09T21:38:52.645306Z | Review | 456 | 12.7244 | 456 | 456 |
| I09 | v1-position-6h | 2026-11-09T21:38:52.360083Z | Review | 474 | 9.9423 | 474 | 474 |
| I09 | v2-message-state | 2026-11-09T21:38:52.496939Z | Review | 474 | 20.2015 | 474 | 474 |
| I02 | v1-position-6h | 2026-11-09T21:38:51.906714Z | Review | 467 | 30.2399 | 0 | 28 |
| I02 | v2-message-state | 2026-11-09T21:38:52.123974Z | Review | 467 | 27.7894 | 0 | 28 |
| I10 | v1-position-6h | 2026-11-09T11:27:48.642898Z | Complete | 527 | 3.1569 | 527 | 527 |
| I09 | v1-position-6h | 2026-11-09T11:27:48.526675Z | Review | 545 | 19.5307 | 545 | 545 |
| I02 | v2-message-state | 2026-11-09T11:27:48.450535Z | Review | 472 | 14.3970 | 472 | 54 |
| I02 | v1-position-6h | 2026-11-09T11:27:48.202640Z | Review | 472 | 37.9054 | 472 | 54 |
| I10 | v1-position-6h | 2026-11-09T07:30:03.077172Z | Review | 523 | 26.3554 | 523 | 523 |
| I09 | v1-position-6h | 2026-11-09T07:30:02.965468Z | Complete | 541 | 4.7278 | 541 | 539 |
| I02 | v1-position-6h | 2026-11-09T07:30:02.661693Z | Review | 487 | 16.8950 | 487 | 116 |
| I02 | v2-message-state | 2026-11-09T07:30:02.892434Z | Review | 487 | 38.9416 | 487 | 116 |
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
