import os
import subprocess
import pathlib

print("Building CodeMind AI standalone package with PyInstaller...")

# دستور PyInstaller برای ساخت نسخه اجرایی
subprocess.run([
    "pyinstaller",
    "--onedir",
    "--name=codemind-ai",
    "--clean",
    "src/codemind/__init__.py"
], check=False)

print("Build process completed! Check 'dist/' folder.")
