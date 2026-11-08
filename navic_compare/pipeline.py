import csv
import hashlib
import json
import platform
import shutil
from pathlib import Path
from importlib.metadata import version
from datetime import datetime,timezone
import numpy as np
from astropy import units as u
from . import __version__
from .acquire import atomic_json
from .rinex import read_rinex,select_ephemeris
from .timeframes import utc_grid,pinned_orientation,check_eop
from .orbits import parse_gp,select_gp,propagate_gp,broadcast_position,rtn_residual
from .identity import match_identities
from .analysis import summarize
from .report import technical_report
from .sp3 import read_sp3,interpolate_sp3
from .fitting import generate_models

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def clean(value):
    if isinstance(value,dict): return {k:clean(v) for k,v in value.items()}
    if isinstance(value,list): return [clean(x) for x in value]
    if isinstance(value,(np.floating,float)) and not np.isfinite(value): return None
    if isinstance(value,np.generic): return value.item()
    return value

def local_inputs(rinex,gps,eop,leaps,sp3=None):
    def meta(p): return {"path":str(Path(p).resolve()),"sha256":sha(p),"source":"user-supplied local file","retrieved_at":None}
    result = {"rinex":meta(rinex),"gp":[meta(p) for p in gps],"eop":meta(eop),"leaps":meta(leaps)}
    if sp3: result["sp3"] = meta(sp3)
    return result

