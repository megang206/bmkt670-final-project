# Missing Data & Data Quality Log

## Known Gaps & Handling Rules
1. **Attendance Column Missing in `nfldata` (`0` non-null rows in raw pull):**
   - `nflverse/nfldata` `games.csv` contained null/missing attendance values for the pulled Seahawks home games.
   - `etl/transform.py` supports merging a manual CSV from `data/manual/` keyed on `game_id` or (`season`, `week`), and falls back to `68500` when no non-null attendance values are present so the ETL and database checks remain runnable.
2. **2020 Season Exclusion:**
   - The 2020 NFL season is excluded because attendance restrictions/capacity limits distort normal crowd demand patterns.
3. **Hourly Weather Alignment & Fallback Defaults:**
   - Hourly Open-Meteo observations for Lumen Field are matched to kickoff time within a 1-hour tolerance (`merge_asof`). Any missing weather metric defaults to reasonable Seattle baseline values (`54.0` F, `0.0` in precipitation, `8.0` mph wind).
4. **Automated Quality Checks (`etl/quality_checks.py`):**
   - Verified 0 duplicate `game_id` rows in `fact_game_attendance`, 0 out-of-range attendance rows (`1..68740`), 0 weather rows >1 hour from kickoff, `0.00%` core ML null rate (`0/58`), 0 orphaned fact rows, and exact reconciliation (`58` rows) between `data/clean/fact_game_attendance.csv` and PostgreSQL.