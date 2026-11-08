from collections import Counter
import numpy as np

def summarize(rows, identities, config):
    summaries = []
    for identity in identities:
        group = [r for r in rows if r["prn"]==identity["prn"]]
        valid = [r for r in group if r["separation_km"] is not None]
        values = np.array([r["separation_km"] for r in valid])
        flags = Counter(f for r in group for f in r["flags"])
        thresholds = config["thresholds"][identity["orbit_class"]]
        rms = float(np.sqrt(np.mean(values**2))) if len(values) else None
        maximum = float(values.max()) if len(values) else None
        reasons = sorted(set(flags)-{"gp_set_change","ephemeris_change"})
        if rms is not None and rms>thresholds["rms_km"]: reasons.append("rms_threshold")
        if maximum is not None and maximum>thresholds["max_km"]: reasons.append("maximum_threshold")
        if len(valid)<len(group): reasons.append("incomplete_coverage")
        if not identity["confirmed"]: reasons.append("identity_unconfirmed")
        age = np.array([r["gp_age_hours"] for r in valid])
        age_trend = None
        if len(age)>2 and np.ptp(age)>1e-6:
            slope,intercept = np.polyfit(age,values,1)
            age_trend = {"slope_km_per_hour":float(slope),"intercept_km":float(intercept),
                         "note":"descriptive across selected sets; not causal"}
        bins = []
        for lo,hi in [(0,6),(6,12),(12,24),(24,48),(48,96)]:
            subset = values[(age>=lo)&(age<hi)]
            if len(subset): bins.append({"age_lo_hours":lo,"age_hi_hours":hi,"n":len(subset),
                                        "rms_km":float(np.sqrt(np.mean(subset**2)))})
        maxrow = max(valid,key=lambda r:r["separation_km"]) if valid else None
        summaries.append({**identity,"valid_epochs":len(valid),"total_epochs":len(group),
                          "coverage_percent":100*len(valid)/len(group) if group else 0,
                          "rms_km":rms,"mean_km":float(values.mean()) if len(values) else None,
                          "max_km":maximum,"max_utc":maxrow["utc"] if maxrow else None,
                          "rtn_rms_km":[float(np.sqrt(np.mean([r[k]**2 for r in valid]))) for k in ("radial_km","along_km","cross_km")] if valid else None,
                          "max_gp_age_hours":float(max(age)) if valid else None,
                          "age_trend":age_trend,"age_bins":bins,"thresholds":thresholds,
                          "status":"Review" if reasons or not valid else "Close",
                          "reasons":sorted(set(reasons)),"flag_counts":dict(flags)})
    comparable = [s for s in summaries if s["rms_km"] is not None]
    return summaries,{"satellites_present":len(summaries),"satellites_compared":len(comparable),
                      "valid_epochs":sum(s["valid_epochs"] for s in summaries),
                      "mean_satellite_rms_km":float(np.mean([s["rms_km"] for s in comparable])) if comparable else None,
                      "worst_satellite":max(comparable,key=lambda s:s["rms_km"])["prn"] if comparable else None,
                      "review_count":sum(s["status"]=="Review" for s in summaries)}
