import sys
from cx_Freeze import setup, Executable



build_exe_options = {
    "packages": ["os", "idna","sys", "pandas", "csv", "serial", "numpy", "pathlib", "pyqtgraph", "PyQt5", "copy"],
    "excludes": ["tkinter"],
    "includes": ["atexit"],
    "include_files": ["GUI\Icons\chart.svg", "GUI\PopUpWindow.py", "GetArduino\get_arduino.py", "Processamento\Moving_Average.py"]
}


base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Medidor de GSR",
    version="1.0",
    description="Software para auxiliar na medição e vizualização de GSR",
    options={"build_exe": build_exe_options},
    executables=[Executable("Main.py", base=base)]
)