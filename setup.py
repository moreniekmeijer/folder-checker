from setuptools import setup


APP = ['src/menubar_app.py']
DATA_FILES = [
    'resources/disabled.icns',
    'resources/enabled.icns',
    'resources/sweeper_disabled.icns',
    'resources/sweeper_enabled.icns',
    'resources/folder.icns',
    'resources/doc.icns',
    'resources/rtf.icns',
    'resources/txt.icns',
    'resources/mp3.icns',
    'resources/wav.icns',
    'resources/aiff.icns',
    'resources/zip.icns',
    'resources/dmg.icns',
    'resources/mp4.icns',
    'resources/mov.icns',
    'resources/app.icns',
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
)
