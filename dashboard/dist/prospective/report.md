# Prospective NavIC SGP4 validation

Updated 2026-11-11T00:41:28.594977Z. 46 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional. V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.

Models issue every 30 minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
| I10 | v2-message-state | 2026-11-11T00:41:28.576728Z | Waiting | 0 | — | 0 | 0 |
| I09 | v2-message-state | 2026-11-11T00:41:28.500797Z | Waiting | 0 | — | 0 | 0 |
| I09 | v1-position-6h | 2026-11-11T00:41:28.358733Z | Waiting | 0 | — | 0 | 0 |
| I02 | v1-position-6h | 2026-11-11T00:41:28.141647Z | Waiting | 0 | — | 0 | 0 |
| I02 | v2-message-state | 2026-11-11T00:41:28.282548Z | Waiting | 0 | — | 0 | 0 |
| I10 | v1-position-6h | 2026-11-10T20:01:26.491960Z | Tracking | 9 | 3.6798 | 9 | 9 |
| I09 | v2-message-state | 2026-11-10T20:01:26.416695Z | Tracking | 8 | 0.1812 | 8 | 8 |
| I09 | v1-position-6h | 2026-11-10T20:01:26.241893Z | Tracking | 8 | 1.3200 | 8 | 8 |
| I02 | v2-message-state | 2026-11-10T20:01:25.896612Z | Tracking | 8 | 0.5557 | 0 | 0 |
| I02 | v1-position-6h | 2026-11-10T20:01:25.718756Z | Tracking | 8 | 0.7045 | 0 | 0 |
| I10 | v2-message-state | 2026-11-10T12:37:27.496148Z | Tracking | 80 | 0.6958 | 80 | 80 |
| I10 | v1-position-6h | 2026-11-10T12:37:27.427739Z | Tracking | 80 | 2.4053 | 80 | 80 |
| I09 | v1-position-6h | 2026-11-10T12:37:27.299248Z | Tracking | 112 | 6.0832 | 112 | 112 |
| I09 | v2-message-state | 2026-11-10T12:37:27.384056Z | Tracking | 112 | 3.8417 | 112 | 112 |
| I02 | v2-message-state | 2026-11-10T12:37:27.161874Z | Tracking | 112 | 3.2961 | 0 | 0 |
| I02 | v1-position-6h | 2026-11-10T12:37:27.068032Z | Review | 112 | 9.0470 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-10T03:50:44.444496Z | Review | 201 | 6.0982 | 201 | 201 |
| I09 | v2-message-state | 2026-11-10T03:50:44.368827Z | Tracking | 218 | 2.6289 | 218 | 218 |
| I09 | v1-position-6h | 2026-11-10T03:50:44.132839Z | Tracking | 218 | 5.0632 | 218 | 218 |
| I02 | v1-position-6h | 2026-11-10T03:50:43.671047Z | Tracking | 194 | 3.1100 | 0 | 0 |
| I02 | v2-message-state | 2026-11-10T03:50:43.890411Z | Tracking | 194 | 2.6313 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T21:38:52.645306Z | Review | 272 | 8.2672 | 272 | 272 |
| I09 | v1-position-6h | 2026-11-09T21:38:52.360083Z | Tracking | 277 | 6.5477 | 277 | 277 |
| I09 | v2-message-state | 2026-11-09T21:38:52.496939Z | Review | 277 | 12.8959 | 277 | 277 |
| I02 | v1-position-6h | 2026-11-09T21:38:51.906714Z | Review | 262 | 19.2432 | 0 | 0 |
| I02 | v2-message-state | 2026-11-09T21:38:52.123974Z | Review | 262 | 17.6610 | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T11:27:48.642898Z | Tracking | 397 | 2.6146 | 397 | 397 |
| I09 | v1-position-6h | 2026-11-09T11:27:48.526675Z | Review | 415 | 14.2977 | 415 | 415 |
| I02 | v2-message-state | 2026-11-09T11:27:48.450535Z | Review | 334 | 11.5626 | 334 | 54 |
| I02 | v1-position-6h | 2026-11-09T11:27:48.202640Z | Review | 334 | 29.0185 | 334 | 54 |
| I10 | v1-position-6h | 2026-11-09T07:30:03.077172Z | Review | 441 | 22.8650 | 441 | 441 |
| I09 | v1-position-6h | 2026-11-09T07:30:02.965468Z | Tracking | 459 | 4.6300 | 459 | 457 |
| I02 | v1-position-6h | 2026-11-09T07:30:02.661693Z | Review | 397 | 13.2307 | 397 | 116 |
| I02 | v2-message-state | 2026-11-09T07:30:02.892434Z | Review | 397 | 31.1219 | 397 | 116 |
| I10 | v1-position-6h | 2026-11-09T02:59:21.767924Z | Review | 488 | 11.5621 | 488 | 488 |
| I09 | v1-position-6h | 2026-11-09T02:59:21.651496Z | Tracking | 506 | 6.7716 | 506 | 504 |
| I02 | v1-position-6h | 2026-11-09T02:59:21.475281Z | Tracking | 451 | 7.3512 | 451 | 171 |
| I10 | v1-position-6h | 2026-11-08T23:12:00.859398Z | Tracking | 528 | 2.6409 | 528 | 528 |
| I09 | v1-position-6h | 2026-11-08T23:12:00.753567Z | Review | 547 | 18.8040 | 547 | 545 |
| I02 | v1-position-6h | 2026-11-08T23:12:00.588965Z | Review | 489 | 36.0306 | 489 | 216 |
| I10 | v1-position-6h | 2026-11-08T22:36:00.143061Z | Tracking | 528 | 3.6074 | 528 | 528 |
| I09 | v1-position-6h | 2026-11-08T22:36:00.026138Z | Review | 547 | 17.1472 | 547 | 545 |
| I02 | v1-position-6h | 2026-11-08T22:35:59.850666Z | Review | 495 | 37.2932 | 495 | 222 |
| I10 | v1-position-6h | 2026-11-08T20:35:50.210Z | Review | 552 | 18.7730 | 552 | 552 |
| I09 | v1-position-6h | 2026-11-08T20:35:49.991Z | Complete | 560 | 5.6421 | 560 | 558 |
| I02 | v1-position-6h | 2026-11-08T20:35:49.678Z | Review | 508 | 29.7758 | 508 | 246 |

The Git-tracked history/prospective directory stores original RINEX/GP bytes, first receipts, parsed messages, frozen model documents, compressed pinned EOP/leap versions and immutable scoring chunks. GitHub caches are not the authoritative model archive. No automatic deletion is configured. Git repository size will grow; plan external archival storage as the history expands. The cumulative statistics CSV contains matched-epoch summaries; selected-model epoch CSVs and series JSON retain gaps and cohort identifiers. Blanks are gaps, not zero error.
