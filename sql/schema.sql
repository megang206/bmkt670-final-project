-- Drop existing tables to allow clean re-runs
DROP TABLE IF EXISTS fact_game_attendance CASCADE;
DROP TABLE IF EXISTS dim_schedule CASCADE;
DROP TABLE IF EXISTS dim_team_stats CASCADE;
DROP TABLE IF EXISTS dim_weather CASCADE;
DROP TABLE IF EXISTS dim_local_context CASCADE;

-- Dimension: Game Schedule and Timing
-- One row represents schedule metadata for a Seahawks game
CREATE TABLE dim_schedule (
    game_id VARCHAR(50) PRIMARY KEY,
    game_date DATE NOT NULL,
    kickoff_time TIME,
    opponent VARCHAR(50) NOT NULL,
    day_of_week VARCHAR(15),
    is_division_rival BOOLEAN,
    week_number INTEGER
);

-- Dimension: Team Performance & Records
-- One row represents team records prior to a given game
CREATE TABLE dim_team_stats (
    team_stat_id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) UNIQUE REFERENCES dim_schedule(game_id),
    seahawks_win_loss_record VARCHAR(10),
    opponent_win_loss_record VARCHAR(10),
    playoff_implications_flag BOOLEAN,
    seahawks_streak INTEGER
);

-- Dimension: Weather at Kickoff
-- One row represents stadium weather mapped to game date/time
CREATE TABLE dim_weather (
    weather_id SERIAL PRIMARY KEY,
    game_date DATE NOT NULL,
    temperature_f NUMERIC(5,2),
    precipitation_probability NUMERIC(5,2),
    precipitation_inches NUMERIC(5,2),
    wind_speed_mph NUMERIC(5,2)
);

-- Dimension: Local Context & Holidays
-- One row represents local events or holiday flags for a game date
CREATE TABLE dim_local_context (
    context_id SERIAL PRIMARY KEY,
    game_date DATE NOT NULL,
    is_holiday BOOLEAN,
    conflicting_event_flag BOOLEAN
);

-- Fact Table: Game Attendance (Primary Table)
-- One row represents an individual Seahawks home game and actual attendance
CREATE TABLE fact_game_attendance (
    attendance_id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) REFERENCES dim_schedule(game_id),
    game_date DATE NOT NULL,
    actual_attendance INTEGER,
    weather_id INTEGER REFERENCES dim_weather(weather_id),
    context_id INTEGER REFERENCES dim_local_context(context_id)
);