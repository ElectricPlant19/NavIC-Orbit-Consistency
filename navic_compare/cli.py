import argparse
import json
import logging
import os
from pathlib import Path
from datetime import date,datetime,timedelta,timezone
import requests
from .acquire import acquire,Archive,atomic_json
from .pipeline import run_comparison,local_inputs
from .orbits import parse_gp

def alert(payload):
    """Optional explicitly configured endpoint. No recipients or channels are assumed."""
    url=os.environ.get("NAVIC_ALERT_WEBHOOK")
    if url:
        response=requests.post(url,json=payload,timeout=20)
        response.raise_for_status()

def main(argv=None):
    parser=argparse.ArgumentParser(description="NavIC trajectory consistency; neither source is truth")
    parser.add_argument("command",choices=["daily","compare","poll-gp","validate-gps","fit","fresh","track"])
    parser.add_argument("--date",default=None,help="UTC comparison day; daily defaults to yesterday UTC")
    parser.add_argument("--config",default="config/default.json")
    parser.add_argument("--data",default="data")
    parser.add_argument("--output",default="results")
    parser.add_argument("--dashboard",default="dashboard/dist")
    parser.add_argument('--history',default='history/prospective',help='Durable prospective model and scoring archive')
    parser.add_argument("--rinex")
    parser.add_argument("--gp",action="append",help="Repeat for all archived GP snapshots")
    parser.add_argument("--eop")
    parser.add_argument("--leaps")
    parser.add_argument("--sp3")
    parser.add_argument("--gps-validation",help="Previously generated observational GPS/SP3 baseline evidence")
    parser.add_argument('--acquire-only',action='store_true',help='Fresh mode: collect and assess current files without the retrospective benchmark')
    args=parser.parse_args(argv)
    Path(args.data).mkdir(parents=True,exist_ok=True)
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(),logging.FileHandler(Path(args.data)/"pipeline.log",encoding="utf-8")])
    config=json.loads(Path(args.config).read_text())
    day=date.fromisoformat(args.date) if args.date else datetime.now(timezone.utc).date()-timedelta(days=1)
    try:
        if args.command=='track':
            from .prospective import run_tracking
            summary=run_tracking(config,args.data,args.history,args.dashboard)
            logging.info('Prospective archive: %d issued models, %d scored forecast epochs',summary['issue_count'],summary['fleet']['recorded_epochs'])
            review=[i for i in summary['issues'] if i['status']=='Review']
            if review:
                payload={'event':'prospective_review','issues':[{'issue_id':i['issue_id'],'reasons':i['reasons']} for i in review]}
                atomic_json(Path(args.data)/'prospective-alert.json',payload);alert(payload)
            return 0
        if args.command=='fresh':
            if args.date and day!=datetime.now(timezone.utc).date():parser.error('fresh mode always acquires the current UTC day; use compare/fit for historical dates')
            from .fresh import run_current
            report=run_current(config,args.data,str(Path(args.output)/'fresh'),args.dashboard,args.acquire_only)
            logging.info('Current-day run %s: %s usable satellites; %s comparable freshness tests',report['run_id'],report['acquisition']['freshness']['usable_satellites'],report['benchmark'].get('comparable_satellites',0))
            return 0
        if args.command=="poll-gp":
            record=Archive(args.data).fetch(config["gp_url"],".omm.json",gp=True)
            sets=parse_gp(record["path"])
            logging.info("GP snapshot %s: %d objects",record["sha256"],len(sets))
            return 0
        if args.command=="daily":
            inputs=acquire(day,config,args.data)
            # Use EVERY archived GP set, not just the current snapshot.
            inputs["gp"]=[{"path":str(p.resolve()),"sha256":p.stem.split('.')[0],"source":"archived CelesTrak snapshot",
                           "retrieved_at":None} for p in sorted((Path(args.data)/"raw").glob("*.omm.json"))]
            # Restore retrieval timestamps and source URLs from append-only journal.
            journal=[json.loads(l) for l in (Path(args.data)/"retrievals.jsonl").read_text().splitlines()]
            by_hash={}
            for item in journal: by_hash.setdefault(item["sha256"],item)
            inputs["gp"]=[by_hash.get(item["sha256"],item) for item in inputs["gp"]]
        else:
            missing=[k for k in ("rinex","gp","eop","leaps") if not getattr(args,k)]
            if missing: parser.error("Local comparison requires: "+", ".join("--"+k for k in missing))
            if args.command=="validate-gps" and not args.sp3: parser.error("GPS validation requires --sp3")
            inputs=local_inputs(args.rinex,args.gp,args.eop,args.leaps,args.sp3)
        if args.command=="validate-gps":
            # GPS GP sets must be supplied separately; NavIC GP cannot validate GPS identities.
            config={**config,"identity_max_km":100,"thresholds":{"GEO":config["thresholds"]["GEO"],"IGSO":config["thresholds"]["IGSO"]}}
        validation_path=args.gps_validation or config.get("gps_validation_path")
        if validation_path and args.command!='validate-gps':
            from .pipeline import sha
            inputs['gps_validation']={'path':str(Path(validation_path).resolve()),'sha256':sha(validation_path),'source':'archived GPS/SP3 baseline','retrieved_at':None}
        run=run_comparison(day,config,inputs,args.output,args.dashboard,"G" if args.command=="validate-gps" else "I")
        if args.command=="validate-gps":
            import numpy as np
            rows=json.loads((Path(args.output)/run["run_id"]/"epochs.json").read_text())
            values=[r["sp3_broadcast_km"]*1000 for r in rows if r["sp3_broadcast_km"] is not None]
            result={"paired_epochs":len(values),"broadcast_sp3_rms_m":float(np.sqrt(np.mean(np.square(values)))) if values else None,
                    "pass":bool(values and np.sqrt(np.mean(np.square(values)))<20),
                    "criterion":"diagnostic <20 m RMS; antenna reference-point biases not corrected",
                    "run_id":run['run_id'],'day':run['day'],'fleet':run['fleet'],
                    'inputs':run['manifest']['inputs'],'software':run['manifest']['software'],
                    'code_sha256':run['manifest']['code_sha256'],
                    'satellites':[{k:s[k] for k in ('prn','norad_id','name','valid_epochs','rms_km','max_km')} for s in run['satellites']],
                    'sp3_note':'Check product class: ultra-rapid SP3 includes observed and predicted arcs. No antenna/COM correction applied.'}
            # Separate validation artifact; do not mutate a completed immutable run.
            atomic_json(Path(args.output)/(run["run_id"]+"-gps-validation.json"),result)
            logging.info("GPS/SP3 validation: %s",json.dumps(result))
            return 0 if result["pass"] else 2
        logging.info("Completed %s: %s",run["run_id"],json.dumps(run["fleet"]))
        if run["fleet"]["review_count"] or run.get('generator',{}).get('rejected_count',0):
            payload={"event":"review","run_id":run["run_id"],"fleet":run["fleet"],
                     "satellites":[{"prn":s["prn"],"reasons":s["reasons"]} for s in run["satellites"] if s["status"]=="Review"],
                     "generator_rejections":[{'prn':s['prn'],'reasons':s['reasons']} for s in run.get('generator',{}).get('satellites',[]) if s['status']!='Accepted']}
            atomic_json(Path(args.data)/"alert.json",payload);alert(payload)
        return 0
    except Exception as exc:
        logging.exception("Pipeline failed")
        payload={"event":"failure","day":str(day),"error":str(exc)}
        atomic_json(Path(args.data)/"alert.json",payload)
        try: alert(payload)
        except requests.RequestException: logging.error("Alert webhook failed")
        return 1

if __name__=="__main__": raise SystemExit(main())
