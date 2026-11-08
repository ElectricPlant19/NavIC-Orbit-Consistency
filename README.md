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

The daily job commits the validated dataset under `dashboard/dist/data` to this repository's main branch. The private Sites dashboard reads that **public repository's** data feed on load and every 30 minutes, checking SHA-256 digests to reject partially cached updates. It falls back to its bundled first-run snapshot if the feed is unavailable. The repository is public, so this does not require a token or expose a private credential. Change `dashboard/dist/feed.json` if moving the repository. CI needs `contents: write` for dataset publication; normal branch protection still applies. The first genuine GP snapshot and its retrieval time seed empty CI archives, including the rate guard. No deployment credentials are embedded in Actions.

Failures produce a nonzero exit code, `data/pipeline.log` and `data/alert.json`. Missing/Review satellites also produce structured alerts. Optionally set the repository secret `NAVIC_ALERT_WEBHOOK` to an explicitly chosen endpoint; no recipient is assumed or contacted without configuration. GitHub's workflow-failure notifications remain available. Same-day hourly navigation acquisition is not enabled.

## References

[ISRO SPS ICD v1.1](https://www.isro.gov.in/media_isro/pdf/SateliteNavigation/irnss_sps_icd_version1.1-2017.pdf), [IGS RINEX 4.02](https://files.igs.org/pub/data/format/rinex_4.02.pdf), [Vallado SGP4 reference](https://celestrak.org/publications/AIAA/2006-6753/), [CelesTrak GP documentation](https://celestrak.org/NORAD/documentation/gp-data-formats.php), [usage policy](https://celestrak.org/usage-policy.php), [Astropy frame guide](https://docs.astropy.org/en/stable/coordinates/satellites.html).

I11 is explicitly catalogued as **NVS-03 (IRNSS-1L), NORAD 101228**, following the user-supplied mapping on 8 November 2026. Catalogue identity is preserved even when geometric confirmation fails. The first archived GP is from 5 November and does not pass the geometric gate against the 7 November broadcast trajectory; I11 remains Review, with no accepted residuals. No name or launch numbering inference overrides that declared mapping.

The genuine GPS GP snapshot and SP3 file used for the baseline are preserved byte-for-byte under validation/inputs/. Their content hashes match validation/gps-2026-11-07.json; the broadcast, EOP and leap inputs are shared with the archived NavIC run.
