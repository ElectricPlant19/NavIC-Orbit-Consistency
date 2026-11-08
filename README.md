# NavIC Orbit Consistency

Reproducible comparison of broadcast navigation-message orbits and CelesTrak GP/SGP4 trajectories at identical physical epochs. **This is a consistency assessment. Neither source is truth.**

The first observed run uses the BKG IGS BRDC file for **7 November 2026 UTC**. It contains **four** NavIC PRNs (I02, I09, I10, I11); three have geometrically confirmed GP matches. The dashboard header and table use the same run registry. No nominal fleet count or sample residual is hard-coded.

## Start

Python 3.11+ is required. The validated environment used Python 3.13.3; GitHub Actions uses 3.12.

```powershell
python -m pip install -r requirements.lock
python -m pip install --no-deps -e .
python -m pytest -q --basetemp .test-tmp
python -m navic_compare.cli daily
python -m http.server 8765 --directory dashboard/dist
```

Open http://localhost:8765. `daily` fetches the previous **UTC** day's completed navigation file, archives inputs, compares usable satellites, and refreshes the local dashboard. On Windows, allow local network access if the execution sandbox blocks the server. Run commands from the repository root.

Acquire GP snapshots now to build history:

```powershell
python -m navic_compare.cli poll-gp
```

A persisted two-hour guard and conditional HTTP requests prevent excessive CelesTrak polling. Each snapshot is content-addressed with an append-only retrieval journal. Today's current GP set cannot recreate unarchived historical sets. The first run consequently has partial coverage; subsequent runs improve as the archive accumulates. Only prior GP epochs are used by default, up to a 48-hour age cap.

## Local inputs and reproduction

```powershell
python -m navic_compare.cli compare --date 2026-11-07 --rinex path/to/nav.rnx.gz --gp path/to/snapshot.omm.json --eop path/to/finals2000A.all --leaps path/to/Leap_Second.dat
```

Repeat `--gp` for multiple snapshots; add `--sp3 reference.sp3.gz` for a third trajectory wherever coverage exists. Paths may be absolute. To reproduce an observed run, retain the exact raw files and software versions in its manifest. `data/raw/` is an immutable local content-addressed archive; `data/retrievals.jsonl` supplies source URLs and retrieval times. The published first-run manifest points to these archived local files. Run IDs include input/config/code/software fingerprints. Existing outputs are checksum-verified and never overwritten; incomplete runs remain `.partial` for inspection.

Outputs in `results/<run-id>/`:

| File | Purpose |
|---|---|
| `epochs.csv`, `epochs.json` | Every satellite/grid epoch, paired positions, 3D/RTN residuals, signed GP age, issue/health/URA, source identifiers and flags; gaps are null |
| `summary.json` | Per-satellite mean, RMS, maximum/time, RTN RMS, age bins/trend, quality flags and computed status; fleet counts and mean RMS |
| `identity.json` | Explicit PRN/NORAD/name matches, all candidate distances and multi-epoch evidence |
| `ephemerides.json` | Parsed Keplerian/harmonic parameters, clock, toe, IODEC, health, URA and time system |
| `eop_used.json` | Applied UT1−UTC and polar motion at every grid epoch |
| `manifest.json`, `checksums.json` | Input/output hashes, retrieval metadata, parameters and software/code versions |
| `report.md` | Method, assumptions, findings and limitations |
| `validation.json` | Explicit baseline/calibration state |

The dashboard includes satellite/status filters, separation and RTN plots, GP-age view/overlay, identity evidence, quality notes, report viewer, manifest viewer and CSV export. `Load run` accepts a generated `summary.json` and matching `epochs.json` together; processing stays local in the browser. The static dashboard does not fetch or propagate orbits itself.

## Current-day acquisition and controlled recency test

```powershell
python -m navic_compare.cli fresh
python -m navic_compare.cli fresh --acquire-only
```

`fresh` discovers actual files in the current **UTC** day's BKG directory. It validates gzip, RINEX headers and supported NavIC content, then assesses each satellite at the check time. Candidates are ranked by usable satellite count and ephemeris age, with WRD stream/receiver filename priority only breaking ties. A file containing only stale/unhealthy/unusable NavIC data is rejected. A file with a mix of healthy and unusable satellites can still be selected; gaps remain explicit. Same-day partial data do not overwrite the completed daily dataset.

