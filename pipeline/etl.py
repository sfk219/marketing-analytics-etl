"""Idempotent CSV -> SQLite -> aggregated JSON reports."""
import csv,sqlite3,json,argparse
from pathlib import Path
from datetime import date
FIELDS=["event_id","date","channel","campaign","impressions","clicks","installs","spend_eur"]
def validate(r):
    if any(not r.get(k) for k in FIELDS):raise ValueError("missing field")
    date.fromisoformat(r["date"])
    imp,clk,ins=(int(r[k]) for k in ("impressions","clicks","installs"))
    spend=float(r["spend_eur"])
    if not (0<=ins<=clk<=imp and 0<=spend<float("inf")):raise ValueError("invalid counts or spend")
    return (r["event_id"],r["date"],r["channel"],r["campaign"],imp,clk,ins,spend)
def run(source="data/sample_campaigns.csv",db_path="output/campaigns.db",report_path="output/report.json"):
    Path(db_path).parent.mkdir(parents=True,exist_ok=True)
    Path(report_path).parent.mkdir(parents=True,exist_ok=True)
    added,duplicates,rejected=0,0,0
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY,event_date TEXT,channel TEXT,campaign TEXT,impressions INTEGER,clicks INTEGER,installs INTEGER,spend REAL)")
        with open(source,newline="",encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:values=validate(row)
                except (ValueError,TypeError,KeyError):rejected+=1;continue
                cur=db.execute("INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?,?)",values)
                if cur.rowcount:added+=1
                else:duplicates+=1
        rows=db.execute("SELECT channel,SUM(impressions),SUM(clicks),SUM(installs),ROUND(SUM(spend),2) FROM events GROUP BY channel").fetchall()
    data=[{"channel":ch,"impressions":imp,"clicks":clk,"installs":ins,"spend_eur":cost,
      "ctr_pct":round(100*clk/imp,2) if imp else None,"cpi_eur":round(cost/ins,2) if ins else None} for ch,imp,clk,ins,cost in rows]
    result={"inserted":added,"duplicates":duplicates,"rejected":rejected,"channels":data}
    Path(report_path).write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",default="data/sample_campaigns.csv");p.add_argument("--db",default="output/campaigns.db");p.add_argument("--report",default="output/report.json")
    x=p.parse_args();print(json.dumps(run(x.input,x.db,x.report),indent=2))
