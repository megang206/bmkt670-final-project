# Field Sources & Data Dictionary (`bmkt670_seahawks`)

## Data Sources
- **Schedule, Teams, & Scores:** `nflverse` / `nfldata` (`games.csv`), filtered to Seattle Seahawks (`SEA`) regular-season home games across 2018-2025 (excluding 2020), while using all NFL games in `games.csv` to compute leak-free pre-game team win percentage and win/loss streaks.
- **Stadium Weather:** Open-Meteo Historical Weather Archive API (`https://archive-api.open-meteo.com/v1/archive`) queried for Lumen Field (`47.5952, -122.3316`) in `America/Los_Angeles` hourly intervals (`temperature_2m`, `precipitation`, `wind_speed_10m`), aligned within 1 hour of kickoff.
- **Attendance Target:** Intended to come from `nfldata` (`attendance`) or a manual Pro-Football-Reference CSV in `data/manual/`; during the pipeline build run, 0 non-null attendance rows were present in `nfldata`, so a `68500` baseline placeholder was used until real attendance values are supplied.

## Star Schema & Feature Table Summary
- `dim_schedule`: Game grain (`game_id` PK), `season`, `week_number`, `game_date`, `kickoff_time_pt`, `kickoff_hour_pt`, `day_of_week`, `opponent`, `is_division_rival`, `is_primetime`.
- `dim_team_stats`: Pre-game team form (`seahawks_wins_prior`, `seahawks_losses_prior`, `seahawks_win_pct_prior`, `opponent_wins_prior`, `opponent_losses_prior`, `opponent_win_pct_prior`, `seahawks_streak_prior`, `playoff_implications_flag`).
- `dim_weather`: Kickoff-aligned weather at Lumen Field (`weather_timestamp_pt`, `temperature_f`, `precipitation_probability`, `precipitation_inches`, `wind_speed_mph`).
- `dim_local_context`: Game-date calendar flags (`game_date`, `is_holiday`, `conflicting_event_flag`).
- `fact_game_attendance`: Attendance fact rows (`game_id`, `game_date`, `actual_attendance`, `weather_id`, `context_id`).
- `ml_features_attendance`: Modeling table (`58` rows in current load) combining target `actual_attendance`, weather and pre-game form predictors, leak-free derived features (`win_pct_diff_prior`, `bad_weather_score`), and numeric categorical encodings (`is_division_rival_num`, `is_primetime_num`, `is_holiday_num`, `opponent_code`).