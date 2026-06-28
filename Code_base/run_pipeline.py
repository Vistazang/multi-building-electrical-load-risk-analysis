from pathlib import Path
import subprocess
import sys

base_path = Path(__file__).parent

scripts = [
    "generate_data.py",
    "Risk_analysis_and_summary_generation.py",
    "Mitigate_analyse.py",
    "After_and_before_processd_plot.py",
    "generate_summary.py"
]

def run_script(script_name):
    script_path = base_path / script_name

    print(f"\nRunning {script_name}...")
    python_exe = Path(sys.executable)

    if python_exe.name.lower() == "pythonw.exe":
        python_exe = python_exe.with_name("python.exe")

    result = subprocess.run(
        [str(python_exe), str(script_path)],
        check=True
    )

    print(f"Finished {script_name}")

def main():
    print("Starting electrical load risk analysis pipeline...")

    for script in scripts:
        run_script(script)

    print("\nPipeline completed successfully.")

if __name__ == "__main__":
    main()
