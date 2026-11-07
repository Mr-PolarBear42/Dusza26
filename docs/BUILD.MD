# Dusza Verseny 2026 (Arany bánya)

## A projekt függőségei
A uv csomag és projekt kezelőt le kell telepítened ahhoz, hogy futtatni vagy buildelni tudd a projektet.
Kövesd az utasításokat [innen](https://docs.astral.sh/uv/getting-started/installation/).

## A futtatható fájl buildelése

Futtasd a következő parancsokat egymás után:
```
uv add pyinstaller
```
```
uv run pyinstaller --onefile --add-data "src/assets:assets" src/main.py
```
Ez létre fog hozni egy `dist/main.exe` futtatható fájlt a projekt könyvtárában.