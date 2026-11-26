from pathlib import Path
import numpy as np
import pandas as pd

RAW_DIR = Path("data/raw")
MANUAL_DIR = Path("data/manual")
CLEAN_DIR = Path("data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

NFC_WEST = {"ARI", "LA", "LAR", "SF", "SEA"}

TEAM_NAME_MAP = {
    "ARI": "Arizona Cardinals",
    "ATL": "Atlanta Falcons",
    "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills",
    "CAR": "Carolina Panthers",
    "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals",
    "CLE": "Cleveland Browns",
    "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos",
    "DET": "Detroit Lions",
    "GB": "Green Bay Packers",
    "HOU": "Houston Texans",
    "IND": "Indianapolis Colts",
    "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs",
    "LA": "Los Angeles Rams",
    "LAR": "Los Angeles Rams",
    "LAC": "Los Angeles Chargers",
    "LV": "Las Vegas Raiders",
    "OAK": "Oakland Raiders",
    "MIA": "Miami Dolphins",
    "MIN": "Minnesota Vikings",
    "NE": "New England Patriots",
    "NO": "New Orleans Saints",
    "NYG": "New York Giants",
    "NYJ": "New York Jets",
    "PHI": "Philadelphia Eagles",
    "PIT": "Pittsburgh Steelers",
    "SEA": "Seattle Seahawks",
    "SF": "San Francisco 49ers",
    "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans",
    "WAS": "Washington Commanders",
    "WSH": "Washington Commanders",
    "Washington Football Team": "Washington Commanders",
    "Washington Redskins": "Washington Commanders",
}


def normalize_team_name(val: object) -> str:
    if pd.isna(val):
        return "Unknown"
    text = str(val).strip()
    return TEAM_NAME_MAP.get(text, text)


def compute_prior_team_form(all_games: pd.DataFrame) -> pd.DataFrame:
    valid = all_games.dropna(subset=["home_score", "away_score"]).copy()
    valid["game_dt"] = pd.to_datetime(valid["gameday"], errors="coerce")
    valid = valid.sort_values(["season", "game_dt", "game_id"]).reset_index(drop=True)

    rows = []
    for _, g in valid.iterrows():
        h_win = 1 if g["home_score"] > g["away_score"] else 0
        h_loss = 1 if g["home_score"] < g["away_score"] else 0
        a_win = 1 if g["away_score"] > g["home_score"] else 0
        a_loss = 1 if g["away_score"] < g["home_score"] else 0

        rows.append({"game_id": g["game_id"], "season": int(g["season"]), "team": g["home_team"], "win": h_win, "loss": h_loss})
        rows.append({"game_id": g["game_id"], "season": int(g["season"]), "team": g["away_team"], "win": a_win, "loss": a_loss})

    long_df = pd.DataFrame(rows).sort_values(["season", "team", "game_id"]).reset_index(drop=True)

    prior_wins, prior_losses, prior_win_pct, prior_streak = [], [], [], []
    for _, grp in long_df.groupby(["season", "team"], sort=False):
        w_cum, l_cum, streak = 0, 0, 0
        for _, r in grp.iterrows():
            games_played = w_cum + l_cum
            win_pct = (w_cum / games_played) if games_played > 0 else 0.0
            prior_wins.append(w_cum)
            prior_losses.append(l_cum)
            prior_win_pct.append(round(win_pct, 4))
            prior_streak.append(streak)

            if r["win"] == 1:
                w_cum += 1
                streak = streak + 1 if streak > 0 else 1
            elif r["loss"] == 1:
                l_cum += 1
                streak = streak - 1 if streak < 0 else -1
            else:
                streak = 0

    long_df["prior_wins"] = prior_wins
    long_df["prior_losses"] = prior_losses
    long_df["prior_win_pct"] = prior_win_pct
    long_df["prior_streak"] = prior_streak
    return long_df


def build_kickoff_pt(df: pd.DataFrame) -> pd.Series:
    date_part = pd.to_datetime(df["gameday"], errors="coerce").dt.strftime("%Y-%m-%d")
    raw_time = df["gametime"] if "gametime" in df.columns else pd.Series([""] * len(df), index=df.index)
    time_part = raw_time.fillna("16:05").astype(str).str.strip().replace("", "16:05")
    et_dt = pd.to_datetime(date_part + " " + time_part, errors="coerce")
    fallback_dt = pd.to_datetime(date_part + " 16:05:00", errors="coerce")
    et_dt = et_dt.fillna(fallback_dt)
    return et_dt - pd.Timedelta(hours=3)


def main() -> None:
    raw_home_path = RAW_DIR / "nflverse_seahawks_home_raw.csv"
    raw_all_path = RAW_DIR / "nflverse_all_schedules_raw.csv"
    raw_weather_path = RAW_DIR / "open_meteo_lumen_field_hourly_raw.csv"

    home = pd.read_csv(raw_home_path)
    if "game_type" in home.columns:
        home = home[home["game_type"] == "REG"].copy()
    home = home[home["season"] != 2020].copy()

    manual_files = list(MANUAL_DIR.glob("*.csv")) if MANUAL_DIR.exists() else []
    att_series = pd.Series(home["attendance"], index=home.index) if "attendance" in home.columns else pd.Series([np.nan] * len(home), index=home.index)
    if manual_files:
        manual_df = pd.read_csv(manual_files[0])
        if "game_id" in manual_df.columns and "attendance" in manual_df.columns:
            home = home.merge(
                manual_df[["game_id", "attendance"]].rename(columns={"attendance": "manual_att"}),
                on="game_id",
                how="left",
            )
            att_series = pd.Series(home["attendance"] if "attendance" in home.columns else np.nan, index=home.index).combine_first(home["manual_att"])
        elif {"season", "week", "attendance"}.issubset(manual_df.columns):
            home = home.merge(
                manual_df[["season", "week", "attendance"]].rename(columns={"attendance": "manual_att"}),
                on=["season", "week"],
                how="left",
            )
            att_series = pd.Series(home["attendance"] if "attendance" in home.columns else np.nan, index=home.index).combine_first(home["manual_att"])

    home["actual_attendance"] = pd.to_numeric(att_series, errors="coerce")
    non_null_att = int(home["actual_attendance"].notna().sum())
    if non_null_att == 0:
        print("Warning: 0 non-null attendance rows found in raw/manual data; keeping games with stadium baseline (68500) for pipeline build.")
        home["actual_attendance"] = 68500
    else:
        home = home.dropna(subset=["actual_attendance"]).copy()
        home["actual_attendance"] = home["actual_attendance"].astype(int)
        home = home[(home["actual_attendance"] > 0) & (home["actual_attendance"] <= 68740)].copy()

    all_sched = pd.read_csv(raw_all_path, low_memory=False)
    all_sched = all_sched[all_sched["season"] != 2020].copy()
    form_df = compute_prior_team_form(all_sched)

    sea_form = form_df[form_df["team"] == "SEA"][
        ["game_id", "prior_wins", "prior_losses", "prior_win_pct", "prior_streak"]
    ].rename(columns={
        "prior_wins": "seahawks_wins_prior",
        "prior_losses": "seahawks_losses_prior",
        "prior_win_pct": "seahawks_win_pct_prior",
        "prior_streak": "seahawks_streak_prior",
    })

    opp_form = form_df[
        ["game_id", "team", "prior_wins", "prior_losses", "prior_win_pct"]
    ].rename(columns={
        "team": "away_team",
        "prior_wins": "opponent_wins_prior",
        "prior_losses": "opponent_losses_prior",
        "prior_win_pct": "opponent_win_pct_prior",
    })

    home = home.merge(sea_form, on="game_id", how="left").merge(
        opp_form, on=["game_id", "away_team"], how="left"
    )

    home["game_date"] = pd.to_datetime(home["gameday"], errors="coerce").dt.date
    home["kickoff_dt_pt"] = build_kickoff_pt(home)
    home["kickoff_time_pt"] = home["kickoff_dt_pt"].dt.strftime("%H:%M")
    home["kickoff_hour_pt"] = home["kickoff_dt_pt"].dt.hour.astype(int)
    home["day_of_week"] = pd.to_datetime(home["game_date"]).dt.day_name()
    home["opponent"] = home["away_team"].apply(normalize_team_name)
    home["is_division_rival"] = home["away_team"].isin(NFC_WEST)
    home["is_primetime"] = (
        (home["day_of_week"] != "Sunday")
        | (home["kickoff_hour_pt"] >= 17)
        | (home["kickoff_hour_pt"] < 12)
    )

    weather_raw = pd.read_csv(raw_weather_path)
    weather_raw["weather_dt_pt"] = pd.to_datetime(weather_raw["weather_timestamp_pt"], errors="coerce")
    weather_raw = weather_raw.dropna(subset=["weather_dt_pt"]).sort_values("weather_dt_pt")

    home_sorted = home.sort_values("kickoff_dt_pt").copy()
    merged = pd.merge_asof(
        home_sorted,
        weather_raw,
        left_on="kickoff_dt_pt",
        right_on="weather_dt_pt",
        direction="nearest",
        tolerance=pd.Timedelta(hours=1),
    )

    merged["temperature_f"] = pd.to_numeric(merged["temperature_f"], errors="coerce").fillna(54.0)
    merged["precipitation_inches"] = pd.to_numeric(merged["precipitation_inches"], errors="coerce").fillna(0.0)
    merged["precipitation_probability"] = np.where(merged["precipitation_inches"] > 0, 80.0, 15.0)
    merged["wind_speed_mph"] = pd.to_numeric(merged["wind_speed_mph"], errors="coerce").fillna(8.0)

    merged["seahawks_wins_prior"] = merged["seahawks_wins_prior"].fillna(0).astype(int)
    merged["seahawks_losses_prior"] = merged["seahawks_losses_prior"].fillna(0).astype(int)
    merged["seahawks_win_pct_prior"] = merged["seahawks_win_pct_prior"].fillna(0.0).astype(float)
    merged["opponent_wins_prior"] = merged["opponent_wins_prior"].fillna(0).astype(int)
    merged["opponent_losses_prior"] = merged["opponent_losses_prior"].fillna(0).astype(int)
    merged["opponent_win_pct_prior"] = merged["opponent_win_pct_prior"].fillna(0.0).astype(float)
    merged["seahawks_streak_prior"] = merged["seahawks_streak_prior"].fillna(0).astype(int)

    merged["month_day"] = pd.to_datetime(merged["game_date"]).dt.strftime("%m-%d")
    merged["is_holiday"] = merged["month_day"].isin(
        {"11-11", "11-26", "11-27", "11-28", "12-24", "12-25", "12-31", "01-01"}
    )
    merged["conflicting_event_flag"] = False

    merged["win_pct_diff_prior"] = (merged["seahawks_win_pct_prior"] - merged["opponent_win_pct_prior"]).round(4)
    merged["bad_weather_score"] = (
        merged["precipitation_inches"] * 25.0
        + np.maximum(0.0, merged["wind_speed_mph"] - 12.0) * 0.5
        + np.maximum(0.0, 45.0 - merged["temperature_f"]) * 0.25
    ).round(4)

    merged["is_division_rival_num"] = merged["is_division_rival"].astype(int)
    merged["is_primetime_num"] = merged["is_primetime"].astype(int)
    merged["is_holiday_num"] = merged["is_holiday"].astype(int)
    merged["opponent_code"] = merged["opponent"].astype("category").cat.codes.astype(int)

    merged = merged.sort_values(["season", "week", "game_id"]).reset_index(drop=True)

    dim_schedule = merged[[
        "game_id", "season", "week", "game_date", "kickoff_time_pt",
        "kickoff_hour_pt", "day_of_week", "opponent", "is_division_rival", "is_primetime",
    ]].rename(columns={"week": "week_number"})

    dim_team_stats = merged[[
        "game_id", "seahawks_wins_prior", "seahawks_losses_prior",
        "seahawks_win_pct_prior", "opponent_wins_prior", "opponent_losses_prior",
        "opponent_win_pct_prior", "seahawks_streak_prior",
    ]].copy()
    dim_team_stats["playoff_implications_flag"] = merged["week"] >= 15

    dim_weather = merged[[
        "game_id", "game_date", "weather_dt_pt", "temperature_f",
        "precipitation_probability", "precipitation_inches", "wind_speed_mph",
    ]].rename(columns={"weather_dt_pt": "weather_timestamp_pt"})

    dim_local_context = (
        merged[["game_date", "is_holiday", "conflicting_event_flag"]]
        .drop_duplicates(subset=["game_date"])
        .reset_index(drop=True)
    )

    fact_game_attendance = merged[["game_id", "game_date", "actual_attendance"]].copy()

    ml_features = merged[[
        "game_id", "season", "week", "actual_attendance", "kickoff_hour_pt",
        "temperature_f", "precipitation_inches", "wind_speed_mph",
        "seahawks_win_pct_prior", "opponent_win_pct_prior", "seahawks_streak_prior",
        "win_pct_diff_prior", "bad_weather_score", "is_division_rival_num",
        "is_primetime_num", "is_holiday_num", "opponent_code",
    ]].rename(columns={"week": "week_number"})

    dim_schedule.to_csv(CLEAN_DIR / "dim_schedule.csv", index=False)
    dim_team_stats.to_csv(CLEAN_DIR / "dim_team_stats.csv", index=False)
    dim_weather.to_csv(CLEAN_DIR / "dim_weather.csv", index=False)
    dim_local_context.to_csv(CLEAN_DIR / "dim_local_context.csv", index=False)
    fact_game_attendance.to_csv(CLEAN_DIR / "fact_game_attendance.csv", index=False)
    ml_features.to_csv(CLEAN_DIR / "ml_features_attendance.csv", index=False)

    print(f"Transform complete: {len(fact_game_attendance)} Seahawks home games saved to {CLEAN_DIR}")


if __name__ == "__main__":
    main()
