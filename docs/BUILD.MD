# Dusza Verseny 2026(Arany bánya)
## Building the executable
**pyinstaller**: You need the pyinstaller python module downloaded to build the executable.
This can must usually be done with one of the following commands:
```
pip install pyinstaller
```
```
py -3 -m pip install pyinstaller
```
#
then you need to run pyinstaller to pack the main.py file into a bundle, this aswell can most usually be done via one of the following commands:
```
pyinstaller --onefile main.py
```
```
py -3 -m pyinstaller --onefile main.py
```
```
py -m PyInstaller --onefile main.py
```