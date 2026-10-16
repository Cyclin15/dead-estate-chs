import ctypes, time, subprocess
ret = ctypes.windll.shell32.ShellExecuteW(None, 'runas', 'taskkill',
    '/IM "Dead Estate.exe" /F', None, 0)
print('ShellExecute ret:', ret)
if ret > 32:
    for _ in range(30):
        time.sleep(0.5)
        out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Dead Estate.exe'],
                             capture_output=True, text=True).stdout
        if 'Dead Estate.exe' not in out:
            print('game killed')
            break
    else:
        print('still running!'); print(out)
