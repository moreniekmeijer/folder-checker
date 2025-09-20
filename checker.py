import os
import subprocess
import time
import config
from logger_setup import logger
from AppKit import NSBundle
from notifications import send_notification

logger.info("Checker started")


EXCLUDED_PATTERNS = {".DS_Store", ".localized", ".Spotlight-V100", ".fseventsd", ".Trash"}


def get_top_level_items(path):
    """Return a list of top-level items (files + folders) in path, excluding system files."""
    return [
        os.path.join(path, f)
        for f in os.listdir(path)
        if f not in EXCLUDED_PATTERNS
    ]


def get_folder_size(path):
    """Return total bytes, number of top-level items, and total files recursively."""
    total_bytes = 0
    total_files = 0
    items = get_top_level_items(path)
    for item_path in items:
        if os.path.isfile(item_path):
            total_bytes += os.path.getsize(item_path)
            total_files += 1
        elif os.path.isdir(item_path):
            for dirpath, _, filenames in os.walk(item_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.isfile(fp):
                        total_bytes += os.path.getsize(fp)
                        total_files += 1
    return total_bytes, len(items), total_files


def move_to_trash(path):
    logger.info(f"Moving to Trash: {path}")
    script = f'tell application "Finder" to move (POSIX file "{path}") to trash'
    subprocess.run(["osascript", "-e", script])


def delete_files_interactive(path, max_items=10):
    bundle = NSBundle.mainBundle()
    icon_path = bundle.pathForResource_ofType_("icon_sweeper", "icns")

    items = get_top_level_items(path)
    items.sort(key=os.path.getmtime, reverse=True)

    skip_all = False
    """Return a list of top-level items (files + folders) in path, excluding system files."""
    for item_path in items[:max_items]:
        if skip_all:
            logger.debug(f"{item_path} skipped (Skip All).")
            continue

        name = os.path.basename(item_path)
        if icon_path:
            script = f'display dialog "Do you want to remove this item?\n\n{name}" with icon POSIX file "{icon_path}" buttons {{"No","Yes","Skip All"}} default button "No"'
        else:
            script = f'display dialog "Do you want to remove this item?\n\n{name}" buttons {{"No","Yes","Skip All"}} default button "No"'
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

        if "Yes" in result.stdout:
            try:
                move_to_trash(item_path)
                logger.info(f"{item_path} moved to Trash.")
            except Exception as e:
                logger.error(f"Error moving {item_path} to Trash: {e}")
        elif "Skip All" in result.stdout:
            skip_all = True
            logger.info("User chose Skip All — remaining items will be kept.")
        else:
            logger.debug(f"{item_path} kept.")


def run_checker():
    cfg = config.load_config()
    watch_paths = cfg.get("WATCH_PATHS", [])
    max_size_mb = cfg["MAX_SIZE_MB"]
    max_amount_items = cfg["MAX_AMOUNT_ITEMS"]
    max_interactive_files = cfg["MAX_INTERACTIVE_FILES"]

    bundle = NSBundle.mainBundle()
    icon_disabled_path = bundle.pathForResource_ofType_("icon_disabled", "icns")

    for path in watch_paths:
        expanded_path = os.path.expanduser(path)

        if os.path.isdir(expanded_path):
            size_bytes, top_level_items, total_files = get_folder_size(expanded_path)
            size_mb = size_bytes / (1024 * 1024)

            logger.info(f"Checking {expanded_path} → {top_level_items} items, {size_mb:.2f} MB")

            if size_mb > max_size_mb or top_level_items > max_amount_items:
                logger.warning(f"Folder exceeds limits: {expanded_path}")

                summary = f"{expanded_path} contains {top_level_items} items ({size_mb:.2f} MB).\n\nDo you want to cleanup now?"
                if icon_disabled_path:
                    script = f'display dialog "{summary}" with icon POSIX file "{icon_disabled_path}" buttons {{"Remind me later","Clean now"}} default button "Remind me later"'
                else:
                    script = f'display dialog "{summary}" buttons {{"Remind me later","Clean now"}} default button "Remind me later"'
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

                if "Clean now" in result.stdout:
                    logger.info("User chose Clean now")
                    delete_files_interactive(expanded_path, max_interactive_files)
                else:
                    logger.info("User chose Remind me later")
            else:
                logger.info(f"{expanded_path} is within limits")
                summary = f"It contains {top_level_items} items ({size_mb:.2f} MB)."
                send_notification(f"{expanded_path} is within limits", summary)
        else:
            logger.error(f"Cannot find folder: {expanded_path}")


if __name__ == "__main__":
    while True:
        run_checker()
        cfg = config.load_config()
        interval = cfg.get("CHECK_INTERVAL_SEC", 300)
        logger.debug(f"Sleeping for {interval} seconds...")
        time.sleep(interval)
