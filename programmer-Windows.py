import time
import threading
import psutil
import shutil
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
SOURCE_FILE = os.path.join(SCRIPT_DIR, 'multi_launcher.ino.uf2')
DEST_FILENAME = 'multi_launcher.ino.uf2'

# Track drive + copy state
copied_drives = {}

def is_target_usb(drive):
    required_files = {'INDEX.HTM', 'INFO_UF2.TXT'}
    try:
        files = set(os.listdir(drive))
        return required_files.issubset(files)
    except Exception:
        return False

def copy_to_drive(drive):
    if not is_target_usb(drive):
        print(f'Skipped {drive} (required files not found)')
        return
    try:
        dest = os.path.join(drive, DEST_FILENAME)
        print(f'Copying to {dest}')
        shutil.copy2(SOURCE_FILE, dest)
        print(f'Successfully copied to {dest}')
        copied_drives[drive] = True
    except Exception as e:
        print(f'Error copying to {drive}: {e}')

def monitor_usb():
    print('Waiting for USB drives...')
    while True:
        current_drives = {p.device for p in psutil.disk_partitions() if 'removable' in p.opts}
        
        # Forget drives that were removed
        for drive in list(copied_drives.keys()):
            if drive not in current_drives:
                del copied_drives[drive]

        for drive in current_drives:
            if drive not in copied_drives:
                copied_drives[drive] = False
                threading.Thread(target=copy_to_drive, args=(drive,), daemon=True).start()
        
        time.sleep(1)

if __name__ == '__main__':
    monitor_usb()
