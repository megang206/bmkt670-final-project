import os
from pathlib import Path
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

SCHEMA_PATH = Path("sql/schema.sql")
CLEAN_DIR = Path("data/clean")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "bmkt670_seahawks"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


def execute_sql_file(cur, path: Path) -> None:
    raw_sql = path.read_text(encoding="utf-8-sig")
    statements = [s.strip() for s in raw_sql.split(";") if s.strip()]
    for stmt in statements:
        cur.execute(stmt + ";")


def main() -> None:
    conn = get_connection()
    cur = conn.cursor()

    execute_sql_file(cur, SCHEMA_PATH)
    cur.execute(
        """
        TRUNCATE TABLE
            ml_features_attendance,
            fact_game_attendance,
            dim_weather,
            dim_team_stats,
            dim_local_context,
            dim_schedule
        RESTART IDENTITY CASCADE;
        """
    )

    sched_df = pd.read_csv(CLEAN_DIR / "dim_schedule.csv")
    for _, r in sched_df.iterrows():
        cur.execute(
            """
            INSERT INTO dim_schedule (
                game_id, season, week_number, game_date, kickoff_time_pt,
                kickoff_hour_pt, day_of_week, opponent, is_division_rival, is_primetime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                r["game_id"], int(r["season"]), int(r["week_number"]), r["game_date"],
                r["kickoff_time_pt"], int(r["kickoff_hour_pt"]), r["day_of_week"],
                r["opponent"], bool(r["is_division_rival"]), bool(r["is_primetime"]),
            ),
        )

    team_df = pd.read_csv(CLEAN_DIR / "dim_team_stats.csv")
    for _, r in team_df.iterrows():
        cur.execute(
            """
            INSERT INTO dim_team_stats (
                game_id, seahawks_wins_prior, seahawks_losses_prior,
                seahawks_win_pct_prior, opponent_wins_prior, opponent_losses_prior,
                opponent_win_pct_prior, seahawks_streak_prior, playoff_implications_flag
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                r["game_id"], int(r["seahawks_wins_prior"]), int(r["seahawks_losses_prior"]),
                float(r["seahawks_win_pct_prior"]), int(r["opponent_wins_prior"]),
                int(r["opponent_losses_prior"]), float(r["opponent_win_pct_prior"]),
                int(r["seahawks_streak_prior"]), bool(r["playoff_implications_flag"]),
            ),
        )

    context_df = pd.read_csv(CLEAN_DIR / "dim_local_context.csv")
    context_map = {}
    for _, r in context_df.iterrows():
        cur.execute(
            """
            INSERT INTO dim_local_context (game_date, is_holiday, conflicting_event_flag)
            VALUES (%s, %s, %s)
            RETURNING context_id;
            """,
            (r["game_date"], bool(r["is_holiday"]), bool(r["conflicting_event_flag"])),
        )
        context_map[str(r["game_date"])] = cur.fetchone()[0]

    weather_df = pd.read_csv(CLEAN_DIR / "dim_weather.csv")
    weather_map = {}
    for _, r in weather_df.iterrows():
        ts_val = None if pd.isna(r["weather_timestamp_pt"]) else str(r["weather_timestamp_pt"])
        cur.execute(
            """
            INSERT INTO dim_weather (
                game_id, game_date, weather_timestamp_pt, temperature_f,
                precipitation_probability, precipitation_inches, wind_speed_mph
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING weather_id;
            """,
            (
                r["game_id"], r["game_date"], ts_val, float(r["temperature_f"]),
                float(r["precipitation_probability"]), float(r["precipitation_inches"]),
                float(r["wind_speed_mph"]),
            ),
        )
        weather_map[r["game_id"]] = cur.fetchone()[0]

    fact_df = pd.read_csv(CLEAN_DIR / "fact_game_attendance.csv")
    for _, r in fact_df.iterrows():
        cur.execute(
            """
            INSERT INTO fact_game_attendance (
                game_id, game_date, actual_attendance, weather_id, context_id
            ) VALUES (%s, %s, %s, %s, %s);
            """,
            (
                r["game_id"], r["game_date"], int(r["actual_attendance"]),
                weather_map.get(r["game_id"]), context_map.get(str(r["game_date"])),
            ),
        )

    ml_df = pd.read_csv(CLEAN_DIR / "ml_features_attendance.csv")
    for _, r in ml_df.iterrows():
        cur.execute(
            """
            INSERT INTO ml_features_attendance (
                game_id, season, week_number, actual_attendance, kickoff_hour_pt,
                temperature_f, precipitation_inches, wind_speed_mph,
                seahawks_win_pct_prior, opponent_win_pct_prior, seahawks_streak_prior,
                win_pct_diff_prior, bad_weather_score, is_division_rival_num,
                is_primetime_num, is_holiday_num, opponent_code
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                r["game_id"], int(r["season"]), int(r["week_number"]), int(r["actual_attendance"]),
                int(r["kickoff_hour_pt"]), float(r["temperature_f"]), float(r["precipitation_inches"]),
                float(r["wind_speed_mph"]), float(r["seahawks_win_pct_prior"]),
                float(r["opponent_win_pct_prior"]), int(r["seahawks_streak_prior"]),
                float(r["win_pct_diff_prior"]), float(r["bad_weather_score"]),
                int(r["is_division_rival_num"]), int(r["is_primetime_num"]),
                int(r["is_holiday_num"]), int(r["opponent_code"]),
            ),
        )

    conn.commit()
    print(
        f"Loaded {len(sched_df)} dim_schedule, {len(team_df)} dim_team_stats, "
        f"{len(weather_df)} dim_weather, {len(context_df)} dim_local_context, "
        f"{len(fact_df)} fact_game_attendance, {len(ml_df)} ml_features_attendance rows."
    )
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
