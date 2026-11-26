from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

NFL_GAMES_CSV_URL = "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv"
SEASONS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]


def main() -> None:
    all_path = RAW_DIR / "nflverse_all_schedules_raw.csv"
    home_path = RAW_DIR / "nflverse_seahawks_home_raw.csv"

    if all_path.exists() and home_path.exists():
        sea_home = pd.read_csv(home_path)
        print(f"Kept existing raw NFL files (did not overwrite): {home_path} ({len(sea_home)} rows)")
        return

    df = pd.read_csv(NFL_GAMES_CSV_URL, low_memory=False)
    if not all_path.exists():
        df.to_csv(all_path, index=False)

    sea_home = df[(df["season"].isin(SEASONS)) & (df["home_team"] == "SEA")].copy()
    if not home_path.exists():
        sea_home.to_csv(home_path, index=False)

    print(f"Saved raw NFL files to {RAW_DIR} ({len(sea_home)} Seahawks home rows)")


if __name__ == "__main__":
    main()