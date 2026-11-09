# NavIC orbit consistency assessment

Run `2026-11-08-I-f809628ec73e` · UTC date 2026-11-08 · schema 1.0.0

## Findings

3 satellites present in supported RINEX records; 3 compared.
Mean satellite RMS: 3.156 km. Worst RMS: I02.
0 satellites require review. Missing/invalid epochs remain gaps and do not enter residual statistics.

| PRN | NORAD | Name | Orbit | Paired/total | RMS km | Mean km | Max km | Time of max UTC | Status |
|---|---|---|---|---|---|---|---|---|---|
| I02 | 39635 | IRNSS-1B | IGSO | 1440/1440 | 6.372 | 5.862 | 8.329 | 2026-11-08T01:07:00.000Z | Close |
| I09 | 43286 | IRNSS-1I | IGSO | 1440/1440 | 1.516 | 1.405 | 2.182 | 2026-11-08T16:47:00.000Z | Close |
| I10 | 56759 | NVS-01 (IRNSS-1J) | GEO | 1440/1440 | 1.579 | 1.374 | 2.895 | 2026-11-08T11:23:00.000Z | Close |

## Experimental broadcast-derived SGP4 generator

**2 accepted models; 1 rejected.** This independently generated NAVIC-BROADCAST-FIT product is not CelesTrak SupGP. It fits a model to broadcast trajectories; the broadcast-vs-CelesTrak comparison above remains separate.

| PRN | Fit RMS km | Held-out RMS km | Held-out max km | Export status | Reason |
|---|---|---|---|---|---|
| I02 | 0.9279 | 6.0826 | 8.0075 | Rejected | holdout_rms_gate |
| I09 | 0.5101 | 4.0144 | 5.7758 | Accepted | gates passed |
| I10 | 0.8826 | 4.0812 | 5.8932 | Accepted | gates passed |

Targets are sampled every 300 seconds. Training spans 2026-11-08T00:00:00.000Z through (excluding) 2026-11-08T18:00:00.000Z; held-out validation spans 2026-11-08T18:00:00.000Z through (excluding) 2026-11-09T00:00:00.000Z. Held-out epochs never enter the optimizer. Both arcs still share broadcast biases, and this retrospective test does not establish live forecast accuracy.

The optimizer varies six nonsingular prograde mean-element coordinates (mean longitude, eccentricity vector, inclination vector, log mean motion), evaluated through SGP4/SDP4 with WGS72. Initialization comes from a training-arc broadcast TEME position/velocity; existing GP data supply catalogue identifiers only. This is a numerical mean-element fit, not a direct reuse of osculating Kepler elements. BSTAR and mean-motion derivatives are fixed at zero. Training records with toc after the split are excluded. Invalid broadcast data remain gaps. The fitted elements are frozen before the later arc is evaluated.

Each exported OMM is reloaded through the standard parser and propagation-checked against the fitted object. Only converged, identifiable deep-space solutions with sufficient training and validation coverage and passing class-specific RMS/maximum gates enter **generated.omm.json**. Empty output means no accepted product; rejected candidates are reported in fit_summary.json. Fitted residuals, RTN components, partitions and gap flags are in fitted_epochs.csv/json. The element epoch and optimizer diagnostics are recorded per satellite. No use beyond the tested interval is established.

Threshold calibration: **provisional engineering gates; no absolute accuracy claim**. A low fit or held-out residual means close reproduction of the broadcast trajectory, not independently established absolute orbit accuracy.


## Interpretation

This compares two independent trajectories. Neither is truth. Broadcast ephemerides describe a navigation-message orbit; GP elements are fitted SGP4 mean elements. A separation is a disagreement, not an SGP4 accuracy measurement. Threshold status is computed from residuals and data quality. Threshold calibration: **provisional; baseline calibration required**. No operational accuracy claim follows from Close.

## Method and time systems

One UTC day is sampled every 60 SI seconds on a TAI-backed Astropy timeline, including leap-second days. RINEX IRN calendar times use the nominal GPS=IRN=TAI−19 relationship (RINEX 4.02 §4.1.6–7). The pinned leap-second table supplies UTC conversion. IRUT fractional polynomial corrections are applied when provided in a RINEX 3 header. Missing fractional corrections, or unsupported RINEX4 STO messages, are reported; nominal sub-microsecond alignment is assumed. GP epochs are UTC. Both sources are evaluated at the same Time object, not matched by textual clock tags. Epoch clock corrections are not subtracted from coordinate time.

