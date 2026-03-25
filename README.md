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
