import subprocess
import sys

# Required libraries
required_libraries = [
    "Pillow",        # For image processing (Image, ImageTk, etc.)
    "tk",            # For tkinter GUI
    "ctypes",        # For interacting with C functions
    "struct",        # For working with packed binary data
    "zlib",          # For compression
    "shutil",        # For file operations like copy, remove, etc.
]

for lib in required_libraries:
    try:
        __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
