"""Launch Dead Estate, watch 45s for a 'Code Error' dialog; report boot result."""
import ctypes, os, subprocess, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
user32 = ctypes.windll.user32
GAMEDIR = r"D:\Steam\steamapps\common\Dead Estate"
EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

def win_text(h):
    ln = user32.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(ln + 1)
    user32.GetWindowTextW(h, b, ln + 1)
    return b.value

subprocess.Popen([os.path.join(GAMEDIR, "Dead Estate.exe")], cwd=GAMEDIR)
t0 = time.time()
saw_game = False
while time.time() - t0 < 45:
    errs, games = [], []
    def cb(h, _):
        if user32.IsWindowVisible(h):
            t = win_text(h)
            if "Code Error" in t: errs.append(t)
            elif "Dead Estate" in t: games.append(t)
        return True
    user32.EnumWindows(EnumProc(cb), 0)
    if errs:
        print("CODE ERROR:", errs[0])
        sys.exit(1)
    if games:
        saw_game = True
    time.sleep(0.5)
print("no Code Error in 45s; game window seen:", saw_game)
