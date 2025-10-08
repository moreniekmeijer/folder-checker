import subprocess, os
from logger_setup import logger
from AppKit import NSBundle


def show_dialog(message, icon_name=None, buttons=("OK",), default_button="OK", timeout=60):
    bundle = NSBundle.mainBundle()
    icon_path = None

    if icon_name:
        if os.path.exists(icon_name):
            icon_path = icon_name
        else:
            icon_path = bundle.pathForResource_ofType_(icon_name, "icns")

    safe_message = message.replace('"', '\\"')

    button_list = "{" + ",".join(f'"{b}"' for b in buttons) + "}"

    if icon_path:
        script = (
            f'display dialog "{safe_message}" with icon POSIX file "{icon_path}" '
            f'buttons {button_list} default button "{default_button}"'
        )
    else:
        script = (
            f'display dialog "{safe_message}" '
            f'buttons {button_list} default button "{default_button}"'
        )

    if timeout:
        script += f' giving up after {timeout}'

    logger.debug(f"AppleScript: {script}")

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout + 2 if timeout else None
        )

        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        
        logger.debug(f"Dialog stdout: '{stdout}'")
        logger.debug(f"Dialog stderr: '{stderr}'")
        logger.debug(f"Dialog return code: {result.returncode}")
        
        if "button returned" in stdout:
            button_part = stdout.split("button returned:")[-1].strip()
            button_returned = button_part.split(",")[0].strip()
            logger.info(f"Button clicked: '{button_returned}'")
            return button_returned
        
        if result.returncode != 0:
            logger.warning(f"Dialog cancelled or error occurred")
            return None
            
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