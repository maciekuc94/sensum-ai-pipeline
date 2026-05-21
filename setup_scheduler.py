"""
One-time setup: register a weekly Windows Task Scheduler entry for agent11.

Run once:
    python setup_scheduler.py

The task runs every Sunday at 08:00 using the current Python interpreter.
To remove:
    python setup_scheduler.py --remove
"""

import argparse
import subprocess
import sys
from pathlib import Path

TASK_NAME = "SENSUM_Niche_Intelligence"
PROJECT_ROOT = Path(__file__).parent.resolve()
SCRIPT = PROJECT_ROOT / "tools" / "intelligence" / "agent11_intelligence.py"
PYTHON = sys.executable


def create_task():
    cmd = [
        "schtasks", "/Create", "/F",
        "/TN", TASK_NAME,
        "/TR", f'"{PYTHON}" "{SCRIPT}"',
        "/SC", "WEEKLY",
        "/D", "SUN",
        "/ST", "08:00",
        "/RL", "HIGHEST",
        "/RU", "SYSTEM",
    ]
    print(f"Creating task: {TASK_NAME}")
    print(f"Script       : {SCRIPT}")
    print(f"Schedule     : Every Sunday at 08:00\n")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("Task created successfully.")
        print("\nVerify in Task Scheduler → Task Scheduler Library → SENSUM_Niche_Intelligence")
        print("Or run: schtasks /Query /TN SENSUM_Niche_Intelligence /FO LIST")
    else:
        print(f"Error creating task:\n{result.stderr}")
        print("\nIf permission is denied, run this script as Administrator:")
        print("  Right-click terminal → Run as administrator → python setup_scheduler.py")
        sys.exit(1)


def remove_task():
    cmd = ["schtasks", "/Delete", "/F", "/TN", TASK_NAME]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Task '{TASK_NAME}' removed.")
    else:
        print(f"Error: {result.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--remove", action="store_true", help="Remove the scheduled task")
    args = parser.parse_args()

    if args.remove:
        remove_task()
    else:
        create_task()
