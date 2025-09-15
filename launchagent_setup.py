import os
import plistlib
import sys
import subprocess


def setup_launchagent():
    plist_path = os.path.expanduser("~/Library/LaunchAgents/nl.moreniekmeijer.foldercleaner.plist")
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "checker.py"))

    if not os.path.exists(plist_path):
        plist = {
            'Label': 'nl.moreniekmeijer.foldercleaner',
            'ProgramArguments': [sys.executable, script_path],
            'RunAtLoad': True,
        }

        os.makedirs(os.path.dirname(plist_path), exist_ok=True)

        with open(plist_path, 'wb') as f:
            plistlib.dump(plist, f)

        subprocess.run(["launchctl", "load", plist_path], check=True)
        print("LaunchAgent made and loaded:", plist_path)
    else:
        print("LaunchAgent already exists:", plist_path)


if __name__ == "__main__":
    setup_launchagent()
