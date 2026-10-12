# Field Sources Data Dictionary

| Table | Field | Comes from | How | Used for |
|---|---|---|---|---|
| dim_schedule | game_id | nflverse | Unique game identifier string | Key: links games across dimension and fact tables |
| dim_schedule | game_date | nflverse | Converted date format | Key: links to weather and local context tables |
| dim_schedule | kickoff_time | nflverse | Kickoff timestamp | Feature: game time impact |
| dim_schedule | opponent | nflverse | Team abbreviation | Feature / Dashboard display |
| dim_schedule | day_of_week | nflverse | Derived from game_date | Feature: day of week impact |
| dim_schedule | is_division_rival | Calculated in Python | Flag based on division opponent list | Feature for model |
| dim_schedule | week_number | nflverse | Season week integer | Feature: week of season |
| dim_team_stats | team_stat_id | Created (Postgres) | Auto-increment primary key | Key: primary key |
| dim_team_stats | game_id | nflverse | Foreign key to schedule | Key: links team stats to game |
| dim_team_stats | seahawks_win_loss_record | Pro-Football-Reference | Wins-Losses record string | Feature: team momentum |
| dim_team_stats | opponent_win_loss_record | Pro-Football-Reference | Opponent record string | Feature: opponent strength |
| dim_team_stats | playoff_implications_flag | Pro-Football-Reference | Flag based on standings late in season | Feature |
| dim_team_stats | seahawks_streak | Pro-Football-Reference | Win/loss streak count | Feature |
| dim_weather | weather_id | Created (Postgres) | Auto-increment primary key | Key: primary key |
| dim_weather | game_date | Open-Meteo API | Date mapped to kickoff | Key: links to date |
| dim_weather | temperature_f | Open-Meteo API | Hourly temp at kickoff | Feature |
| dim_weather | precipitation_probability | Open-Meteo API | Hourly precip chance | Feature |
| dim_weather | precipitation_inches | Open-Meteo API | Hourly precip amount | Feature |
| dim_weather | wind_speed_mph | Open-Meteo API | Hourly wind speed | Feature |
| dim_local_context | context_id | Created (Postgres) | Auto-increment primary key | Key: primary key |
| dim_local_context | game_date | Calculated in Python | US Holiday calendar comparison | Key: links to date |
| dim_local_context | is_holiday | Calculated in Python | Boolean flag | Feature |
| dim_local_context | conflicting_event_flag | Calculated in Python | Event calendar check | Feature |
| fact_game_attendance | attendance_id | Created (Postgres) | Auto-increment primary key | Key: primary key |
| fact_game_attendance | game_id | nflverse | Foreign key | Key: links game schedule |
| fact_game_attendance | game_date | nflverse | Foreign key | Key: links dates |
| fact_game_attendance | actual_attendance | Pro-Football-Reference | Official stadium game attendance | Target Variable for ML Model |
| fact_game_attendance | weather_id | Joined | Foreign key from dim_weather | Key: links weather |
| fact_game_attendance | context_id | Joined | Foreign key from dim_local_context | Key: links context |