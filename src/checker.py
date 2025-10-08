import os
import time
import config
from logger_setup import logger
from dialogs import show_dialog, move_to_trash
from notifications import send_notification
from AppKit import NSBundle

logger.info("Checker started")


EXCLUDED_FOLDERS = {
    ".DS_Store",
    ".localized",
    ".Spotlight-V100",
    ".fseventsd",
    ".Trash",
}

ALLOWED_ICON_EXTS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff", ".bmp", ".heic", ".svg", ".icns"
}

EXTENSION_MAP = {
    "mp3": {".mp3"},
    "wav": {".wav"},
    "aiff": {".aiff", ".aif"},
    "mp4": {".mp4"},
    "mov": {".mov"},
    "zip": {".zip"},
    "dmg": {".dmg"},
    "doc": {".doc", ".odt", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"},
    "txt": {".txt", ".text", ".md", ".markdown", ".csv", ".log", ".json", ".xml", ".yaml", ".yml"},
    "rtf": {".rtf"},
    "app": {".app"},
}


def get_top_level_items(path):
    """Return a list of top-level items (files + folders) in path, excluding system files."""
    return [
        os.path.join(path, f)
        for f in os.listdir(path)
        if f not in EXCLUDED_FOLDERS
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


def load_icons():
    """Load app icon paths for various file types."""
    bundle = NSBundle.mainBundle()
    return {
        "doc": bundle.pathForResource_ofType_("doc", "icns"),
        "rtf": bundle.pathForResource_ofType_("rtf", "icns"),
        "txt": bundle.pathForResource_ofType_("txt", "icns"),
        "mp3": bundle.pathForResource_ofType_("mp3", "icns"),
        "wav": bundle.pathForResource_ofType_("wav", "icns"),
        "aiff": bundle.pathForResource_ofType_("aiff", "icns"),
        "mp4": bundle.pathForResource_ofType_("mp4", "icns"),
        "mov": bundle.pathForResource_ofType_("mov", "icns"),
        "zip": bundle.pathForResource_ofType_("zip", "icns"),
        "dmg": bundle.pathForResource_ofType_("dmg", "icns"),
        "app": bundle.pathForResource_ofType_("app", "icns"),
        "folder": bundle.pathForResource_ofType_("folder", "icns"),
        "fallback": bundle.pathForResource_ofType_("sweeper", "icns"),
    }


def get_icon_for_item(item_path, icons):
    """Return icon path for a given file or folder."""
    if os.path.isdir(item_path):
        return icons.get("folder") or icons.get("fallback")

    ext = os.path.splitext(item_path)[1].lower()

    if ext in ALLOWED_ICON_EXTS:
        return item_path

    for category, exts in EXTENSION_MAP.items():
        if ext in exts:
            return icons.get(category) or icons.get("fallback")

    return icons.get("fallback")


def delete_files_interactive(path, max_items=10):
    """Ask user interactively which items to delete."""
    icons = load_icons()
    items = get_top_level_items(path)
    items.sort(key=os.path.getmtime, reverse=True)

    skip_all = False
    for item_path in items[:max_items]:
        if skip_all:
            logger.debug(f"{item_path} skipped (Skip All).")
            continue

        name = os.path.basename(item_path)
        icon_path = get_icon_for_item(item_path, icons)

        choice = show_dialog(
            f"Do you want to remove this item?\n\n{name}",
            icon_name=icon_path,
            buttons=("No", "Yes", "Skip All"),
            default_button="No",
            timeout=60,
        )

        if choice == "Yes":
            try:
                move_to_trash(item_path)
                logger.info(f"{item_path} moved to Trash.")
            except Exception as e:
                logger.error(f"Error moving {item_path} to Trash: {e}")
        elif choice == "Skip All":
            skip_all = True
            logger.info("User chose Skip All — remaining items will be kept.")
        else:
            logger.debug(f"{item_path} kept.")

        time.sleep(0.05)


def run_checker(interactive=False):
    """Main cleanup logic: check folder sizes and optionally run cleanup."""
    cfg = config.load_config()

    if not cfg.get("FIRST_RUN_DONE", False):
        logger.info("Skipping checker because FIRST_RUN_DONE is not set")
        return

    watch_paths = cfg.get("WATCH_PATHS", [])
    max_size_mb = cfg["MAX_SIZE_MB"]
    max_amount_items = cfg["MAX_AMOUNT_ITEMS"]
    max_interactive_files = cfg["MAX_INTERACTIVE_FILES"]

    icon_disabled = "sweeper_disabled"
    icon_enabled = "sweeper_enabled"

    if not watch_paths:
        logger.warning("No folders selected")
        show_dialog(
            "No folders selected.\n\nPlease add at least one folder in the settings.",
            icon_name=icon_disabled,
            buttons=("OK",),
            default_button="OK",
            timeout=30,
        )
        return

    for path in watch_paths:
        expanded_path = os.path.expanduser(path)

        if os.path.isdir(expanded_path):
            size_bytes, top_level_items, total_files = get_folder_size(expanded_path)
            size_mb = size_bytes / (1024 * 1024)
            logger.info(f"Checking {expanded_path} → {top_level_items} items, {size_mb:.2f} MB")

            if size_mb > max_size_mb or top_level_items > max_amount_items:
                logger.warning(f"Folder exceeds limits: {expanded_path}")

                summary = (
                    f"{expanded_path} contains {top_level_items} items ({size_mb:.2f} MB).\n\n"
                    "Do you want to clean up now?"
                )
                choice = show_dialog(
                    summary,
                    icon_name=icon_disabled,
                    buttons=("Remind me later", "Clean now"),
                    default_button="Remind me later",
                    timeout=60,
                )

                if choice == "Clean now":
                    logger.info("User chose Clean now")
                    delete_files_interactive(expanded_path, max_interactive_files)
                else:
                    logger.info("User chose Remind me later")

            else:
                logger.info(f"{expanded_path} is within limits")
                summary = f"It contains {top_level_items} items ({size_mb:.2f} MB)."

                if interactive:
                    show_dialog(
                        f"{expanded_path} is within limits.\n\n{summary}",
                        icon_name=icon_enabled,
                        buttons=("OK",),
                        default_button="OK",
                        timeout=30,
                    )
                else:
                    send_notification(
                        expanded_path,
                        f"Folder is within limits.\n{summary}",
                    )

        else:
            logger.error(f"Cannot find folder: {expanded_path}")


if __name__ == "__main__":
    while True:
        run_checker()
        cfg = config.load_config()
        interval = cfg.get("CHECK_INTERVAL_SEC", 300)
        logger.debug(f"Sleeping for {interval} seconds...")
        time.sleep(interval)
