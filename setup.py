from setuptools import setup


APP = ['settings_gui.py']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': 'Folder Cleaner',
        'CFBundleDisplayName': 'Folder Cleaner',
        'CFBundleIdentifier': 'nl.moreniekmeijer.foldercleaner',
        'CFBundleVersion': '0.1',
        'CFBundleShortVersionString': '0.1',
    },
    # 'iconfile': 'resources/icon.icns',
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
