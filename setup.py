from setuptools import setup

APP = ['menubar_app.py']
DATA_FILES = [
    'resources/disabled.icns',
    'resources/enabled.icns',
    'resources/sweeper_disabled.icns',
    'resources/sweeper_enabled.icns',
    'resources/sweeper_dark.icns',
]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/sweeper.icns',
    'packages': ['Cocoa', 'objc', 'Foundation', 'AppKit', 'CoreFoundation'],
    'resources': DATA_FILES,
    'plist': {
        'CFBundleName': 'FolderChecker',
        'CFBundleDisplayName': 'FolderChecker',
        'CFBundleIdentifier': 'nl.moreniekmeijer.folderchecker',
        'CFBundleVersion': '0.1',
        'CFBundleShortVersionString': '0.1',
        'LSUIElement': True,
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    install_requires=['pyobjc'],
    py_modules=['checker', 'config', 'settings_cocoa', 'logger_setup'],
)
