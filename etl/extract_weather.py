from pathlib import Path
import pandas as pd
import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
LUMEN_FIELD_LAT = 47.5952
LUMEN_FIELD_LON = -122.3316


def main() -> None:
    out_path = RAW_DIR / "open_meteo_lumen_field_hourly_raw.csv"
    if out_path.exists():
        weather_df = pd.read_csv(out_path)
        print(f"Kept existing raw weather file (did not overwrite): {out_path} ({len(weather_df)} rows)")
        return

    games_path = RAW_DIR / "nflverse_seahawks_home_raw.csv"
    if not games_path.exists():
        raise FileNotFoundError(f"Missing {games_path}. Run etl/extract_nfl.py first.")

    games = pd.read_csv(games_path)
    dates = pd.to_datetime(games["gameday"], errors="coerce").dropna()
    start_date = dates.min().strftime("%Y-%m-%d")
    end_date = dates.max().strftime("%Y-%m-%d")

    params = {
        "latitude": LUMEN_FIELD_LAT,
        "longitude": LUMEN_FIELD_LON,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,precipitation,wind_speed_10m",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "wind_speed_unit": "mph",
        "timezone": "America/Los_Angeles",
    }

    response = requests.get(OPEN_METEO_ARCHIVE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    hourly = pd.DataFrame(payload["hourly"]).rename(
        columns={
            "time": "weather_timestamp_pt",
            "temperature_2m": "temperature_f",
            "precipitation": "precipitation_inches",
            "wind_speed_10m": "wind_speed_mph",
        }
    )

    hourly.to_csv(out_path, index=False)
    print(f"Saved {len(hourly)} hourly weather rows ({start_date} to {end_date}) to {out_path}")


if __name__ == "__main__":
    main()