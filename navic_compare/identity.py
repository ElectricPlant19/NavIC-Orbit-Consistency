import numpy as np
from .rinex import select_ephemeris
from .orbits import broadcast_position, select_gp, propagate_gp

def match_identities(records, gps, times, config):
    """All-to-all geometric evidence at up to 3 separated valid physical epochs.

    No PRN/name numbering assumptions. Ambiguous or duplicate assignments fail closed.
    """
    matches = []
    norads = sorted({g.norad for g in gps})
    for prn in sorted({e.prn for e in records}):
        group = [e for e in records if e.prn==prn]
        available = []
        for i in range(0,len(times),max(1,len(times)//24)):
            e, _ = select_ephemeris(group,times[i],config["broadcast_max_age_seconds"])
            if e: available.append((times[i],e))
        candidates = []
        for norad in norads:
            elements = [g for g in gps if g.norad==norad]
            evidence = []
            usable = [(time,e) for time,e in available if select_gp(elements,time,config["gp_max_age_hours"],config["gp_allow_future"])[0]]
            selected = [usable[i] for i in sorted(set([0,len(usable)//2,len(usable)-1]))] if usable else []
            for time,e in selected:
                g,_ = select_gp(elements,time,config["gp_max_age_hours"],config["gp_allow_future"])
                if not g: continue
                try:
                    _,p = propagate_gp(g,time)
                    separation = float(np.linalg.norm(p-broadcast_position(e,time)))
                    evidence.append({"utc":time.utc.isot+"Z","separation_km":separation,
                                     "gp_element_id":g.element_id,"gp_age_hours":float((time-g.epoch).sec/3600),"name":g.name})
                except ValueError: continue
            if evidence:
                candidates.append({"norad_id":norad,"max_test_km":max(x["separation_km"] for x in evidence),
                                   "test_epochs":evidence})
        candidates.sort(key=lambda c:c["max_test_km"])
        best = candidates[0] if candidates else None
        margin = candidates[1]["max_test_km"]-best["max_test_km"] if len(candidates)>1 else None
        confirmed = bool(best and len(best["test_epochs"])>=2 and best["max_test_km"]<=config["identity_max_km"]
                         and (margin is None or margin>=config["identity_margin_km"]))
        inclination = float(np.median([abs(np.degrees(e.values[12])) for e in group]))
        matches.append({"prn":prn,"norad_id":best["norad_id"] if confirmed else None,
                        "name":best["test_epochs"][0]["name"] if confirmed else "Unconfirmed identity",
                        "orbit_class":"GEO" if inclination<config["geo_inclination_limit_deg"] else "IGSO",
                        "inclination_deg":inclination,"confirmed":confirmed,"margin_km":margin,
                        "candidates":candidates,"method":"all-to-all geometric confirmation; no numbering assumptions"})
    ids = [m["norad_id"] for m in matches if m["confirmed"]]
    for m in matches:
        if m["confirmed"] and ids.count(m["norad_id"])>1:
            m.update(confirmed=False,norad_id=None,name="Ambiguous duplicate assignment")
    return matches
