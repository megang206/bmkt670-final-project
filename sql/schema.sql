CREATE TABLE IF NOT EXISTS dim_schedule (
    game_id VARCHAR(50) PRIMARY KEY,
    season INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    game_date DATE NOT NULL,
    kickoff_time_pt VARCHAR(20),
    kickoff_hour_pt INTEGER,
    day_of_week VARCHAR(20),
    opponent VARCHAR(100) NOT NULL,
    is_division_rival BOOLEAN NOT NULL DEFAULT FALSE,
    is_primetime BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS dim_team_stats (
    team_stats_id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL REFERENCES dim_schedule(game_id) ON DELETE CASCADE,
    seahawks_wins_prior INTEGER NOT NULL DEFAULT 0,
    seahawks_losses_prior INTEGER NOT NULL DEFAULT 0,
    seahawks_win_pct_prior DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    opponent_wins_prior INTEGER NOT NULL DEFAULT 0,
    opponent_losses_prior INTEGER NOT NULL DEFAULT 0,
    opponent_win_pct_prior DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    seahawks_streak_prior INTEGER NOT NULL DEFAULT 0,
    playoff_implications_flag BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS dim_weather (
    weather_id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL REFERENCES dim_schedule(game_id) ON DELETE CASCADE,
    game_date DATE NOT NULL,
    weather_timestamp_pt TIMESTAMP,
    temperature_f DOUBLE PRECISION,
    precipitation_probability DOUBLE PRECISION,
    precipitation_inches DOUBLE PRECISION,
    wind_speed_mph DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS dim_local_context (
    context_id SERIAL PRIMARY KEY,
    game_date DATE NOT NULL,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    conflicting_event_flag BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS fact_game_attendance (
    attendance_id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL REFERENCES dim_schedule(game_id) ON DELETE CASCADE,
    game_date DATE NOT NULL,
    actual_attendance INTEGER NOT NULL,
    weather_id INTEGER REFERENCES dim_weather(weather_id) ON DELETE SET NULL,
    context_id INTEGER REFERENCES dim_local_context(context_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ml_features_attendance (
    game_id VARCHAR(50) PRIMARY KEY REFERENCES dim_schedule(game_id) ON DELETE CASCADE,
    season INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    actual_attendance INTEGER NOT NULL,
    kickoff_hour_pt INTEGER NOT NULL,
    temperature_f DOUBLE PRECISION NOT NULL,
    precipitation_inches DOUBLE PRECISION NOT NULL,
    wind_speed_mph DOUBLE PRECISION NOT NULL,
    seahawks_win_pct_prior DOUBLE PRECISION NOT NULL,
    opponent_win_pct_prior DOUBLE PRECISION NOT NULL,
    seahawks_streak_prior INTEGER NOT NULL,
    win_pct_diff_prior DOUBLE PRECISION NOT NULL,
    bad_weather_score DOUBLE PRECISION NOT NULL,
    is_division_rival_num INTEGER NOT NULL,
    is_primetime_num INTEGER NOT NULL,
    is_holiday_num INTEGER NOT NULL,
    opponent_code INTEGER NOT NULL
);
