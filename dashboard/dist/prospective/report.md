# Prospective NavIC SGP4 validation

Updated 2026-11-13T07:55:25.277730Z. 80 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional. V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.

Models issue every 30 minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
| I10 | v1-position-6h | 2026-11-13T07:55:25.217679Z | Waiting | 0 | — | 0 | 0 |
| I09 | v2-message-state | 2026-11-13T07:55:25.156243Z | Waiting | 0 | — | 0 | 0 |
| I09 | v1-position-6h | 2026-11-13T07:55:25.010067Z | Waiting | 0 | — | 0 | 0 |
| I02 | v1-position-6h | 2026-11-13T07:55:24.649041Z | Waiting | 0 | — | 0 | 0 |
| I02 | v2-message-state | 2026-11-13T07:55:24.785701Z | Waiting | 0 | — | 0 | 0 |
| I10 | v2-message-state | 2026-11-13T01:04:17.740776Z | Tracking | 71 | 0.6371 | 71 | 71 |
| I09 | v2-message-state | 2026-11-13T01:04:17.630296Z | Tracking | 82 | 1.6464 | 82 | 82 |
| I02 | v2-message-state | 2026-11-13T01:04:17.522167Z | Tracking | 82 | 1.0370 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-12T19:53:41.100909Z | Review | 95 | 9.7045 | 95 | 95 |
| I09 | v1-position-6h | 2026-11-12T19:53:40.991137Z | Tracking | 94 | 1.9037 | 94 | 94 |
| I02 | v1-position-6h | 2026-11-12T19:53:40.811090Z | Tracking | 100 | 2.5250 | 100 | 0 |
| I02 | v2-message-state | 2026-11-12T19:53:40.924471Z | Tracking | 100 | 2.6519 | 100 | 0 |
| I10 | v1-position-6h | 2026-11-12T11:52:08.929605Z | Tracking | 167 | 3.1639 | 167 | 167 |
| I09 | v1-position-6h | 2026-11-12T11:52:08.569364Z | Review | 142 | 13.4414 | 142 | 142 |
| I09 | v2-message-state | 2026-11-12T11:52:08.846828Z | Review | 142 | 17.4128 | 142 | 142 |
| I02 | v2-message-state | 2026-11-12T11:52:08.196189Z | Tracking | 169 | 5.5727 | 169 | 69 |
| I02 | v1-position-6h | 2026-11-12T11:52:07.997837Z | Review | 169 | 12.3063 | 169 | 69 |
| I10 | v1-position-6h | 2026-11-12T03:22:54.424044Z | Tracking | 263 | 2.5776 | 263 | 263 |
| I10 | v2-message-state | 2026-11-12T03:22:54.525350Z | Review | 263 | 12.8550 | 263 | 263 |
| I09 | v2-message-state | 2026-11-12T03:22:54.361878Z | Tracking | 259 | 4.2843 | 259 | 259 |
| I09 | v1-position-6h | 2026-11-12T03:22:54.200917Z | Review | 259 | 12.7731 | 259 | 259 |
| I02 | v1-position-6h | 2026-11-12T03:22:53.867959Z | Tracking | 286 | 4.2304 | 286 | 186 |
| I02 | v2-message-state | 2026-11-12T03:22:54.033350Z | Tracking | 286 | 1.6077 | 286 | 186 |
| I10 | v1-position-6h | 2026-11-11T15:38:21.831087Z | Review | 335 | 7.2032 | 335 | 335 |
| I09 | v2-message-state | 2026-11-11T15:38:21.778524Z | Tracking | 313 | 3.0136 | 313 | 313 |
| I09 | v1-position-6h | 2026-11-11T15:38:21.584895Z | Review | 313 | 17.2497 | 313 | 313 |
| I02 | v1-position-6h | 2026-11-11T15:38:21.214711Z | Tracking | 367 | 3.3600 | 367 | 267 |
| I02 | v2-message-state | 2026-11-11T15:38:21.394006Z | Tracking | 367 | 2.7945 | 367 | 267 |
| I10 | v2-message-state | 2026-11-11T07:13:00.570907Z | Review | 423 | 14.4129 | 423 | 423 |
| I10 | v1-position-6h | 2026-11-11T07:13:00.421414Z | Review | 423 | 27.1880 | 423 | 423 |
| I09 | v2-message-state | 2026-11-11T07:13:00.354391Z | Review | 422 | 13.3962 | 422 | 422 |
| I09 | v1-position-6h | 2026-11-11T07:13:00.161717Z | Tracking | 422 | 2.4742 | 422 | 422 |
| I02 | v1-position-6h | 2026-11-11T07:12:59.730123Z | Tracking | 476 | 3.8753 | 0 | 295 |
| I02 | v2-message-state | 2026-11-11T07:12:59.921559Z | Review | 476 | 24.5696 | 0 | 295 |
| I10 | v2-message-state | 2026-11-11T00:41:28.576728Z | Review | 417 | 9.6263 | 417 | 417 |
| I09 | v2-message-state | 2026-11-11T00:41:28.500797Z | Review | 422 | 14.1209 | 422 | 422 |
| I09 | v1-position-6h | 2026-11-11T00:41:28.358733Z | Review | 422 | 22.2998 | 422 | 422 |
| I02 | v1-position-6h | 2026-11-11T00:41:28.141647Z | Review | 476 | 24.8226 | 0 | 295 |
| I02 | v2-message-state | 2026-11-11T00:41:28.282548Z | Complete | 476 | 6.9599 | 0 | 295 |
| I10 | v1-position-6h | 2026-11-10T20:01:26.491960Z | Review | 432 | 27.1745 | 432 | 432 |
| I09 | v2-message-state | 2026-11-10T20:01:26.416695Z | Review | 423 | 19.0646 | 423 | 423 |
| I09 | v1-position-6h | 2026-11-10T20:01:26.241893Z | Review | 423 | 2.7901 | 423 | 423 |
| I02 | v2-message-state | 2026-11-10T20:01:25.896612Z | Review | 469 | 31.3591 | 0 | 286 |
| I02 | v1-position-6h | 2026-11-10T20:01:25.718756Z | Review | 469 | 14.7570 | 0 | 286 |
| I10 | v2-message-state | 2026-11-10T12:37:27.496148Z | Review | 432 | 14.8135 | 432 | 432 |
| I10 | v1-position-6h | 2026-11-10T12:37:27.427739Z | Review | 432 | 4.1944 | 432 | 432 |
| I09 | v1-position-6h | 2026-11-10T12:37:27.299248Z | Review | 472 | 24.3567 | 472 | 472 |
| I09 | v2-message-state | 2026-11-10T12:37:27.384056Z | Review | 472 | 11.9120 | 472 | 472 |
| I02 | v2-message-state | 2026-11-10T12:37:27.161874Z | Complete | 507 | 5.7138 | 0 | 218 |
| I02 | v1-position-6h | 2026-11-10T12:37:27.068032Z | Review | 507 | 27.1325 | 0 | 218 |
| I10 | v1-position-6h | 2026-11-10T03:50:44.444496Z | Review | 455 | 13.5659 | 455 | 455 |
| I09 | v2-message-state | 2026-11-10T03:50:44.368827Z | Complete | 472 | 2.6779 | 472 | 472 |
| I09 | v1-position-6h | 2026-11-10T03:50:44.132839Z | Complete | 472 | 7.0811 | 472 | 472 |
| I02 | v1-position-6h | 2026-11-10T03:50:43.671047Z | Complete | 482 | 3.5727 | 0 | 113 |
| I02 | v2-message-state | 2026-11-10T03:50:43.890411Z | Review | 482 | 8.5368 | 0 | 113 |
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
