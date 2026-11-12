# Prospective NavIC SGP4 validation

Updated 2026-11-12T03:22:54.549992Z. 63 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional. V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.

Models issue every 30 minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
| I10 | v1-position-6h | 2026-11-12T03:22:54.424044Z | Waiting | 0 | — | 0 | 0 |
| I10 | v2-message-state | 2026-11-12T03:22:54.525350Z | Waiting | 0 | — | 0 | 0 |
| I09 | v2-message-state | 2026-11-12T03:22:54.361878Z | Waiting | 0 | — | 0 | 0 |
| I09 | v1-position-6h | 2026-11-12T03:22:54.200917Z | Waiting | 0 | — | 0 | 0 |
| I02 | v1-position-6h | 2026-11-12T03:22:53.867959Z | Waiting | 0 | — | 0 | 0 |
| I02 | v2-message-state | 2026-11-12T03:22:54.033350Z | Waiting | 0 | — | 0 | 0 |
| I10 | v1-position-6h | 2026-11-11T15:38:21.831087Z | Tracking | 64 | 1.6730 | 64 | 64 |
| I09 | v2-message-state | 2026-11-11T15:38:21.778524Z | Tracking | 51 | 3.4737 | 51 | 51 |
| I09 | v1-position-6h | 2026-11-11T15:38:21.584895Z | Review | 51 | 11.9098 | 51 | 51 |
| I02 | v1-position-6h | 2026-11-11T15:38:21.214711Z | Tracking | 78 | 4.1243 | 78 | 78 |
| I02 | v2-message-state | 2026-11-11T15:38:21.394006Z | Tracking | 78 | 1.5853 | 78 | 78 |
| I10 | v2-message-state | 2026-11-11T07:13:00.570907Z | Review | 160 | 7.4037 | 160 | 160 |
| I10 | v1-position-6h | 2026-11-11T07:13:00.421414Z | Review | 160 | 13.9188 | 160 | 160 |
| I09 | v2-message-state | 2026-11-11T07:13:00.354391Z | Tracking | 168 | 5.6634 | 168 | 168 |
| I09 | v1-position-6h | 2026-11-11T07:13:00.161717Z | Tracking | 168 | 1.9155 | 168 | 168 |
| I02 | v1-position-6h | 2026-11-11T07:12:59.730123Z | Tracking | 195 | 2.3541 | 0 | 106 |
| I02 | v2-message-state | 2026-11-11T07:12:59.921559Z | Review | 195 | 11.4938 | 0 | 106 |
| I10 | v2-message-state | 2026-11-11T00:41:28.576728Z | Review | 233 | 5.4583 | 233 | 233 |
| I09 | v2-message-state | 2026-11-11T00:41:28.500797Z | Review | 247 | 8.8310 | 247 | 247 |
| I09 | v1-position-6h | 2026-11-11T00:41:28.358733Z | Review | 247 | 13.5091 | 247 | 247 |
| I02 | v1-position-6h | 2026-11-11T00:41:28.141647Z | Review | 274 | 15.3142 | 0 | 107 |
| I02 | v2-message-state | 2026-11-11T00:41:28.282548Z | Tracking | 274 | 4.6639 | 0 | 107 |
| I10 | v1-position-6h | 2026-11-10T20:01:26.491960Z | Review | 257 | 17.9104 | 257 | 257 |
| I09 | v2-message-state | 2026-11-10T20:01:26.416695Z | Review | 256 | 11.6663 | 256 | 256 |
| I09 | v1-position-6h | 2026-11-10T20:01:26.241893Z | Tracking | 256 | 2.6478 | 256 | 256 |
| I02 | v2-message-state | 2026-11-10T20:01:25.896612Z | Review | 290 | 19.7842 | 0 | 107 |
| I02 | v1-position-6h | 2026-11-10T20:01:25.718756Z | Review | 290 | 9.3334 | 0 | 107 |
| I10 | v2-message-state | 2026-11-10T12:37:27.496148Z | Review | 329 | 10.2877 | 329 | 329 |
| I10 | v1-position-6h | 2026-11-10T12:37:27.427739Z | Tracking | 329 | 3.9275 | 329 | 329 |
| I09 | v1-position-6h | 2026-11-10T12:37:27.299248Z | Review | 361 | 19.2440 | 361 | 361 |
| I09 | v2-message-state | 2026-11-10T12:37:27.384056Z | Review | 361 | 9.9197 | 361 | 361 |
| I02 | v2-message-state | 2026-11-10T12:37:27.161874Z | Tracking | 396 | 5.4872 | 0 | 107 |
| I02 | v1-position-6h | 2026-11-10T12:37:27.068032Z | Review | 396 | 22.7366 | 0 | 107 |
| I10 | v1-position-6h | 2026-11-10T03:50:44.444496Z | Review | 449 | 13.3633 | 449 | 449 |
| I09 | v2-message-state | 2026-11-10T03:50:44.368827Z | Tracking | 466 | 2.6676 | 466 | 466 |
| I09 | v1-position-6h | 2026-11-10T03:50:44.132839Z | Tracking | 466 | 7.0522 | 466 | 466 |
| I02 | v1-position-6h | 2026-11-10T03:50:43.671047Z | Tracking | 476 | 3.5760 | 0 | 107 |
| I02 | v2-message-state | 2026-11-10T03:50:43.890411Z | Review | 476 | 8.3823 | 0 | 107 |
| I10 | v1-position-6h | 2026-11-09T21:38:52.645306Z | Review | 456 | 12.7244 | 456 | 456 |
| I09 | v1-position-6h | 2026-11-09T21:38:52.360083Z | Review | 474 | 9.9423 | 474 | 474 |
| I09 | v2-message-state | 2026-11-09T21:38:52.496939Z | Review | 474 | 20.2015 | 474 | 474 |
| I02 | v1-position-6h | 2026-11-09T21:38:51.906714Z | Review | 492 | 31.5219 | 0 | 53 |
| I02 | v2-message-state | 2026-11-09T21:38:52.123974Z | Review | 492 | 28.9696 | 0 | 53 |
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