HTTP ETag/Last-Modified validators are persisted. A `304 Not Modified` response reuses only a checksum-verified archived body and keeps its original receipt timestamp. Changed bytes are archived immutably by SHA-256. Directory HTML, raw files and all retrieval events are retained; each acquisition assessment is also written immutably under `data/acquisitions/`. `data/acquisition-current.json` is the latest assessment. A new download or recently modified file does not by itself establish fresh orbital parameters.

Freshness checks enforce the existing health, URA, IODEC and absolute toe-age policy. The ±2 h limit remains an explicitly labelled **analysis cutoff**, based on nominal update cadence; a message-specific ICD fit-interval guarantee has not been established. The software does not claim certified validity or extrapolate broadcast targets across gaps.

The controlled experiment fits a model to six hours of recent broadcast positions and a control model to six hours ending six hours earlier. Both use the same optimizer and sample cadence and are evaluated at exactly the same later physical epochs over one hour. Their element epochs are their respective simulated issue times. Standard GP is frozen at the retrospective origin and used only when both its archived receipt time and its element epoch precede that origin. Missing delayed baselines or GP snapshots remain unavailable, not zero error. Explicit PRN/NORAD mappings are retained in configuration with historical provenance; no name-number equivalence is assumed.

**This is retrospective, not a demonstrated live forecast.** Current files are first received after the simulated forecast origin. Filtering on toc prevents using later reference epochs for training, but toc is not proof of transmission/receipt time. Reduced RMS means closer agreement with the valid broadcast trajectory in this experiment, not absolute accuracy, a general advantage over standard GP or established release validity. The research OMMs are kept in `benchmark-models.json`; they do not replace the daily accepted-model download. A prospective study must freeze an actually received snapshot/model before collecting later reference messages.

Each immutable run under `results/fresh/<timestamp-hash>/` contains `fresh.json` (freshness, experiment, input hashes, code/software versions), `residuals.csv/json` (common-epoch 3D/RTN residuals), `benchmark-models.json`, `report.md` and `checksums.json`. The separate dashboard feed is `dashboard/dist/fresh/`. The **Current-day inputs** panel shows selected source, UTC reference epochs, signed age, health/URA, the three comparison cohorts, missing baselines, full diagnostics and a report. Its feed is checksum-verified independently of the daily run. **Download experimental recent-model OMM** exports a plain OMM JSON array containing only fitted recent-input models with check samples from the displayed experiment. The source bundle is checksum-verified before export; delayed controls are excluded. The filename and model comments identify the run and experimental status. These models do not pass through the separate daily acceptance gates.

The existing Actions workflow now runs current acquisition every 30 minutes, at UTC minutes 11 and 41, while retaining the completed-day job. GitHub schedules are best effort. The same persistent GP rate guard still limits CelesTrak requests to one per two hours. Acquisition reports, raw files and experiment outputs are included in the 90-day Actions artifacts; preserve them outside the cache/artifact retention period for long-term reproducibility. No NTRIP connection is required or enabled for this file-based stage.

## Experimental NavIC SupGP-style generator

Daily processing now also fits **new SGP4 mean elements** to the valid broadcast-derived trajectory. This independently generated product is named **NAVIC-BROADCAST-FIT**, not CelesTrak SupGP. The original broadcast-versus-CelesTrak comparison remains separate.

The default chronological split fits the first **18 hours** of the UTC day and validates the frozen model on the later **6 hours**, at 300-second sampling. The optimizer receives training positions only. Its initial estimate comes from a training-arc broadcast TEME position/velocity; CelesTrak GP supplies catalogue metadata, not fitting targets or initial mean elements. Training ephemeris records with toc after the split are excluded. Gaps, health, URA and issue checks remain enforced; missing data are never filled by extrapolation.

The six fitted variables use nonsingular eccentricity/inclination vectors for nearly circular and equatorial orbits. Every trial is evaluated with the actual WGS72 SGP4 deep-space model. BSTAR and mean-motion derivatives stay zero because this short near-geosynchronous fit does not estimate drag. A direct conversion from osculating broadcast Kepler elements to SGP4 mean elements would be incorrect; the numerical optimizer performs that fit.

