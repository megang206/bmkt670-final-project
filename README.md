# Seattle Seahawks Home Game Attendance Prediction

## Business Question
How many fans will attend an upcoming Seattle Seahawks home game at Lumen Field Stadium?

## Target Variable
Game attendance

## Prediction Unit
One row in my ML feature table = one home game.

## Data Sources
| Source | What it provides | Access |
|---|---|---|  
| nflverse (Python library / API) | Game schedule, IDs, dates, kickoff times, opponents, and week numbers | Real-time API / Python package download |
| Pro-Football-Reference | Historical team records, streaks, and win-loss data | Hand-downloaded CSV archive |
| Open-Meteo API | Historical and forecast weather (temperature, precipitation, wind speed) | Real-time API call |

* **Pro-Football-Reference (Manual Download):** Downloaded from [Pro-Football-Reference](https://www.pro-football-reference.com) on October 11, 2026, using the team schedules table export to CSV feature.

## How to Run
1. Create and activate a virtual environment
2. Install packages: pip install -r requirements.txt
3. Create a .env file with your API keys and DB_PASSWORD 
4. Pull the data: run each script in etl/ (e.g., python etl/extract_nflverse.py)  
5. Build the database: run sql/schema.sql in pgAdmin or psql
6. Confirm it worked: python db_check.py (should print all table names)

## AI Usage
Used AI collaborator to structure project repository and draft schema and ETL extraction scripts.