def run_comparison(day,config,inputs,output="results",dashboard="dashboard/dist",system="I"):
    software = {"python":platform.python_version(),"pipeline":__version__,
                **{name:version(name) for name in ("numpy","astropy","pyerfa","sgp4","requests","scipy")}}
    code_hash = hashlib.sha256(b"".join(p.read_bytes() for p in sorted(Path(__file__).parent.glob("*.py")))).hexdigest()
    fingerprint = hashlib.sha256(json.dumps({"day":str(day),"config":config,"hashes":{k:[r['sha256'] for r in v] if isinstance(v,list) else v['sha256'] for k,v in inputs.items() if k!='acquisition_attempts'},"code":code_hash,"software":software,"system":system},sort_keys=True).encode()).hexdigest()[:12]
    run_id = f"{day}-{system}-{fingerprint}"
    target = Path(output)/run_id
    if target.exists():
        # Verify immutable outputs before reuse.
        expected = json.loads((target/"checksums.json").read_text())
        if any(sha(target/name)!=digest for name,digest in expected.items()): raise ValueError("Existing run output checksum mismatch")
        publish_dashboard(target,dashboard)
        return json.loads((target/"summary.json").read_text())
    staging = Path(output)/(run_id+".partial")
    if staging.exists(): raise ValueError(f"Incomplete run exists: {staging}; inspect or choose a different output directory")
    records,header = read_rinex(inputs["rinex"]["path"])
    records = [e for e in records if e.prn[0]==system]
    if not records: raise ValueError(f"No {system} records available")
    gp = sum([parse_gp(item["path"]) for item in inputs["gp"]],[])
    gp = list({(g.norad,g.element_id):g for g in gp}.values())
    notes = list(header["notes"])
    if "IRUT" not in header["time_corrections"]: notes.append("IRUT fractional time correction unavailable: nominal IRN=GPS assumed")
    notes.append("Thresholds are "+config["threshold_calibration"])
    validation = json.loads(Path(inputs["gps_validation"]["path"]).read_text()) if "gps_validation" in inputs else {"gps_sp3_baseline":"not run","pass":False}
    notes.append(f"GPS/SP3 diagnostic passed: {validation['broadcast_sp3_rms_m']:.3f} m RMS on {validation['paired_epochs']} paired epochs" if validation.get("pass") else "Observational GPS/SP3 validation pending; do not interpret residuals as validated accuracy")
    sp3,sp3_meta = read_sp3(inputs["sp3"]["path"]) if "sp3" in inputs else ({},None)
    with pinned_orientation(inputs["eop"]["path"],inputs["leaps"]["path"]) as eop:
        times = utc_grid(day,config["step_seconds"])
        from astropy.utils import iers
        leaps = iers.LeapSeconds.open(inputs["leaps"]["path"])
        if leaps.expires < times[-1]: raise ValueError("Leap-second table expires before the comparison window")
        orientation = check_eop(times,eop)
        if orientation["prediction_used"]: notes.append("IERS predicted EOP values used for part of this window")
        # Validate RINEX integer leap count against the pinned table at midpoint.
        mid = times[len(times)//2]
        leap_offset = int(round((mid.tai.to_datetime()-mid.utc.to_datetime()).total_seconds()-19))
        if header["leap_seconds"] is not None and header["leap_seconds"] != leap_offset:
            raise ValueError("RINEX LEAP SECONDS conflicts with pinned leap table at comparison date")
        identities = match_identities(records,gp,times,config)
        for identity in identities:
            if identity.get('catalogue_identity') and not identity['confirmed']:
                notes.append(f"{identity['prn']} catalogue identity is {identity['name']} / NORAD {identity['norad_id']} (declared); geometric confirmation failed or lacked evidence, so no residual is accepted")
        rows = []
        for identity in identities:
            prn = identity["prn"]
            group = [e for e in records if e.prn==prn]
            elements = [g for g in gp if g.norad==identity["norad_id"]]
            satrows = []
            batches = {}
            for i,time in enumerate(times):
                e,flags = select_ephemeris(group,time,config["broadcast_max_age_seconds"])
                g,gflags = select_gp(elements,time,config["gp_max_age_hours"],config["gp_allow_future"])
                epoch_gps = float(time.gps)
                emeta = e or min(group,key=lambda x:abs(epoch_gps-x.toe_gps))
                gmeta = g or select_gp(elements,time,1e12,config["gp_allow_future"])[0]
                if not identity["confirmed"]: flags.append("identity_geometry_unconfirmed" if identity.get('catalogue_identity') else "identity_unconfirmed")
                flags += gflags
                row = {"prn":prn,"norad_id":identity["norad_id"],"name":identity["name"],"orbit_class":identity["orbit_class"],
                       "utc":time.utc.isot+"Z","tai_jd1":float(time.tai.jd1),"tai_jd2":float(time.tai.jd2),
                       "separation_km":None,"radial_km":None,"along_km":None,"cross_km":None,
                       "gp_age_hours":float((time-gmeta.epoch).to_value(u.hour)) if gmeta else None,
                       "gp_epoch_utc":gmeta.epoch.utc.isot+"Z" if gmeta else None,"gp_snapshot_sha256":gmeta.snapshot if gmeta else None,
                       "gp_element_id":gmeta.element_id if gmeta else None,"sgp4_branch":gmeta.sat.method if gmeta else None,
                       "toe_age_seconds":float((time-emeta.toe).sec),
                       "iodec":emeta.iode,"health":emeta.health,"ura_m":emeta.ura,
                       "ephemeris_key":emeta.key,"broadcast_x_km":None,"broadcast_y_km":None,"broadcast_z_km":None,
                       "gp_x_km":None,"gp_y_km":None,"gp_z_km":None,"sp3_broadcast_km":None,"sp3_gp_km":None,"flags":flags}
                satrows.append(row)
                if e and g and identity["confirmed"]:
                    batches.setdefault((e.key,g.element_id),(e,g,[]))[2].append(i)
            for e,g,indices in batches.values():
                tt = times[indices]
                try:
                    teme,p = propagate_gp(g,tt)
                    b = broadcast_position(e,tt)
                    rtn = rtn_residual(e,tt,teme)
                except ValueError as exc:
                    for i in indices: satrows[i]["flags"].append("propagation_failure")
                    notes.append(f"{prn}: {exc}"); continue
                for k,i in enumerate(indices):
                    row = satrows[i]
                    sep = float(np.linalg.norm(p[k]-b[k]))
                    if sep>config["identity_max_km"]:
                        row["flags"].append("identity_geometry_inconsistent"); continue
                    row.update(separation_km=sep,radial_km=float(rtn[k,0]),along_km=float(rtn[k,1]),cross_km=float(rtn[k,2]))
                    for axis,j in zip("xyz",range(3)):
                        row[f"broadcast_{axis}_km"] = float(b[k,j]); row[f"gp_{axis}_km"] = float(p[k,j])
                    if sep>config["thresholds"][identity["orbit_class"]]["max_km"]: row["flags"].append("separation_threshold")
                    if prn in sp3:
                        reference = interpolate_sp3(sp3[prn],times[i])
                        if reference is not None:
                            row.update(sp3_broadcast_km=float(np.linalg.norm(b[k]-reference)),sp3_gp_km=float(np.linalg.norm(p[k]-reference)))
            previous = None
            for row in satrows:
                if row["separation_km"] is None: previous=None; continue
                if previous:
                    if row["gp_element_id"] != previous["gp_element_id"]: row["flags"].append("gp_set_change")
                    if row["ephemeris_key"] != previous["ephemeris_key"]: row["flags"].append("ephemeris_change")
                    delta = np.array([row[f"gp_{a}_km"]-row[f"broadcast_{a}_km"] for a in "xyz"])
                    prevdelta = np.array([previous[f"gp_{a}_km"]-previous[f"broadcast_{a}_km"] for a in "xyz"])
                    row["jump_km"] = float(np.linalg.norm(delta-prevdelta))
                    if row["jump_km"]>config["thresholds"][identity["orbit_class"]]["jump_km"]: row["flags"].append("discontinuity")
                previous=row
            rows.extend(satrows)
        summaries,fleet = summarize(rows,identities,config)
        generator,generated_omm,fitted_rows = generate_models(records,identities,gp,times,config) if system=='I' else ({'enabled':False},[],[])
        if generator.get('enabled'):
            generator.update(input_hashes={key:inputs[key]['sha256'] for key in ('rinex','eop','leaps')},
                             code_sha256=code_hash,software=software)
        eop_rows = {"mjd":times.utc.mjd.tolist(),"ut1_minus_utc_s":eop.ut1_utc(times).to_value(u.s).tolist(),
                    "polar_x_arcsec":eop.pm_xy(times)[0].to_value(u.arcsec).tolist(),"polar_y_arcsec":eop.pm_xy(times)[1].to_value(u.arcsec).tolist()}
    manifest = {"inputs":inputs,"config":config,"code_sha256":code_hash,"orientation":orientation,"rinex_header":header,
                "sp3":sp3_meta,"software":software}
    run = clean({"schema_version":"1.0.0","run_id":run_id,"day":str(day),"generated_at":datetime.now(timezone.utc).isoformat(),
                 "kind":"observed","assessment":"consistency, not accuracy","config":config,"fleet":fleet,
                 "satellites":summaries,"notes":sorted(set(notes)),"manifest":manifest,"validation":validation,
                 "generator":generator})
    staging.mkdir(parents=True)
    atomic_json(staging/"manifest.json",clean(manifest))
    atomic_json(staging/"summary.json",run)
    atomic_json(staging/"identity.json",clean(identities))
    atomic_json(staging/"ephemerides.json",clean([e.metadata() for e in records]))
    atomic_json(staging/"eop_used.json",eop_rows)
    atomic_json(staging/"epochs.json",clean(rows))
    atomic_json(staging/"fit_summary.json",clean(generator))
    atomic_json(staging/"generated.omm.json",clean(generated_omm))
    atomic_json(staging/"fitted_epochs.json",clean(fitted_rows))
    if fitted_rows:
        with (staging/"fitted_epochs.csv").open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(fitted_rows[0]));writer.writeheader()
            for row in fitted_rows: writer.writerow({**row,'flags':';'.join(row['flags'])})
    keys = sorted(set().union(*(r.keys() for r in rows)))
    with (staging/"epochs.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
        for row in rows: writer.writerow({**row,"flags":";".join(row["flags"])})
    (staging/"report.md").write_text(technical_report(run),encoding="utf-8")
    atomic_json(staging/"validation.json",{**validation,"thresholds_calibrated":False})
    atomic_json(staging/"checksums.json",{p.name:sha(p) for p in staging.iterdir() if p.is_file()})
    staging.rename(target)
    publish_dashboard(target,dashboard)
    return run

def publish_dashboard(target,dashboard):
    destination=Path(dashboard)/"data";destination.mkdir(parents=True,exist_ok=True)
    for name in ("summary.json","epochs.json","epochs.csv","report.md","identity.json","manifest.json","checksums.json","validation.json",
                 "fit_summary.json","generated.omm.json","fitted_epochs.json","fitted_epochs.csv"):
        if not (target/name).exists(): continue
        shutil.copy2(target/name,destination/name)
    atomic_json(destination/"latest.json",{"summary":"summary.json","epochs":"epochs.json",
                "summary_sha256":sha(destination/"summary.json"),"epochs_sha256":sha(destination/"epochs.json"),
                "artifacts":{name:sha(target/name) for name in ('generated.omm.json','fit_summary.json','fitted_epochs.json','fitted_epochs.csv') if (target/name).exists()}})
