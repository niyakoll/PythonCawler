# shared/shared_pidlock.py
import os
import sys
import atexit
import logging

# 根據執行檔名稱自動選 lock 名稱
script_name = os.path.basename(sys.argv[0]).lower()
if "lihkg" in script_name:
    lock_name = "lihkg_flow_control.lock"
elif "threads" in script_name or "th" in script_name:
    lock_name = "threads_flow_control.lock"
elif "baby" in script_name or "bk" in script_name:
    lock_name = "bk_flow_control.lock"
else:
    lock_name = "flow_control.lock"

# Windows / Linux 自動適應
if os.name == 'nt':
    LOCK_FILE = os.path.join(os.environ.get('TEMP', r'C:\temp'), lock_name)
else:
    LOCK_FILE = f"/tmp/{lock_name}"

os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True) if os.name == 'nt' else None

def acquire_lock() -> bool:
    try:
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        atexit.register(release_lock)
        return True
    except FileExistsError:
        # 檢查舊程式是否還活著
        try:
            with open(LOCK_FILE) as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)  # 如果沒錯就代表還活著
            logging.warning(f"另一個實例正在運行 (PID {old_pid}) → 退出")
            return False
        except (OSError, ValueError, ProcessLookupError):
            # 舊程式已經死了 → 強制刪除 lock 檔案
            logging.info(f"發現殘留 lock 檔案，已自動清理: {LOCK_FILE}")
            try: os.unlink(LOCK_FILE)
            except: pass
            return acquire_lock()  # 再試一次

def release_lock():
    if os.path.exists(LOCK_FILE):
        try: os.unlink(LOCK_FILE)
        except: pass