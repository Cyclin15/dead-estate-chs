"""Find the running 'Code Error' dialog, click its Copy button, read clipboard."""
import ctypes, ctypes.wintypes as wt, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
user32 = ctypes.windll.user32
EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

def win_text(h):
    ln = user32.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(ln + 1)
    user32.GetWindowTextW(h, b, ln + 1)
    return b.value

# find dialog
dlg = []
def cb(h, _):
    if user32.IsWindowVisible(h) and win_text(h) == "Code Error":
        dlg.append(h)
    return True
user32.EnumWindows(EnumProc(cb), 0)
if not dlg:
    print("no dialog"); sys.exit(1)
hwnd = dlg[0]
print("hwnd", hwnd)

# find Copy button child
btn = []
def cb2(h, _):
    if win_text(h) == "Copy":
        btn.append(h)
    return True
user32.EnumChildWindows(ctypes.c_void_p(hwnd), EnumProc(cb2), 0)
print("copy btn", btn)
if btn:
    user32.SendMessageW(btn[0], 0x00F5, 0, 0)  # BM_CLICK
    time.sleep(1.0)

# read clipboard
user32.OpenClipboard(0)
h = user32.GetClipboardData(13)  # CF_UNICODETEXT
if h:
    ptr = ctypes.windll.kernel32.GlobalLock(h)
    s = ctypes.c_wchar_p(ptr).value
    ctypes.windll.kernel32.GlobalUnlock(h)
    print(s[:8000])
else:
    print("clipboard empty")
user32.CloseClipboard()
