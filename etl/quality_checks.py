import os
from pathlib import Path
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

CLEAN_DIR = Path("data/clean")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "bmkt670_seahawks"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


def main() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) - COUNT(DISTINCT game_id) FROM fact_game_attendance;")
    dupes = cur.fetchone()[0]
    print(f"[{'PASS' if dupes == 0 else 'FAIL'}] Duplicate game_ids in fact_game_attendance: {dupes}")

    cur.execute("SELECT COUNT(*) FROM fact_game_attendance WHERE actual_attendance <= 0 OR actual_attendance > 68740;")
    bad_range = cur.fetchone()[0]
    print(f"[{'PASS' if bad_range == 0 else 'FAIL'}] Out-of-range attendance rows: {bad_range}")

    cur.execute(
        """
        SELECT COUNT(*)
        FROM dim_weather w
        JOIN dim_schedule s ON w.game_id = s.game_id
        WHERE ABS(
            EXTRACT(EPOCH FROM (
                w.weather_timestamp_pt - (s.game_date + (s.kickoff_time_pt || ':00')::TIME)
            ))
        ) > 3600;
        """
    )
    misaligned = cur.fetchone()[0]
    print(f"[{'PASS' if misaligned == 0 else 'FAIL'}] Weather rows >1 hour from kickoff: {misaligned}")

    cur.execute(
        """
        SELECT COUNT(*) FILTER (
            WHERE actual_attendance IS NULL
               OR temperature_f IS NULL
               OR precipitation_inches IS NULL
               OR wind_speed_mph IS NULL
               OR seahawks_win_pct_prior IS NULL
               OR opponent_win_pct_prior IS NULL
        ), COUNT(*)
        FROM ml_features_attendance;
        """
    )
    null_rows, total_ml = cur.fetchone()
    null_pct = (null_rows / total_ml * 100.0) if total_ml > 0 else 100.0
    print(f"[{'PASS' if null_pct < 5.0 else 'FAIL'}] Core ML null rate: {null_pct:.2f}% ({null_rows}/{total_ml})")

    cur.execute(
        """
        SELECT COUNT(*)
        FROM fact_game_attendance f
        LEFT JOIN dim_schedule s ON f.game_id = s.game_id
        WHERE s.game_id IS NULL;
        """
    )
    orphans = cur.fetchone()[0]
    print(f"[{'PASS' if orphans == 0 else 'FAIL'}] Orphaned fact rows: {orphans}")

    cur.execute("SELECT COUNT(*) FROM fact_game_attendance;")
    db_fact_count = cur.fetchone()[0]
    clean_fact_count = len(pd.read_csv(CLEAN_DIR / "fact_game_attendance.csv"))
    diff = abs(db_fact_count - clean_fact_count)
    print(f"[{'PASS' if diff == 0 else 'FAIL'}] Fact row count diff (Postgres={db_fact_count} vs clean CSV={clean_fact_count}): {diff}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
