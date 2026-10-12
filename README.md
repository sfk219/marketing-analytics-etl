# Marketing Analytics ETL

A runnable batch data pipeline that reads **fictional marketing campaign data** from CSV, validates it, deduplicates on event ID and stores it in SQLite. Produces a channel-level JSON report with CTR and cost per install.

## Run (Python standard library only)
```bash
python -m pipeline.etl --input data/sample_campaigns.csv --db output/campaigns.db --report output/report.json
python -m unittest discover -s tests -v
```

Re-run the pipeline to see idempotent inserts: previously processed events are detected as duplicates.

**Tech:** Python, SQL, SQLite, ETL, data cleaning, aggregation and reporting. This is not a GA4, AppsFlyer or live advertising-platform integration.