"""Elevated input+capture helper. MUST run elevated to send input to the
(elevated) game process. Usage:
  python admin_input.py OUT.png [--key KEY] [--click X Y] [--delay SEC] [--seq k1,k2,k3]
"""
import sys, os, time, ctypes, ctypes.wintypes

user32 = ctypes.windll.user32
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'shots')

KEYS = {'return': 0x0D, 'enter': 0x0D, 'esc': 0x1B, 'left': 0x25, 'up': 0x26,
        'right': 0x27, 'down': 0x28, 'space': 0x20, 'tab': 0x09, 'shift': 0x10,
        'ctrl': 0x11, 'alt': 0x12, 'backspace': 0x08, 'delete': 0x2E, 'end': 0x23,
        'home': 0x24, 'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B}


def vk_of(key):
    vk = KEYS.get(key)
    return vk if vk is not None else ord(key.upper())


def scancode_of(vk):
    m = user32.MapVirtualKeyW(vk, 0)  # MAPVK_VK_TO_VSC
    return m


def find_window():
    res = []

    def cb(h, _):
        if user32.IsWindowVisible(h):
            ln = user32.GetWindowTextLengthW(h)
            if ln:
                buf = ctypes.create_unicode_buffer(ln + 1)
                user32.GetWindowTextW(h, buf, ln + 1)
                res.append((h, buf.value))
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    for h, t in res:
        if 'Dead Estate' in t or '死亡庄园' in t:
            return h
    return None


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [('wVk', ctypes.c_ushort), ('wScan', ctypes.c_ushort),
                ('dwFlags', ctypes.c_ulong), ('time', ctypes.c_ulong),
                ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))]


class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        class _S(ctypes.Structure):
            _fields_ = [('ki', KEYBDINPUT)]
        _fields_ = [('ki', KEYBDINPUT)]
    _fields_ = [('type', ctypes.c_ulong), ('union', _U)]


def send_key(vk, hold=0.09):
    """Send via BOTH PostMessage (direct to game window, bypasses IME) and
    SendInput (system stream), so at least one path registers."""
    global hwnd
    sc = scancode_of(vk)
    lp_down = 1 | (sc << 16)
    lp_up = 1 | (sc << 16) | (1 << 30) | (1 << 31)
    if hwnd:
        for _ in range(2):
            user32.PostMessageW(hwnd, 0x0100, vk, lp_down)   # WM_KEYDOWN
            time.sleep(0.05)
            user32.PostMessageW(hwnd, 0x0101, vk, lp_up)     # WM_KEYUP
            time.sleep(0.05)
    # also SendInput with scancode flags
    down = INPUT(type=1)
    down.union.ki = KEYBDINPUT(0, sc, 0x0008, 0, None)
    up = INPUT(type=1)
    up.union.ki = KEYBDINPUT(0, sc, 0x0008 | 0x0002, 0, None)
    user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(INPUT))
    time.sleep(hold)
    user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(INPUT))


hwnd = None


def main():
    global hwnd
    args = sys.argv[1:]
    name = args[0]
    key = args[args.index('--key') + 1] if '--key' in args else None
    click = None
    if '--click' in args:
        i = args.index('--click')
        click = (int(args[i + 1]), int(args[i + 2]))
    delay = float(args[args.index('--delay') + 1]) if '--delay' in args else 0.7
    seq = args[args.index('--seq') + 1].split(',') if '--seq' in args else []

    user32.SetProcessDPIAware()
    hwnd = find_window()
    if not hwnd:
        open(os.path.join(OUT, name + '.done'), 'w').write('no window')
        sys.exit(1)
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    l, t, r, b = rect.left, rect.top, rect.right, rect.bottom

    # force the game to the foreground before injecting input
    fg_before = user32.GetForegroundWindow()
    ok_fg = False
    for _ in range(15):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        user32.SetFocus(hwnd)
        time.sleep(0.1)
        if user32.GetForegroundWindow() == hwnd:
            ok_fg = True
            break
    fg_after = user32.GetForegroundWindow()

    if click:
        user32.SetCursorPos(click[0], click[1])
        time.sleep(0.08)
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.05)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
        time.sleep(delay)
    if key:
        send_key(vk_of(key))
        time.sleep(delay)
    for k in seq:
        send_key(vk_of(k))
        time.sleep(0.55)

    from PIL import ImageGrab
    img = ImageGrab.grab(bbox=(l, t, r, b), all_screens=True)
    img.save(os.path.join(OUT, name))
    open(os.path.join(OUT, name + '.done'), 'w').write(
        'ok fg_same=%s' % (fg_before == fg_after == hwnd))
    print('ok')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        name = sys.argv[1] if len(sys.argv) > 1 else 'error.txt'
        with open(os.path.join(OUT, name + '.done'), 'w') as f:
            f.write('ERROR\n' + traceback.format_exc())
