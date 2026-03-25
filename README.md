# advery_ttg

MVP: Early Warning System (EWS) for traffic anomalies.

## Quick start

1. Create venv and install dependencies:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Run demo scenarios:
   - `PYTHONPATH=src python run_mvp.py --scenario healthy`
   - `PYTHONPATH=src python run_mvp.py --scenario black_hole`
   - `PYTHONPATH=src python run_mvp.py --scenario loop`
   - `PYTHONPATH=src python run_mvp.py --scenario false_cap`
   - `PYTHONPATH=src python run_mvp.py --scenario drop`
   - `PYTHONPATH=src python run_mvp.py --scenario new_offer_black_hole`

## What this MVP includes

- historical baseline profiler by `offer + geo + weekday + 10m slot`
- anomaly detector with rules:
  - black hole
  - traffic loop
  - false cap sync
  - behavioral drop
  - new offer guardrail
- Teams Power Automate payload formatter (with manager email routing)

## Test with real data chunk (CSV/JSON)

You can run the detector using real data export from your DB.

### 1) Prepare history file

File: `data/history.csv` (or `.json`)

Canonical columns:
- `offer_id`
- `geo`
- `day_of_week` (Monday=0 ... Sunday=6)
- `slot_10m` (0..143, where `hour * 6 + minute // 10`)
- `hits_10m`
- `clicks_10m`

You can skip `day_of_week` + `slot_10m` if your export has timestamp field
(`timestamp`/`event_time`/`created_at`/`datetime`/`time`).

### 2) Prepare current snapshot file

File: `data/snapshot.csv` (or `.json`)

Canonical columns:
- `offer_id`
- `offer_name`
- `geo`
- `day_of_week`
- `slot_10m`
- `hits_10m`
- `clicks_10m`
- `cap_counter`
- `cap_limit`

Optional column:
- `declines_cap_reason_10m` (defaults to `0`)

Also supports common aliases (examples):
- `offerId` -> `offer_id`
- `country` -> `geo`
- `dow` -> `day_of_week`
- `slot` -> `slot_10m`
- `hits` -> `hits_10m`
- `clicks` -> `clicks_10m`
- `cap_used` -> `cap_counter`
- `cap` -> `cap_limit`

### 3) (Optional) manager mapping

Create `data/manager_mapping.json`:

```json
{
  "offer_activechannel": "ivan.ivanov@company.com",
  "offer_other": "anna.petrova@company.com"
}
```

### 4) Run

```bash
PYTHONPATH=src python run_mvp.py \
  --mode files \
  --history-file data/history.csv \
  --snapshot-file data/snapshot.csv \
  --manager-mapping-file data/manager_mapping.json
```
