# pidlock.py
import os
import sys
import atexit
import logging

# ← 這段自動偵測作業系統，選對的路徑
if os.name == 'nt':  # Windows
    LOCK_FILE = os.path.join(os.environ.get('TEMP', r'C:\temp'), 'flow_control.lock')
else:  # Linux / macOS / Docker
    LOCK_FILE = "/tmp/flow_control.lock"

# 確保目錄存在（Windows 專用）
if os.name == 'nt':
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)

def acquire_lock() -> bool:
    """Return True if we got the lock (first/only instance), False if another is running"""
    try:
        # O_EXCL = fail if exists → atomic
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        logging.info(f"Lock acquired → PID {os.getpid()} (only instance)")
        atexit.register(release_lock)
        return True
    except FileExistsError:
        # Check if old process is still alive
        try:
            with open(LOCK_FILE) as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)  # raises OSError if dead
            logging.warning(f"Another instance running (PID {old_pid}) → exiting")
            return False
        except (OSError, ValueError, ProcessLookupError):
            # Stale lock → old container died
            logging.info("Stale lock found → removing and taking over")
            try:
                os.unlink(LOCK_FILE)
            except:
                pass
            return acquire_lock()  # retry once

def release_lock():
    """Remove lock on clean exit"""
    if os.path.exists(LOCK_FILE):
        try:
            os.unlink(LOCK_FILE)
            logging.info("Lock released on exit")
        except:
            pass