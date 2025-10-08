import subprocess
from logger_setup import logger
from AppKit import NSBundle

def show_dialog(message, icon_name=None, buttons=("OK",), default_button="OK", timeout=60):
    bundle = NSBundle.mainBundle()
    icon_path = None

    if icon_name:
        icon_path = bundle.pathForResource_ofType_(icon_name, "icns")

    button_list = "{" + ",".join(f'"{b}"' for b in buttons) + "}"
    if icon_path:
        script = f'display dialog "{message}" with icon POSIX file "{icon_path}" buttons {button_list} default button "{default_button}"'
    else:
        script = f'display dialog "{message}" buttons {button_list} default button "{default_button}"'

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        stdout = (result.stdout or "").strip()
        if "button returned" in stdout:
            return stdout.split(":")[-1].strip()
        return None
    except subprocess.TimeoutExpired:
        logger.warning("Dialog timed out (no user response).")
        return None
    except Exception as e:
        logger.error(f"Error showing dialog: {e}")
        return None


def move_to_trash(path):
    logger.info(f"Moving to Trash: {path}")
    script = f'tell application "Finder" to move (POSIX file "{path}") to trash'
    try:
        subprocess.run(["osascript", "-e", script], check=True, timeout=30)
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout moving {path} to Trash")
    except Exception as e:
        logger.error(f"Error moving to Trash: {e}")
