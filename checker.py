import os
import subprocess
import time
import config


def get_folder_size(path):
    total_bytes = 0
    total_files = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            if f in ['.DS_Store', '.localized']:
                continue
            total_files += 1
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_bytes += os.path.getsize(fp)
    return total_bytes, total_files


# def send_notification(title, message):
#     subprocess.run([
#         "osascript",
#         "-e",
#         f'display notification "{message}" with title "{title}"'
#     ])


def delete_files_interactive(path, max_files=10):
    files = [
        os.path.join(path, f)
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f not in ['.DS_Store', '.localized']
    ]
    files.sort(key=os.path.getmtime, reverse=True)

    skip_all = False
    for file_path in files[:max_files]:
        if skip_all:
            print(f"{file_path} skipped (Skip All).")
            continue

        filename = os.path.basename(file_path)
        script = f'display dialog "Do you want to remove this file?\n{filename}" buttons {{"No","Yes","Skip All"}} default button "No"'
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

        if "Yes" in result.stdout:
            os.remove(file_path)
            print(f"{file_path} deleted.")
        elif "Skip All" in result.stdout:
            skip_all = True
            print("User chose Skip All — remaining files will be kept.")
        else:
            print(f"{file_path} kept.")


def run_checker():
    cfg = config.load_config()
    expanded_path = os.path.expanduser(cfg["WATCH_PATH"])
    max_size_mb = cfg["MAX_SIZE_MB"]
    max_amount_files = cfg["MAX_AMOUNT_FILES"]
    max_interactive_files = cfg["MAX_INTERACTIVE_FILES"]

    if os.path.isdir(expanded_path):
        size_bytes, amount_files = get_folder_size(expanded_path)
        size_mb = size_bytes / (1024 * 1024)

        print(f"Total files: {amount_files}")
        print(f"Total size: {size_mb:.2f} MB")

        if size_mb > max_size_mb or amount_files > max_amount_files:
            print('Cleanup path folder!')
            # send_notification("Folder Alert", "Cleanup folder!")

            summary = f"{expanded_path} contains {amount_files} files ({size_mb:.2f} MB).\n\nDo you want to cleanup now?"
            script = f'display dialog "{summary}" buttons {{"Remind me later","Clean now"}} default button "Remind me later"'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

            if "Clean now" in result.stdout:
                delete_files_interactive(expanded_path, max_interactive_files)
            else:
                print("User chose to be reminded later.")
        else:
            print('Folder is OK')
    else:
        print('Cannot find folder')



if __name__ == "__main__":
    while True:
        run_checker()
        cfg = config.load_config()
        interval = cfg.get("CHECK_INTERVAL_SEC", 600)
        time.sleep(interval)