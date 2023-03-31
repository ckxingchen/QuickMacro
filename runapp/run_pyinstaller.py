import os
import PyInstaller.__main__

project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
ico_path = os.path.join(project_path, 'images', 'icon', 'logo.png')

PyInstaller.__main__.run([
    'runApp.py',
    '-n=自动办公助手',
    '-i={}'.format(ico_path),
    '-D',
    '-w',
    '--paths={}'.format(project_path),
    '--distpath={}'.format(os.path.join(project_path, 'driver')),
    '--clean',
    '--noupx'
])