from setuptools import setup

APP = ['menubar_app.py']
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/sweeper.icns',
    'packages': ['objc', 'Foundation', 'AppKit', 'CoreFoundation'],
    'resources': ['checker.py', 'config.py', 'settings_cocoa.py', 'logger_setup.py', 
                  'resources/disabled.icns', 'resources/enabled.icns', 
                  'resources/sweeper_disabled.icns', 'resources/sweeper_enabled.icns',
                  'resources/sweeper_dark.icns'],
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
