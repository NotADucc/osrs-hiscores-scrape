from pathlib import Path
import subprocess
import sys

def main():
    generator_scripts = sorted(
        p for p in Path(__file__).resolve().parent.glob("generate_*.py")
        if p.name != "run_generators.py"
    )

    if not generator_scripts:
        print("No generator scripts found.")
        return

    for script in generator_scripts:
        print(f"Running generator: {script.name}")

        result = subprocess.run(
            [sys.executable, str(script)],
            check=False,
        )

        if result.returncode != 0:
            raise SystemExit(
                f"Generator failed: {script.name}"
            )

    print("All generators completed successfully.")


if __name__ == "__main__":
    main()