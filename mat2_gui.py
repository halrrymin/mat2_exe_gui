import queue
import subprocess
import sys
import threading
import runpy
import sysconfig
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


class Mat2Gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("mat2 Metadata Cleaner")
        self.geometry("700x460")
        self.minsize(560, 360)
        self.files = []
        self.events = queue.Queue()
        self._build()
        self.after(100, self._poll)

    def _build(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")
        ttk.Button(top, text="Add files", command=self.add_files).pack(side="left")
        ttk.Button(top, text="Add folder", command=self.add_folder).pack(side="left", padx=8)
        ttk.Button(top, text="Clear", command=self.clear).pack(side="left")
        self.clean = ttk.Button(top, text="Clean metadata", command=self.start)
        self.clean.pack(side="right")
        self.listbox = tk.Listbox(self, selectmode=tk.EXTENDED)
        self.listbox.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        bottom = ttk.Frame(self, padding=(12, 0, 12, 12))
        bottom.pack(fill="x")
        self.progress = ttk.Progressbar(bottom, mode="indeterminate")
        self.progress.pack(fill="x")
        self.status = ttk.Label(bottom, text="Choose files to begin")
        self.status.pack(anchor="w", pady=(6, 0))

    def add_files(self):
        chosen = filedialog.askopenfilenames(title="Choose files")
        self._add(Path(p) for p in chosen)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Choose folder")
        if folder:
            self._add(p for p in Path(folder).iterdir() if p.is_file())

    def _add(self, paths):
        for path in paths:
            if path not in self.files:
                self.files.append(path)
                self.listbox.insert(tk.END, str(path))
        self.status.config(text=f"{len(self.files)} file(s) selected")

    def clear(self):
        self.files.clear()
        self.listbox.delete(0, tk.END)
        self.status.config(text="Choose files to begin")

    def start(self):
        if not self.files:
            messagebox.showinfo("mat2", "Add at least one file first.")
            return
        self.clean.config(state="disabled")
        self.progress.start(10)
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        command = [sys.executable, "--mat2-cli", "--no-sandbox"] + [str(p) for p in self.files]
        result = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", errors="replace")
        self.events.put((result.returncode, result.stdout + result.stderr))

    def _poll(self):
        try:
            code, output = self.events.get_nowait()
        except queue.Empty:
            self.after(100, self._poll)
            return
        self.progress.stop()
        self.clean.config(state="normal")
        if code == 0:
            self.status.config(text="Finished. Cleaned files were written next to the originals.")
            messagebox.showinfo("mat2", "Metadata cleaning finished.")
        else:
            self.status.config(text="Finished with errors; see the console output if launched there.")
            messagebox.showerror("mat2 error", output[-2000:] or "mat2 returned an error")
        self.after(100, self._poll)


if __name__ == "__main__":
    if "--mat2-cli" in sys.argv:
        sys.argv.remove("--mat2-cli")
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "mat2script"
        candidates = [base / "mat2-script.py", base / "mat2"]
        candidate = next((p for p in candidates if p.is_file()), None)
        if candidate is None:
            raise RuntimeError("The bundled mat2 command script was not found")
        runpy.run_path(str(candidate), run_name="__main__")
    else:
        Mat2Gui().mainloop()
