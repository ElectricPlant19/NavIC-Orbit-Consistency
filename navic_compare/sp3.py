"""Optional SP3 position reference, strict time scale and interpolation bounds."""
from pathlib import Path
import gzip
import numpy as np
from astropy.time import Time
from .timeframes import system_time

def read_sp3(path):
    raw = Path(path).read_bytes()
    if raw[:2] == b"\x1f\x8b": raw = gzip.decompress(raw)
    lines = raw.decode("ascii").splitlines()
    time_system = next((l[9:12].strip() for l in lines if l.startswith("%c") and l[9:12].strip() in ("GPS","UTC","GAL","TAI")), None)
    if time_system not in ("GPS","UTC","GAL","TAI"): raise ValueError("SP3 time system missing or unsupported")
    data, epoch = {}, None
    for line in lines:
        if line.startswith("* "):
            y,m,d,h,mi = map(int,line[3:].split()[:5]); s = float(line[3:].split()[5])
            text = f"{y:04}-{m:02}-{d:02}T{h:02}:{mi:02}:{s:09.6f}"
            epoch = system_time(text) if time_system in ("GPS","GAL") else Time(text,scale=time_system.lower())
        elif line.startswith("P") and epoch is not None:
            xyz = [float(line[4+14*i:18+14*i]) for i in range(3)]
            if max(abs(x) for x in xyz)>=999999 or np.linalg.norm(xyz)<1: continue
            data.setdefault(line[1:4],[]).append((float(epoch.gps),xyz))
    return data,{"time_system":time_system,"satellites":sorted(data)}

def interpolate_sp3(entries,time):
    if len(entries)<4: return None
    x = np.array([p[0] for p in entries]); t = float(time.gps)
    if t<x.min() or t>x.max(): return None
    nearest = np.argsort(abs(x-t))[:8]; nearest.sort()
    xx = x[nearest]-t; yy = np.array([entries[i][1] for i in nearest])
    if np.max(np.diff(x[nearest]))>1800: return None
    if np.any(abs(xx)<1e-6): return yy[np.argmin(abs(xx))]
    # Lagrange interpolation about target; local abscissae avoid large GPS-second powers.
    weights = np.array([np.prod(-np.delete(xx,i)/(xx[i]-np.delete(xx,i))) for i in range(len(xx))])
    return weights@yy
