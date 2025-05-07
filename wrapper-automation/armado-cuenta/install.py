import subprocess
import sys
import importlib

def install_and_import(package):
    try:
        importlib.import_module(package)
    except ImportError:
        print(f"{package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    finally:
        globals()[package] = importlib.import_module(package)

if __name__ == "__main__":
    required_packages = ["numpy", "pandas", "requests", "flask"]
    for pkg in required_packages:
        install_and_import(pkg)

    # Now you can use the installed packages
    import numpy
    print("NumPy version:", numpy.__version__)