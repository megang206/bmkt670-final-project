import subprocess
import sys

STEPS = [
    "etl/extract_nfl.py",
    "etl/extract_weather.py",
    "etl/transform.py",
    "etl/load.py",
    "etl/quality_checks.py",
]


def main() -> None:
    for step in STEPS:
        print(f"=== Running {step} ===")
        result = subprocess.run([sys.executable, step], check=False)
        if result.returncode != 0:
            print(f"Stopped: {step} exited with code {result.returncode}")
            sys.exit(result.returncode)
    print("Pipeline finished.")


if __name__ == "__main__":
    main()
