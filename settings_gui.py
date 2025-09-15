import tkinter as tk
from tkinter import filedialog, messagebox
import checker
import config
import launchagent_setup


INTERVAL_OPTIONS = {
    "Every 5 minutes": 300,
    "Every hour": 3600,
    "Every day": 86400,
    "Every week": 604800,
    "Every month": 2592000,
}


# def background_loop():
#     while True:
#         checker.run_checker()
#         cfg = config.load_config()
#         interval = cfg.get("CHECK_INTERVAL_SEC", 30)
#         time.sleep(interval)


def open_settings_window():
    launchagent_setup.setup_launchagent()

    cfg = config.load_config()

    root = tk.Tk()
    root.title("Folder Cleaner Settings")

    # Watch Path
    tk.Label(root, text="Watch Path:").grid(row=0, column=0, sticky="w")
    path_entry = tk.Entry(root, width=40)
    path_entry.insert(0, cfg["WATCH_PATH"])
    path_entry.grid(row=0, column=1)

    def browse_path():
        folder = filedialog.askdirectory()
        if folder:
            path_entry.delete(0, tk.END)
            path_entry.insert(0, folder)
    tk.Button(root, text="Browse", command=browse_path).grid(row=0, column=2)

    # Max Size
    tk.Label(root, text="Max Size (MB):").grid(row=1, column=0, sticky="w")
    size_entry = tk.Entry(root)
    size_entry.insert(0, cfg["MAX_SIZE_MB"])
    size_entry.grid(row=1, column=1)

    # Max Files
    tk.Label(root, text="Max Files:").grid(row=2, column=0, sticky="w")
    files_entry = tk.Entry(root)
    files_entry.insert(0, cfg["MAX_AMOUNT_FILES"])
    files_entry.grid(row=2, column=1)

    # Max Interactive Files
    tk.Label(root, text="Max Interactive Files:").grid(row=3, column=0, sticky="w")
    interactive_entry = tk.Entry(root)
    interactive_entry.insert(0, cfg["MAX_INTERACTIVE_FILES"])
    interactive_entry.grid(row=3, column=1)

    # Checker Interval Dropdown
    tk.Label(root, text="Checker Interval:").grid(row=4, column=0, sticky="w")
    interval_var = tk.StringVar(root)
    # Kies huidige config of standaard naar "Elke dag"
    current_interval = cfg.get("CHECK_INTERVAL_SEC", 86400)
    for label, seconds in INTERVAL_OPTIONS.items():
        if seconds == current_interval:
            interval_var.set(label)
            break
    else:
        interval_var.set("Elke dag")

    interval_menu = tk.OptionMenu(root, interval_var, *INTERVAL_OPTIONS.keys())
    interval_menu.grid(row=4, column=1)

    # Save button
    def save():
        new_cfg = {
            "WATCH_PATH": path_entry.get(),
            "MAX_SIZE_MB": int(size_entry.get()),
            "MAX_AMOUNT_FILES": int(files_entry.get()),
            "MAX_INTERACTIVE_FILES": int(interactive_entry.get()),
            "CHECK_INTERVAL_SEC": INTERVAL_OPTIONS[interval_var.get()],
        }
        config.save_config(new_cfg)
        messagebox.showinfo("Saved", "Settings saved successfully!")
        root.destroy()
        check()

    tk.Button(root, text="Save", command=save).grid(row=5, column=1)

    # Check button
    def check():
        try:
            checker.run_checker()
        except Exception as e:
            messagebox.showerror("Error", f"Checker failed: {e}")

    tk.Button(root, text="Check now", command=check).grid(row=7, column=1)

    # threading.Thread(target=background_loop, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    open_settings_window()
