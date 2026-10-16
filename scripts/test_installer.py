# Dry-run check of install.bat path logic in a temp sandbox (nothing in the game dir is touched).
import os, shutil, subprocess, sys, io, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PKG = r"D:\Steam\steamapps\common\Dead Estate\_loc_work\汉化补丁"
root = tempfile.mkdtemp(prefix="depatch_")
game = os.path.join(root, "Dead Estate")
os.makedirs(os.path.join(game, "_loc_work"), exist_ok=True)
pkg = os.path.join(game, "_loc_work", "汉化补丁")
shutil.copytree(PKG, pkg)

# a fake original data.win
orig = os.path.join(game, "data.win")
with open(orig, "wb") as f:
    f.write(b"ORIGINAL" * 100)

print("sandbox game dir :", game)
print("package dir      :", pkg)

r = subprocess.run(["cmd", "/c", "install.bat"], cwd=pkg,
                   input=b"\r\n", capture_output=True)
print("--- install.bat exit:", r.returncode)
print(r.stdout.decode("utf-8", "replace")[-900:])

with open(orig, "rb") as f:
    head = f.read(8)
print("data.win now starts with:", head)
bak = os.path.join(pkg, "backup_original", "data.win")
print("backup exists:", os.path.exists(bak), "size:", os.path.getsize(bak) if os.path.exists(bak) else 0)

r2 = subprocess.run(["cmd", "/c", "uninstall.bat"], cwd=pkg, input=b"\r\n", capture_output=True)
print("--- uninstall.bat exit:", r2.returncode)
with open(orig, "rb") as f:
    head2 = f.read(8)
print("after uninstall data.win starts with:", head2)

# clean up the multi-GB copy
shutil.rmtree(root, ignore_errors=True)
print("sandbox removed")