`config/default.json` → `generator` controls sample cadence, split, coverage/span requirements, evaluation budget and per-class acceptance gates. Current provisional gates require fit RMS ≤1 km, held-out RMS ≤5 km and held-out maximum ≤10 km, plus ≥80% coverage, sufficient time span, optimizer convergence and a full-rank fit. These are engineering gates, not independently validated accuracy limits. The exported OMM representation is reloaded and propagation-checked before acceptance.

| Additional output | Contents |
|---|---|
| `generated.omm.json` | Only accepted SGP4-compatible OMM/JSON element sets; an empty list means no accepted model |
| `fit_summary.json` | Fit/held-out statistics, coverage, optimizer diagnostics, thresholds, reasons, source/run context |
| `fitted_epochs.csv/json` | Separate fit/holdout partitions, residuals, RTN components, ephemeris IDs and gaps |

The dashboard's **Fitted orbit models** section shows these statistics, solid fitting curves, dashed later-validation curves, rejection reasons and an accepted-OMM download. Downloads are checksum-checked against the loaded run. Rejected models never enter the downloadable product. Run the complete local comparison plus fitting stage with:

```powershell
python -m navic_compare.cli fit --date YYYY-MM-DD --rinex mixed.rnx.gz --gp archived.omm.json --eop finals2000A.all --leaps Leap_Second.dat
```

Set `generator.enabled` to `false` to disable fitting. The `fit` command runs the complete comparison and fitting pipeline, so it retains the existing satellite-identity checks. Scheduled daily runs use the same stage automatically.

Held-out broadcast epochs are separate in time but share broadcast-system/model biases with the training data. This retrospective experiment does not establish live forecasting performance, absolute accuracy, indefinite element validity or improvement over standard GP. Use the tested windows in fit_summary.json. `REV_AT_EPOCH=0` is an unspecified revolution-count placeholder. Keep the companion manifest/report with the OMM: the element set alone does not describe its acceptance window or limitations.

## Scientific controls and known limits

- RINEX **3/4 NavIC LNAV** is supported. RINEX4 **L1NV is excluded**, with notes. Other constellations are skipped except GPS LNAV retained for validation. No file is accepted without supported NavIC `I` records.
- RINEX IRN calendar time is nominally GPS-like (TAI−19); UTC conversion uses a pinned leap table. RINEX3 IRUT fractional corrections are applied when available. Missing corrections and RINEX4 STO are disclosed as a nominal sub-microsecond alignment assumption.
- Both propagators evaluate the same Astropy Time grid. A UTC leap-second day has the correct number of SI samples. UTC midnights bound the window; UT1 drives Earth rotation.
- Broadcast uses the ICD Keplerian/harmonic algorithm. Nearest toe, health, IODEC range/conflicts and GPS IODE/IODC are checked. The default **±2 h analysis window is a conservative policy based on the ICD nominal update cadence, not a verified ICD fit-interval guarantee**. Adjust it only with documented message-specific evidence. No gaps enter residual statistics.
- python-sgp4 automatically selects its deep-space branch; WGS72 is used for GP. TEME→ITRS uses UT1/GMST82 and polar motion with pinned IERS tables. Predicted EOP values are disclosed and out-of-coverage values are rejected.
- RTN uses broadcast **inertial** velocity, including frame rotation. This avoids the near-zero ECEF velocity of GEO. Residual sign is GP minus broadcast.
- Identity is geometric, not inferred from numbering. At least two test epochs must pass the distance gate and runner-up margin; duplicate assignments fail closed. No passing candidate means no comparison. Geometry corroborates rather than replaces authoritative catalogue identity.
- Orbit class is inferred from broadcast inclination, with a configurable 5° boundary; drifting retired GEO vehicles may need a reviewed class override or revised boundary. Actual inclination is recorded per satellite.
- GEO/IGSO thresholds are separate and **provisional**. Status includes missing coverage, stale/missing inputs, health and identity problems. Normal element/ephemeris replacements are recorded as context; jumps are flagged separately. An age trend across mixed sets is descriptive, not a causal error-growth estimate.
- The real GPS/SP3 diagnostic passed on 7 November 2026: **1.889 m broadcast/SP3 RMS over 19,370 paired epochs** (26 GPS satellites). The mean satellite broadcast/SGP4 RMS was 1.674 km. Evidence, input hashes and software versions are in `validation/gps-2026-11-07.json`. The IGS ultra-rapid product includes observed and predicted arcs. Threshold calibration remains **pending**. The numerical test suite is not a substitute. For a real GPS check, supply a combined NavIC/GPS RINEX, historical GPS GP snapshots, matching EOP/leaps and an SP3:

