import os
import plistlib
import sys
import subprocess

def setup_launchagent():
    plist_path = os.path.expanduser("~/Library/LaunchAgents/nl.moreniekmeijer.foldercleaner.plist")
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "checker.py"))

    if not os.path.exists(plist_path):
        # Maak plist dictionary aan
        plist = {
            'Label': 'nl.moreniekmeijer.foldercleaner',
            'ProgramArguments': [sys.executable, script_path],
            'RunAtLoad': True,   # Start bij inloggen
            'KeepAlive': True    # Houd script draaiende als het crasht
        }

        # Zorg dat de map bestaat
        os.makedirs(os.path.dirname(plist_path), exist_ok=True)

        # Schrijf plist
        with open(plist_path, 'wb') as f:
            plistlib.dump(plist, f)

        # Laad de LaunchAgent
        subprocess.run(["launchctl", "load", plist_path], check=True)
        print("LaunchAgent aangemaakt en geladen:", plist_path)
    else:
        print("LaunchAgent bestaat al:", plist_path)

if __name__ == "__main__":
    setup_launchagent()
