from setuptools import setup

APP = ['menubar_app.py']
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/icon.icns',
    'packages': ['objc', 'Foundation', 'AppKit', 'CoreFoundation'],
    'resources': ['checker.py', 'config.py', 'settings_cocoa.py', 'logger_setup.py', 'resources/icon_disabled.icns', 'resources/icon_sweeper.png'],
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
    setup_requires=['py2app', 'pyobjc'],
)