Broadcast LNAV uses the ISRO SPS ICD v1.1 Appendix A Kepler solution and harmonic corrections in ECEF (km). Earth μ=3.986005e14 m³/s² and rotation=7.2921151467e−5 rad/s. Nearest toe within ±7200 seconds is selected; unhealthy, reserved-IODEC and conflicting same-toe/IODEC records are rejected. No gap is filled by extrapolation. The window is an analysis policy based on nominal update cadence, **not a verified ICD fit-interval guarantee**: Conservative analysis cutoff based on ISRO SPS ICD v1.1 section 6.2.1.3 nominal 2-hour update cadence; this is NOT an ICD fit-interval guarantee.

GP uses the pinned python-sgp4 implementation, WGS72, and automatic deep-space branch. The closest prior element epoch is selected by default, with a 48 h absolute age cap; future sets are disabled unless explicitly configured, then flagged. Every residual includes signed GP age, set epoch, snapshot hash and element ID. Retrieval time is recorded separately. Archived sets are required for retrospective runs; current CelesTrak data cannot reconstruct GP history.

TEME is transformed through Astropy's Vallado-compatible TEME→ITRS rotation (GMST82 using UT1 and polar motion), with pinned IERS EOP. EOP coverage is checked before propagation; predictions are recorded. ITRS is treated as broadcast ECEF at km scale. Residual sign is GP minus broadcast. Radial, along-track and cross-track axes come from the broadcast position and **inertial** velocity transformed to TEME. Using ECEF velocity would be ill-conditioned for GEO. Velocity is a centered one-second numerical derivative within the same ephemeris model.

Identity confirmation evaluates every candidate NORAD object at up to three separated test epochs, requires at least two successful epochs, ≤50 km worst test separation and ≥500 km runner-up margin. Duplicate assignments fail closed. The full candidate matrix and test evidence are in identity.json. Geometry is a consistency check, not authoritative catalogue identification. Orbit classes use broadcast inclination with a 5° cutoff; individual elements and inclinations remain recorded.

## Flags and element age

RMS, maximum and residual-vector jump thresholds are configured per orbit class. A jump is evaluated only between contiguous paired epochs; it is a diagnostic and may indicate a maneuver, GP replacement or broadcast upload. GP/ephemeris changes are recorded separately. Epoch identity violations invalidate that epoch. Summary statistics exclude all gaps. GP-age bins and a descriptive linear fit are reported; mixed element sets, orbit changes and sparse sampling prevent causal attribution of the slope.

## Supporting data and reproducibility

manifest.json contains input SHA-256 hashes, retrieval metadata, full parameters, software versions, supporting EOP/leap-second versions, time assumptions and code hash. ephemerides.json preserves parsed fields, health, URA, toe and IODEC; epochs.csv/json contains the per-satellite dataset. A complete output file-hash manifest accompanies each immutable run directory. Retain the content-addressed raw archive; hashes alone do not recover unavailable upstream data.

## Validation and limitations

The test suite includes published Vallado SGP4 vectors, deep-space propagation, UTC/leap boundaries, a GEO analytical orbit, orthonormal RTN checks, acquisition fallback and gap handling. A GPS broadcast/SP3 validation command is provided. An observational GPS/SP3 diagnostic passed with 1.889 m broadcast/SP3 RMS over 19,370 paired epochs on 2026-11-07. Its provenance and GP baseline are recorded in validation.json. The SP3 was an IGS ultra-rapid product containing observed/predicted arcs; antenna/COM reference-point corrections were not applied. This checks the processing chain without establishing NavIC orbit accuracy. The thresholds still require representative baseline runs by orbit class.

Optional SP3 is interpolated locally without extrapolation and includes its declared time system. No NavIC SP3 coverage is presumed. SP3 and broadcast may refer to center of mass versus antenna phase center; this matters at metre scales. An SP3 disagreement does not automatically assign truth. Legacy LNAV records in RINEX 3/4 are supported. NavIC L1NV is excluded with notes; this implementation does not claim complete RINEX4 navigation-message support.

## Data quality notes

- GPS/SP3 diagnostic passed: 1.889 m RMS on 19370 paired epochs
- IERS predicted EOP values used for part of this window
- Thresholds are provisional; baseline calibration required

## Primary references

- [ISRO IRNSS SPS ICD v1.1, 2017](https://www.isro.gov.in/media_isro/pdf/SateliteNavigation/irnss_sps_icd_version1.1-2017.pdf)
- [IGS RINEX 4.02](https://files.igs.org/pub/data/format/rinex_4.02.pdf)
- [Vallado et al., Revisiting Spacetrack Report #3](https://celestrak.org/publications/AIAA/2006-6753/)
- [CelesTrak GP formats](https://celestrak.org/NORAD/documentation/gp-data-formats.php) and [usage policy](https://celestrak.org/usage-policy.php)
- [Astropy satellite coordinate guide](https://docs.astropy.org/en/stable/coordinates/satellites.html)
