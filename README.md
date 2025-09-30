# FolderChecker

FolderChecker is a lightweight macOS menubar app that automatically monitors selected folders and warns you when they become too full. The goal is simple: keep your selected folders clean and organized, without constantly having to think about it yourself.

---

## Why FolderChecker?

Many users let their Desktop or Downloads folder fill up with files. This can become messy, slow down your workflow, or even negatively impact your Mac’s performance. FolderChecker provides a solution by continuously monitoring the folders you select. As soon as a folder reaches a set limit (for example, in terms of number of files or total size), you’ll receive a notification so you can take action immediately.

With FolderChecker you can:

- **Automatically monitor**: let the app check once per given interval.
- **Add folders of your choice**: such as Desktop, Downloads, or a project folder.
- **Receive smart alerts**: get a notification if everything is within size/amount limits or a dialog box once a folder exceeds its set limits.
- **Clean up files**: decide to tidy up right away or postpone until later.

---

## Features in detail

- **Menubar app**  
  FolderChecker runs quietly in your menubar. From the icon, you can open the settings, start a manual check, or temporarily disable the checker.

- **Settings window**  
  Through the settings you can easily:

  - Add or remove folders to monitor.
  - Set a maximum folder size (in MB).
  - Set a maximum number of items.
  - Adjust the interval at which the checker runs.

- **Notifications and dialogs**  
  You’ll receive a subtle notification when a folder is within limits, or a warning dialog when it’s time to clean up. This way, you won’t be surprised by a cluttered desktop.

- **Manual check**  
  Click _Check now_ in the menu to perform a check immediately.

<!-- - **Automatic disabling**
  If no folders are selected, the checker stops automatically. This is reflected in the menubar icon right away. -->

---

## Installation

1. Download the latest release from the [releases page](https://github.com/moreniekmeijer/folder-checker/releases).
2. Unzip the `.zip` file.
3. Drag `FolderChecker.app` into your **Applications** folder.
4. Launch the app via Launchpad or Spotlight. The icon will appear in your menubar.

> Tip: Since this is not a signed app from the App Store, macOS Gatekeeper may warn you. In that case, right-click the app → **Open** to launch it.

---

## Uninstall

To uninstall simply select the uninstall option from the menubar. This immediately deletes the config files and the app itself.

---

## Usage

1. Open the app, the icon appears in the menubar.
2. Click the icon and choose **Open settings**.
3. Add the folders you want to monitor.
4. Set limits for file size and number of items.
5. Let FolderChecker run in the background — it takes care of the rest.

---

## Known limitations

- FolderChecker has currently only been tested on recent macOS versions (Monterey, Ventura, and Sonoma).
- Since the app is not distributed via the App Store, you may need to bypass Gatekeeper warnings the first time you open it.
- There is no automatic updater yet; to update you’ll need to manually download the latest zip.

---

## Contributing

Suggestions and improvements are welcome! Feel free to open an _issue_ or a _pull request_ on GitHub.

---

## License

This software is available under the **MIT License**. See the `LICENSE` file for details.
