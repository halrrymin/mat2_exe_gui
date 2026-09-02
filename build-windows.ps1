<#
Build a single-file Windows executable for mat2.

Prerequisite: MSYS2 installed in C:\msys64, with the UCRT64 Python/GTK stack:
  pacman -Syu
  pacman -S --needed mingw-w64-ucrt-x86_64-python mingw-w64-ucrt-x86_64-python-gobject mingw-w64-ucrt-x86_64-python-cairo mingw-w64-ucrt-x86_64-poppler
#>
[CmdletBinding()]
param(
    [string]$MsysRoot = 'C:\msys64',
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'dist')
)

$ErrorActionPreference = 'Stop'
$python = Join-Path $MsysRoot 'ucrt64\bin\python.exe'
if (-not (Test-Path $python)) {
    throw "MSYS2 UCRT64 Python was not found at: $python"
}

& $python -m pip install --upgrade --break-system-packages pip
# GTK/PyGObject, cairo and Tk come from MSYS2; avoid asking pip to rebuild them.
& $python -m pip install --upgrade --break-system-packages --no-deps mat2
& $python -m pip install --upgrade --break-system-packages pyinstaller mutagen

$entryPoint = @'
from pathlib import Path
import runpy
import sysconfig

scripts = Path(sysconfig.get_path("scripts"))
for name in ("mat2-script.py", "mat2"):
    candidate = scripts / name
    if candidate.is_file():
        runpy.run_path(str(candidate), run_name="__main__")
        break
else:
    raise RuntimeError("The installed mat2 command script was not found")
'@
$entryFile = Join-Path $PSScriptRoot 'mat2_entry.py'
Set-Content -Path $entryFile -Value $entryPoint -NoNewline -Encoding utf8

try {
    & $python -m PyInstaller `
        --noconfirm --clean --onefile --console `
        --name mat2-gui `
        --distpath $OutputDirectory `
        --workpath (Join-Path $PSScriptRoot 'build') `
        --specpath $PSScriptRoot `
        --collect-all gi `
        --collect-all cairo `
        --collect-all libmat2 `
        --hidden-import gi.repository.GdkPixbuf `
        --hidden-import gi.repository.GLib `
        --hidden-import gi.repository.Poppler `
        --hidden-import tkinter `
        --add-data "$entryFile;." `
        (Join-Path $PSScriptRoot 'mat2_gui.py')
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE." }
}
finally {
    Remove-Item -Force $entryFile -ErrorAction SilentlyContinue
}

Write-Host "Created: $(Join-Path $OutputDirectory 'mat2-gui.exe')"
