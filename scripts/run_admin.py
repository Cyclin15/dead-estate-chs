"""Launch admin_input.py ELEVATED via ShellExecute runas (UAC auto-approves on
this machine) and wait for it to finish. Usage:
  python run_admin.py OUT.png [--key KEY] [--click X Y] [--delay S] [--seq a,b,c]
"""
import sys, os, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(BASE, 'scripts', 'admin_input.py')


def main():
    out = sys.argv[1]
    args = [PY] + sys.argv[1:]
    # quote for ShellExecute parameters
    params = ' '.join('"%s"' % a for a in args)
    import ctypes
    ret = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 0)
    if ret <= 32:
        print('ShellExecute failed:', ret)
        sys.exit(1)
    # wait for the .done marker
    done = os.path.join(BASE, 'shots', out + '.done')
    import time
    for _ in range(120):
        if os.path.exists(done):
            print(open(done).read().strip())
            os.remove(done)
            return
        time.sleep(0.5)
    print('timeout waiting for', done)
    sys.exit(1)


if __name__ == '__main__':
    main()
