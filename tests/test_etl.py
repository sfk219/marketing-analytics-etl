import tempfile
from pathlib import Path
from pipeline.etl import run
def test_idempotence():
    with tempfile.TemporaryDirectory() as d:
        db=str(Path(d)/"db.sqlite");report=str(Path(d)/"report.json")
        a=run("data/sample_campaigns.csv",db,report)
        b=run("data/sample_campaigns.csv",db,report)
        assert a["inserted"]==5
        assert b["inserted"]==0 and b["duplicates"]==5
        assert len(b["channels"])==3
