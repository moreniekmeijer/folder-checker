import os
import subprocess
import time
import config
from send2trash import send2trash


def get_top_level_items(path):
    """Return a list of top-level items (files + folders) in path, excluding system files."""
    return [
        os.path.join(path, f)
        for f in os.listdir(path)
        if f not in ['.DS_Store', '.localized']
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
            for dirpath, dirnames, filenames in os.walk(item_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.isfile(fp):
                        total_bytes += os.path.getsize(fp)
                        total_files += 1
    return total_bytes, len(items), total_files


def send_notification(title, message):
    subprocess.run([
        "osascript",
        "-e",
        f'display notification \"{message}\" with title \"{title}\"'
    ])


def delete_files_interactive(path, max_items=10):
    items = get_top_level_items(path)
    items.sort(key=os.path.getmtime, reverse=True)

    skip_all = False
    for item_path in items[:max_items]:
        if skip_all:
            print(f"{item_path} skipped (Skip All).")
            continue

        name = os.path.basename(item_path)
        script = f'display dialog "Do you want to remove this item?\n{name}" buttons {{"No","Yes","Skip All"}} default button "No"'
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

        if "Yes" in result.stdout:
            try:
                send2trash(item_path)
                print(f"{item_path} moved to Trash.")
            except Exception as e:
                print(f"Error moving {item_path} to Trash: {e}")
        elif "Skip All" in result.stdout:
            skip_all = True
            print("User chose Skip All — remaining items will be kept.")
        else:
            print(f"{item_path} kept.")


def run_checker():
    cfg = config.load_config()
    watch_paths = cfg.get("WATCH_PATHS", [])
    max_size_mb = cfg["MAX_SIZE_MB"]
    max_amount_files = cfg["MAX_AMOUNT_FILES"]
    max_interactive_files = cfg["MAX_INTERACTIVE_FILES"]

    for path in watch_paths:
        expanded_path = os.path.expanduser(path)

        if os.path.isdir(expanded_path):
            size_bytes, top_level_items, total_files = get_folder_size(expanded_path)
            size_mb = size_bytes / (1024 * 1024)

            print(f"Total files: {total_files}")
            print(f"Total size: {size_mb:.2f} MB")

            if size_mb > max_size_mb or total_files > max_amount_files:
                print('Cleanup path folder!')

                summary = f"{expanded_path} contains {total_files} files ({size_mb:.2f} MB).\n\nDo you want to cleanup now?"
                script = f'display dialog "{summary}" buttons {{"Remind me later","Clean now"}} default button "Remind me later"'
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

                if "Clean now" in result.stdout:
                    delete_files_interactive(expanded_path, max_interactive_files)
                else:
                    print("User chose to be reminded later.")
            else:
                print(f"{expanded_path} is within limits")
                summary = f"It contains {total_files} files ({size_mb:.2f} MB)."
                send_notification(f"{expanded_path} is within limits", summary)
        else:
            print('Cannot find folder')


if __name__ == "__main__":
    while True:
        run_checker()
        cfg = config.load_config()
        interval = cfg.get("CHECK_INTERVAL_SEC", 600)
        time.sleep(interval)