import html

def technical_report(run):
    f = run["fleet"]
    fmt = lambda x: "—" if x is None else f"{x:.3f}"
    table = "\n".join(f"| {s['prn']} | {s['norad_id'] or 'unconfirmed'} | {s['name']} | {s['orbit_class']} | {s['valid_epochs']}/{s['total_epochs']} | {fmt(s['rms_km'])} | {fmt(s['mean_km'])} | {fmt(s['max_km'])} | {s['max_utc'] or '—'} | {s['status']} |" for s in run["satellites"])
    return f"""# NavIC orbit consistency assessment

Run `{run['run_id']}` · UTC date {run['day']} · schema {run['schema_version']}

## Findings

{f['satellites_present']} satellites present in supported RINEX records; {f['satellites_compared']} compared.
Mean satellite RMS: {fmt(f['mean_satellite_rms_km'])} km. Worst RMS: {f['worst_satellite'] or 'none'}.
{f['review_count']} satellites require review. Missing/invalid epochs remain gaps and do not enter residual statistics.

| PRN | NORAD | Name | Orbit | Paired/total | RMS km | Mean km | Max km | Time of max UTC | Status |
|---|---|---|---|---|---|---|---|---|---|
{table}

## Interpretation

This compares two independent trajectories. Neither is truth. Broadcast ephemerides describe a navigation-message orbit; GP elements are fitted SGP4 mean elements. A separation is a disagreement, not an SGP4 accuracy measurement. Threshold status is computed from residuals and data quality. Threshold calibration: **{run['config']['threshold_calibration']}**. No operational accuracy claim follows from Close.

## Method and time systems

One UTC day is sampled every {run['config']['step_seconds']} SI seconds on a TAI-backed Astropy timeline, including leap-second days. RINEX IRN calendar times use the nominal GPS=IRN=TAI−19 relationship (RINEX 4.02 §4.1.6–7). The pinned leap-second table supplies UTC conversion. IRUT fractional polynomial corrections are applied when provided in a RINEX 3 header. Missing fractional corrections, or unsupported RINEX4 STO messages, are reported; nominal sub-microsecond alignment is assumed. GP epochs are UTC. Both sources are evaluated at the same Time object, not matched by textual clock tags. Epoch clock corrections are not subtracted from coordinate time.

Broadcast LNAV uses the ISRO SPS ICD v1.1 Appendix A Kepler solution and harmonic corrections in ECEF (km). Earth μ=3.986005e14 m³/s² and rotation=7.2921151467e−5 rad/s. Nearest toe within ±{run['config']['broadcast_max_age_seconds']} seconds is selected; unhealthy, reserved-IODEC and conflicting same-toe/IODEC records are rejected. No gap is filled by extrapolation. The window is an analysis policy based on nominal update cadence, **not a verified ICD fit-interval guarantee**: {run['config']['broadcast_window_basis']}

GP uses the pinned python-sgp4 implementation, WGS72, and automatic deep-space branch. The closest prior element epoch is selected by default, with a {run['config']['gp_max_age_hours']} h absolute age cap; future sets are disabled unless explicitly configured, then flagged. Every residual includes signed GP age, set epoch, snapshot hash and element ID. Retrieval time is recorded separately. Archived sets are required for retrospective runs; current CelesTrak data cannot reconstruct GP history.

TEME is transformed through Astropy's Vallado-compatible TEME→ITRS rotation (GMST82 using UT1 and polar motion), with pinned IERS EOP. EOP coverage is checked before propagation; predictions are recorded. ITRS is treated as broadcast ECEF at km scale. Residual sign is GP minus broadcast. Radial, along-track and cross-track axes come from the broadcast position and **inertial** velocity transformed to TEME. Using ECEF velocity would be ill-conditioned for GEO. Velocity is a centered one-second numerical derivative within the same ephemeris model.

Identity confirmation evaluates every candidate NORAD object at up to three separated test epochs, requires at least two successful epochs, ≤{run['config']['identity_max_km']} km worst test separation and ≥{run['config']['identity_margin_km']} km runner-up margin. Duplicate assignments fail closed. The full candidate matrix and test evidence are in identity.json. Geometry is a consistency check, not authoritative catalogue identification. Orbit classes use broadcast inclination with a {run['config']['geo_inclination_limit_deg']}° cutoff; individual elements and inclinations remain recorded.

## Flags and element age

RMS, maximum and residual-vector jump thresholds are configured per orbit class. A jump is evaluated only between contiguous paired epochs; it is a diagnostic and may indicate a maneuver, GP replacement or broadcast upload. GP/ephemeris changes are recorded separately. Epoch identity violations invalidate that epoch. Summary statistics exclude all gaps. GP-age bins and a descriptive linear fit are reported; mixed element sets, orbit changes and sparse sampling prevent causal attribution of the slope.

## Supporting data and reproducibility

manifest.json contains input SHA-256 hashes, retrieval metadata, full parameters, software versions, supporting EOP/leap-second versions, time assumptions and code hash. ephemerides.json preserves parsed fields, health, URA, toe and IODEC; epochs.csv/json contains the per-satellite dataset. A complete output file-hash manifest accompanies each immutable run directory. Retain the content-addressed raw archive; hashes alone do not recover unavailable upstream data.

## Validation and limitations

The test suite includes published Vallado SGP4 vectors, deep-space propagation, UTC/leap boundaries, a GEO analytical orbit, orthonormal RTN checks, acquisition fallback and gap handling. A GPS broadcast/SP3 validation command is provided. **An observational GPS/SP3 baseline has not been demonstrated unless validation.json explicitly records it.** NavIC results remain preliminary until that end-to-end check passes on real data. The fitted thresholds require representative baseline runs by orbit class.

Optional SP3 is interpolated locally without extrapolation and includes its declared time system. No NavIC SP3 coverage is presumed. SP3 and broadcast may refer to center of mass versus antenna phase center; this matters at metre scales. An SP3 disagreement does not automatically assign truth. Legacy LNAV records in RINEX 3/4 are supported. NavIC L1NV is excluded with notes; this implementation does not claim complete RINEX4 navigation-message support.

## Data quality notes

{chr(10).join('- '+n for n in run['notes']) or '- No additional notes.'}

## Primary references

- [ISRO IRNSS SPS ICD v1.1, 2017](https://www.isro.gov.in/media_isro/pdf/SateliteNavigation/irnss_sps_icd_version1.1-2017.pdf)
- [IGS RINEX 4.02](https://files.igs.org/pub/data/format/rinex_4.02.pdf)
- [Vallado et al., Revisiting Spacetrack Report #3](https://celestrak.org/publications/AIAA/2006-6753/)
- [CelesTrak GP formats](https://celestrak.org/NORAD/documentation/gp-data-formats.php) and [usage policy](https://celestrak.org/usage-policy.php)
- [Astropy satellite coordinate guide](https://docs.astropy.org/en/stable/coordinates/satellites.html)
"""
