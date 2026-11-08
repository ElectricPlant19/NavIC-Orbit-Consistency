"""Fixed-column RINEX 3.x/4.x LNAV reader. Other records remain visible as notes."""
from dataclasses import dataclass, asdict
import gzip
import re
import math
from pathlib import Path
import numpy as np
from .timeframes import system_time, toe_time

@dataclass
class Ephemeris:
    prn: str
    toc: object
    toe: object
    values: list
    clock: list
    message: str = "LNAV"
    source_line: int = 0

    def __post_init__(self):
        self.toe_gps = float(self.toe.gps)
        self.toc_gps = float(self.toc.gps)

    @property
    def iode(self): return int(self.values[0])
    @property
    def health(self): return int(self.values[21])
    @property
    def ura(self): return self.values[20]
    @property
    def key(self): return f"{self.prn}:{self.toe.gps:.0f}:{self.iode}"
    def metadata(self):
        from astropy.time import TimeDelta
        return {"prn": self.prn, "toc_irn": (self.toc-TimeDelta(19,format="sec")).tai.isot, "toc_utc": self.toc.utc.isot,
                "toe_utc": self.toe.utc.isot, "toe_sow": self.values[8], "iodec": self.iode,
                "health": self.health, "ura_m": self.ura, "parameters": self.values,
                "clock": self.clock, "time_system": "IRN" if self.prn[0] == "I" else "GPS",
                "message": self.message, "source_line": self.source_line}

def fields(line, start, count):
    return [float(line[start + 19*i:start + 19*(i+1)].strip().replace("D", "E").replace("d", "e"))
            if line[start + 19*i:start + 19*(i+1)].strip() else float("nan") for i in range(count)]

def read_rinex(path, systems="IG"):
    path = Path(path)
    raw = path.read_bytes()
    if path.suffix == ".gz" or raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)  # Also validates CRC and complete trailer.
    lines = raw.decode("ascii").splitlines()
    if not lines or "RINEX VERSION / TYPE" not in lines[0]:
        raise ValueError("Not a RINEX navigation file")
    version = float(lines[0][:9])
    if not 3 <= version < 5 or lines[0][20:21] != "N":
        raise ValueError("Expected a RINEX 3.x/4.x navigation file")
    end = next((i for i,l in enumerate(lines) if l[60:].strip() == "END OF HEADER"), None)
    if end is None: raise ValueError("RINEX header has no END OF HEADER")
    notes, corrections, leap = [], {}, None
    for line in lines[:end]:
        if line[60:].strip() == "TIME SYSTEM CORR":
            # 4-character type, 17/16/7/5 character numeric fields.
            corrections[line[:4]] = [float(line[5:22].replace("D", "E")), float(line[22:38].replace("D", "E")),
                                     int(line[38:45]), int(line[45:50])]
        if line[60:].strip() == "LEAP SECONDS": leap = int(line[:6])
    records = []
    k = end + 1
    message = "LNAV"
    while k < len(lines):
        line = lines[k]
        if line.startswith(">"):
            parts = line.split()
            kind = parts[1] if len(parts)>1 else ""
            message = parts[3] if len(parts)>3 else ""
            if kind != "EPH":
                if kind == "STO" and len(parts)>2 and parts[2].startswith("I"):
                    notes.append("RINEX4 IRN STO present; fractional offset not applied (nominal IRN=GPS assumption)")
                k += 1
                while k < len(lines) and not lines[k].startswith(">"): k += 1
                continue
            if len(parts)>2 and parts[2][0] in systems and message != "LNAV":
                notes.append(f"Unsupported {parts[2]} {message}; excluded, not parsed as LNAV")
            if message != "LNAV":
                k += 1
                while k < len(lines) and not lines[k].startswith(">"): k += 1
                continue
            k += 1
            continue
        if not re.match(r"^[A-Z]\d{2} ", line): k += 1; continue
        prn = line[:3]
        count = 4 if prn[0] in "RS" else 8
        if prn[0] in systems:
            if k + 8 > len(lines): raise ValueError(f"Truncated record at line {k+1}")
            if any(not x.startswith("    ") for x in lines[k+1:k+8]):
                raise ValueError(f"Invalid continuation at line {k+1}")
            text = line[4:23].split()
            y, mo, d, h, mi = map(int, text[:5]); sec = float(text[5])
            calendar = f"{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{sec:06.3f}"
            toc = system_time(calendar, corrections.get("IRUT") if prn[0] == "I" else None)
            vals = sum([fields(x, 4, 4) for x in lines[k+1:k+8]], [])
            if not all(math.isfinite(vals[j]) for j in list(range(17)) + [20,21]):
                raise ValueError(f"Missing required orbit fields at line {k+1}")
            if not 0 <= vals[5] < 1 or vals[7] <= 0 or not 0 <= vals[8] < 604800:
                raise ValueError(f"Invalid orbit geometry at line {k+1}")
            if vals[0] != int(vals[0]) or vals[21] != int(vals[21]):
                raise ValueError("Noninteger issue or health")
            toe = toe_time(toc, vals[8])
            if math.isfinite(vals[18]) and abs(float(toe.gps)-(vals[18]*604800+vals[8]))>1:
                raise ValueError(f"RINEX week/toe disagrees with calendar toc at line {k+1}")
            # Apply same fractional system-time correction to toe.
            if prn[0] == "I" and "IRUT" in corrections:
                nominal_toc = system_time(calendar)
                from astropy.time import TimeDelta
                toe += TimeDelta((toc - nominal_toc).sec, format="sec")
            records.append(Ephemeris(prn, toc, toe, vals, fields(line,23,3), message, k+1))
        k += count
    if not any(e.prn[0] == "I" for e in records):
        raise ValueError("File has no supported nonempty NavIC I LNAV records")
    return records, {"version": version, "leap_seconds": leap, "time_corrections": corrections,
                     "notes": sorted(set(notes)), "satellites_present": sorted({e.prn for e in records if e.prn[0]=="I"})}

def valid_issue(e):
    if e.prn[0] == "G": return 0 <= e.iode <= 255
    return 0 <= e.iode <= 29 or 76 <= e.iode <= 255

def select_ephemeris(records, time, max_age):
    gps = float(time.gps)
    nearby = [e for e in records if abs(gps - e.toe_gps) <= max_age + 1e-6]
    if not nearby: return None, ["broadcast_gap"]
    # Evaluate nearest issue first: never hide a health warning with an older healthy issue.
    nearby.sort(key=lambda e: (abs(gps-e.toe_gps), -e.toc_gps))
    e = nearby[0]
    if e.health != 0: return None, ["broadcast_unhealthy"]
    if e.ura >= 8192: return None, ["broadcast_ura_unavailable"]
    if not valid_issue(e): return None, ["iodec_reserved"]
    if e.prn[0] == "G" and math.isfinite(e.values[23]) and (int(e.values[23]) & 255) != e.iode:
        return None, ["iode_iodc_inconsistent"]
    peers = [x for x in nearby if abs(x.toe_gps-e.toe_gps) < 1e-6 and x.iode == e.iode]
    if any(not np.allclose(x.values[:17]+x.clock, e.values[:17]+e.clock, rtol=0, atol=1e-10) for x in peers):
        return None, ["iodec_conflict"]
    return e, []
