# Prospective NavIC SGP4 validation

Updated 2026-11-09T21:38:52.711205Z. 25 immutable issued models across 3 satellites.

Broadcast consistency, not absolute accuracy. No prospective scores are backfilled from retrospective experiments. Reference messages must first arrive after issue, have toc after issue and no later than the checked epoch, and cannot be training records. Frozen GP was available at issuance. Latest GP means latest received by each checked epoch; future snapshots are excluded. Statistics pool forecast-epoch pairs. Overlapping forecasts share reference epochs and are not independent observations. Waiting means future messages have not supplied a score yet. Missing references finalize after the configured wait; first scores are immutable. Issue times, model epochs and prediction ages are distinct. Stored OMMs never refit. GEO/IGSO thresholds are provisional. V1 is the six-hour position-fit control. V2 is an experimental latest-message position-and-motion fit; forward targets come only from the already-received message. Dashboard statistics are separated by version. Replay results are not prospective evidence.

Models issue every 30 minutes where fitting coverage and numerical checks permit. V1 fits six hours of already received positions. V2 fits position and motion over issue ±1 hour from one healthy message available at cutoff, within the toe policy including its differentiation stencil. V2 uses 60-second sampling and velocity residuals scaled by 10,000 seconds; Bstar and mean-motion derivatives stay zero. Its future targets are predictions of that message, not later messages. Both versions remain experimental; V2 is a challenger, not an accepted replacement. The serialized OMM is round-trip checked and frozen at actual issuance. Scores span up to 48 hours in 300-second steps. Missing references mature after 3 hours. No performance is claimed before later-message scores exist. Filter by model_version in the statistics CSV; pooled legacy fleet totals combine versions and must not be used to judge one fitter.

Both baseline comparisons use identical matched epochs within each comparison, with separate sample counts. RMS reductions and win fractions are descriptive, not significance tests. Latest GP is a rolling operational baseline, not a fair equal-age forecast. Exact snapshot and message identifiers, GP ages and signed RTN residuals are retained for every score. The prediction-age bins begin at actual issuance, not model epoch. Broadcast validity is the declared analysis policy, not an independently confirmed ICD fit guarantee.

| PRN | Model version | Issued UTC | Status | Reference epochs | Our RMS km | Frozen GP common epochs | Latest GP common epochs |
|---|---|---|---|---|---|---|---|
| I10 | v1-position-6h | 2026-11-09T21:38:52.645306Z | Waiting | 0 | — | 0 | 0 |
| I09 | v1-position-6h | 2026-11-09T21:38:52.360083Z | Waiting | 0 | — | 0 | 0 |
| I09 | v2-message-state | 2026-11-09T21:38:52.496939Z | Waiting | 0 | — | 0 | 0 |
| I02 | v1-position-6h | 2026-11-09T21:38:51.906714Z | Waiting | 0 | — | 0 | 0 |
| I02 | v2-message-state | 2026-11-09T21:38:52.123974Z | Waiting | 0 | — | 0 | 0 |
| I10 | v1-position-6h | 2026-11-09T11:27:48.642898Z | Tracking | 121 | 2.6439 | 121 | 121 |
| I09 | v1-position-6h | 2026-11-09T11:27:48.526675Z | Tracking | 121 | 4.4580 | 121 | 121 |
| I02 | v2-message-state | 2026-11-09T11:27:48.450535Z | Tracking | 58 | 7.1834 | 58 | 54 |
| I02 | v1-position-6h | 2026-11-09T11:27:48.202640Z | Review | 58 | 14.7377 | 58 | 54 |
| I10 | v1-position-6h | 2026-11-09T07:30:03.077172Z | Review | 164 | 13.4760 | 164 | 164 |
| I09 | v1-position-6h | 2026-11-09T07:30:02.965468Z | Tracking | 164 | 3.9595 | 164 | 162 |
| I02 | v1-position-6h | 2026-11-09T07:30:02.661693Z | Tracking | 120 | 4.6486 | 120 | 116 |
| I02 | v2-message-state | 2026-11-09T07:30:02.892434Z | Review | 120 | 11.8011 | 120 | 116 |
| I10 | v1-position-6h | 2026-11-09T02:59:21.767924Z | Review | 211 | 6.2872 | 211 | 211 |
| I09 | v1-position-6h | 2026-11-09T02:59:21.651496Z | Tracking | 211 | 5.0901 | 211 | 209 |
| I02 | v1-position-6h | 2026-11-09T02:59:21.475281Z | Tracking | 174 | 4.7977 | 174 | 171 |
| I10 | v1-position-6h | 2026-11-08T23:12:00.859398Z | Tracking | 260 | 2.6297 | 260 | 260 |
| I09 | v1-position-6h | 2026-11-08T23:12:00.753567Z | Review | 260 | 11.1196 | 260 | 258 |
| I02 | v1-position-6h | 2026-11-08T23:12:00.588965Z | Review | 220 | 18.9679 | 220 | 216 |
| I10 | v1-position-6h | 2026-11-08T22:36:00.143061Z | Tracking | 260 | 3.0774 | 260 | 260 |
| I09 | v1-position-6h | 2026-11-08T22:36:00.026138Z | Review | 260 | 10.1393 | 260 | 258 |
| I02 | v1-position-6h | 2026-11-08T22:35:59.850666Z | Review | 226 | 19.4985 | 226 | 222 |
| I10 | v1-position-6h | 2026-11-08T20:35:50.210Z | Review | 284 | 11.7054 | 284 | 284 |
| I09 | v1-position-6h | 2026-11-08T20:35:49.991Z | Tracking | 284 | 3.7777 | 284 | 282 |
| I02 | v1-position-6h | 2026-11-08T20:35:49.678Z | Review | 250 | 15.4482 | 250 | 246 |

The Git-tracked history/prospective directory stores original RINEX/GP bytes, first receipts, parsed messages, frozen model documents, compressed pinned EOP/leap versions and immutable scoring chunks. GitHub caches are not the authoritative model archive. No automatic deletion is configured. Git repository size will grow; plan external archival storage as the history expands. The cumulative statistics CSV contains matched-epoch summaries; selected-model epoch CSVs and series JSON retain gaps and cohort identifiers. Blanks are gaps, not zero error.
