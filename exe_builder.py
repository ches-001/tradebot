import PyInstaller.__main__, os, argparse, sys
from distutils.dir_util import copy_tree
from main import BOT_DETAILS

APP_NAME:str =f"{BOT_DETAILS['BOT_NAME']}"

parser = argparse.ArgumentParser(description=APP_NAME)
parser.add_argument('version_no', type=str, metavar='version_no', help='Version Number')
parser.add_argument('app_build', type=str, choices=['gui', 'cli'], metavar='version_no', help='Version Number')
args = parser.parse_args()

APP_DIR:str = 'app'
VERSION:str = f'version-{args.version_no}'
WORKING_DIR:str = os.path.join(APP_DIR, VERSION)
BUILD_DIRNAME:str = f'{args.app_build}-build'
DIST_DIRNAME:str = 'dist'
APP_ICON_DIR = 'app_icon'

if not os.path.isdir(WORKING_DIR): os.makedirs(WORKING_DIR)
copy_tree(APP_ICON_DIR, os.path.join(WORKING_DIR, os.path.join(DIST_DIRNAME, APP_ICON_DIR)))

COMMAND_OPTS:list = [
    '--onefile',
    '--clean',
    '--workpath={path}'.format(path=os.path.join(WORKING_DIR, BUILD_DIRNAME)),
    '--specpath={path}'.format(path=WORKING_DIR),
    '--distpath={path}'.format(path=os.path.join(WORKING_DIR, DIST_DIRNAME)),
    '--icon={image}'.format(image=os.path.join(DIST_DIRNAME, BOT_DETAILS['BOT_ICON'])),
    '--name={name}-{build}'.format(name=APP_NAME, build=args.app_build) if args.app_build=='cli' else '--name={name}'.format(name=APP_NAME),
]

if args.app_build == 'cli':
    FILE_TO_BUILD:str='main.py'
    EXCLUSIONS:list = [
    'matplotlib', 'backtester', 'PyQt6',
    'pyqt6-tools', 'PyQt5', 'IPython',
    'PIL', 'curses', 'scipy',
    'tcl', 'Tkconstants', 'Tkinter',
    'mplfinance', 'asycio', 'MySQLdb',
    'sqlite3', 'zmq', 'sklearn']

elif args.app_build == 'gui':
    gui_dir = 'GUIs'
    config_dir = 'saved_config'

    # copy the extra data files to the app dir
    if os.path.isdir(gui_dir): copy_tree(gui_dir, os.path.join(WORKING_DIR, os.path.join(DIST_DIRNAME, gui_dir)))
    if os.path.isdir(config_dir): copy_tree(config_dir, os.path.join(WORKING_DIR, os.path.join(DIST_DIRNAME, config_dir)))

    FILE_TO_BUILD:str='gui_main.py'
    EXCLUSIONS:list = [
    'matplotlib', 'backtester',
    'pyqt6-tools', 'PyQt5', 'IPython',
    'PIL', 'curses', 'scipy',
    'tcl', 'Tkconstants', 'Tkinter',
    'mplfinance', 'asycio', 'MySQLdb',
    'sqlite3', 'zmq', 'sklearn']

    COMMAND_OPTS += ['--windowed']


else:
    print('invalid app_build type')
    sys.exit()

COMMAND_OPTS += ['--exclude-module={module}'.format(module=module) for module in EXCLUSIONS]

PyInstaller.__main__.run(
    [FILE_TO_BUILD] + COMMAND_OPTS 
)