```powershell
python -m navic_compare.cli validate-gps --date YYYY-MM-DD --rinex mixed.rnx.gz --gp gps-history.json --eop finals2000A.all --leaps Leap_Second.dat --sp3 gps.sp3.gz --dashboard validation-dashboard
```

The diagnostic requires paired broadcast/SP3 epochs and checks for <20 m RMS. Reference-point differences and product quality need review. The recorded diagnostic supports the numerical chain; NavIC interpretation remains preliminary pending baseline threshold calibration. No NavIC SP3 coverage is assumed. Broadcast antenna phase-center and SP3 center-of-mass differences can matter at metre scale.

## Acquisition and automation

`config/default.json` declares date-derived long filenames and source priority: BKG BRDC → CDDIS → BKG DLR BRDM → GFZ BRDM. Each source must pass gzip integrity, header and NavIC-content checks; endpoints can be overridden when archive layouts change. BKG was verified for the initial date. CDDIS requires Earthdata credentials, normally through a user-managed requests-compatible `.netrc` and session cookies; credentials never belong in this repository. Fallback endpoints have not all been exercised against live files.

`.github/workflows/daily.yml` polls GP every two hours and runs yesterday's complete comparison daily at **06:43 UTC (12:13 IST)**. GitHub schedules can be delayed. A manual dispatch supports a date. The persistent Actions cache restores the raw archive and rate guard. Each job uploads results, dashboard, raw inputs and logs as immutable Actions artifacts (90-day retention). Cache eviction and artifact expiry are real limits: copy raw archives to long-term storage for indefinite reproducibility. A newly activated job needs time to accumulate GP history.

The daily job commits the validated dataset under `dashboard/dist/data` to this repository's main branch. The public Sites dashboard reads that **public repository's** data feed on load and every 30 minutes, checking SHA-256 digests to reject partially cached updates. It falls back to its bundled first-run snapshot if the feed is unavailable. The repository is public, so this does not require a token or expose a private credential. Change `dashboard/dist/feed.json` if moving the repository. CI needs `contents: write` for dataset publication; normal branch protection still applies. The first genuine GP snapshot and its retrieval time seed empty CI archives, including the rate guard. No deployment credentials are embedded in Actions.

Failures produce a nonzero exit code, `data/pipeline.log` and `data/alert.json`. Missing/Review satellites also produce structured alerts. Optionally set the repository secret `NAVIC_ALERT_WEBHOOK` to an explicitly chosen endpoint; no recipient is assumed or contacted without configuration. GitHub's workflow-failure notifications remain available. Current-day BKG file discovery and assessment run every 30 minutes; this does not imply a guaranteed source update interval.

## References

