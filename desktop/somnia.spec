# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "dist"

datas = []
binaries = []
hiddenimports = collect_submodules("hotel") + collect_submodules("app") + collect_submodules("config")
hiddenimports += [
    "hotel.management.commands.init_hotel",
    "hotel.management.commands.seed_demo",
    "rest_framework",
    "corsheaders",
    "simpleui",
    "PIL",
]

for package in ("django", "rest_framework", "corsheaders", "simpleui", "PIL", "webview", "waitress"):
    collected = collect_all(package)
    datas += collected[0]
    binaries += collected[1]
    hiddenimports += collected[2]

datas += [
    (str(BACKEND / "hotel"), "hotel"),
    (str(BACKEND / "app"), "app"),
    (str(BACKEND / "config"), "config"),
]
if FRONTEND.exists():
    datas.append((str(FRONTEND), "frontend"))

a = Analysis(
    [str(ROOT / "desktop" / "launch.py")],
    pathex=[str(BACKEND), str(ROOT / "desktop")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="眠栖Somnia",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="眠栖Somnia",
)
