# mat2 Windows single-file build

Run `build-windows.ps1` on Windows with MSYS2 UCRT64 installed to build `dist\\mat2.exe`. The GitHub Actions workflow at `.github/workflows/mat2-release.yml` checks PyPI daily and automatically publishes a new GitHub Release when a new mat2 version appears.

The workflow builds on a clean Windows runner and bundles Python plus GTK/Poppler runtime libraries, so users do not need to install those dependencies. `mat2` is a command-line application, not a graphical-window application; run the released exe from PowerShell or Command Prompt, for example:

```powershell
.\mat2.exe --no-sandbox photo.jpg
```

Some uncommon formats may additionally require ExifTool or FFmpeg on `PATH`.