[ISRO SPS ICD v1.1](https://www.isro.gov.in/media_isro/pdf/SateliteNavigation/irnss_sps_icd_version1.1-2017.pdf), [IGS RINEX 4.02](https://files.igs.org/pub/data/format/rinex_4.02.pdf), [Vallado SGP4 reference](https://celestrak.org/publications/AIAA/2006-6753/), [CelesTrak GP documentation](https://celestrak.org/NORAD/documentation/gp-data-formats.php), [usage policy](https://celestrak.org/usage-policy.php), [Astropy frame guide](https://docs.astropy.org/en/stable/coordinates/satellites.html).

I11 is explicitly catalogued as **NVS-03 (IRNSS-1L), NORAD 101228**, following the user-supplied mapping on 8 November 2026. Catalogue identity is preserved even when geometric confirmation fails. The first archived GP is from 5 November and does not pass the geometric gate against the 7 November broadcast trajectory; I11 remains Review, with no accepted residuals. No name or launch numbering inference overrides that declared mapping.

The genuine GPS GP snapshot and SP3 file used for the baseline are preserved byte-for-byte under validation/inputs/. Their content hashes match validation/gps-2026-11-07.json; the broadcast, EOP and leap inputs are shared with the archived NavIC run.


## Prospective frozen-model history

`python -m navic_compare.cli track` archives truly issued models and scores them against later broadcast messages. It uses the latest acquisition assessment from `fresh` (no older than one hour) and already received neighbouring-day data for six-hour training. It issues a separate experimental OMM at actual processing time every 30-minute slot where coverage and numerical checks permit; this is not an adoption of the retrospective model's simulated issue time. The serialized OMM is re-imported and checked to 1 mm against the fitted object before issuance. The model, actual issue time, fit cutoff/element epoch, training-record fingerprints, configuration, code hash, software versions, pinned supporting inputs and available frozen GP baseline are immutable.

The authoritative archive is **Git-tracked `history/prospective/`**, not the Actions cache. It preserves original RINEX and GP bytes by checksum, earliest known receipt metadata, parsed navigation records, frozen issues, compressed EOP/leap snapshots and append-only scoring chunks. `scripts/prospective_guard.py` also saves/restores the GP HTTP state and two-hour rate guard through Git so a cache eviction does not reset the polling limit. Cached paths are restored portably. Do not delete history to recover a failed job.

Each OMM is watched for 48 hours, at five-minute intervals after **actual issuance**. A reference record must be first received after issue, have toc strictly after issue and no later than the scored epoch, not be a training record, and pass the existing toe-age/health/URA/IODEC policy. References can arrive after the checked epoch; this remains broadcast consistency, using later messages, not independent tracking observations. Missing epochs remain pending for three hours, then finalize as explicit gaps. The first assessment of an epoch is immutable; later reference revisions do not silently rewrite a score. Retrospective experiments are never backfilled into prospective results.

Two CelesTrak baselines are scored: **frozen at actual issue** (eligible snapshot receipt and element epoch precede issue), and **latest received by each checked epoch** (future snapshots/element epochs excluded, age capped). The former tests aging forecasts on equal release availability; the latter tests an older model against a rolling GP service. Frozen GP is allowed to age through the watch horizon; its per-epoch age is retained. GP polling remains guarded at two hours, so latest means latest collected by our pipeline, not every possible CelesTrak update.

The Forecast history dashboard shows issued models, Waiting/Tracking/Complete/Review states, coverage, pending epochs, matched-epoch RMS/mean/max, signed RTN residuals, age bins (0–1, 1–3, 3–6, 6–12, 12–24, 24–48 h), percentile statistics in provenance, RMS reduction and lower-separation fractions. GP changes split chart lines; message/GP changes, discontinuities and provisional per-orbit-class thresholds are recorded. Both baseline comparisons use identical epochs within that comparison and disclose separate counts. Pooled forecast-epoch pairs overlap; they are not independent observations or a significance test. Waiting is not a quality pass. A research issue need not pass the separate daily accepted-model gates.

The workflow runs tracking after the 30-minute current-day step, including when current acquisition fails, so archived models can still be scored where retained inputs allow. Results and history are committed together; a failed scorer does not publish an incomplete new summary. Failure/review logs are retained and the existing optional alert webhook is supported. The dashboard loads a checksum-verified bundled snapshot then the latest public GitHub feed on load/every 30 minutes. Download controls provide unchanged OMMs, cumulative matched-epoch statistics CSV, per-model epoch CSV (including gaps), issue provenance and a technical report. Dates are UTC; the client can be closed while Actions runs.

Use `--history <directory>` for isolated experiments. Production uses the default Git-tracked directory. No automatic history deletion is configured. Actions artifacts retain raw inputs and logs for 90 days, while committed history has no configured expiry. Repository size grows with repeated raw snapshots and forecast pairs; move to long-term object storage as scale warrants. GitHub scheduled starts are best effort. Actual future evidence must accumulate after deployment; no future RMS is invented to populate the dashboard.
