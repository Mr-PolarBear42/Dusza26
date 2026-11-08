# Dusza 2026 – Arany bánya

A 2026-os Dusza Árpád Országos Programozói Emlékversenyre készült projekt.
Az alkalmazás egy MineScript-programozási környezetet és egy robotot
szimuláló értelmezőt tartalmaz. A pályán mozgó robot aranyat bányászhat, a
program pedig grafikus felületen futtatható és lépésenként hibakereshető.

## Főbb funkciók

- PyQt6-alapú grafikus felület Blockly-szerkesztővel;
- a pálya és a robot állapotának megjelenítése;
- MineScript-programok futtatása normál vagy hibakeresési módban;
- változók, feltételek, ciklusok és logikai vagy aritmetikai kifejezések;
- futási napló készítése a megadott kimeneti fájlba;
- egyetlen feladat vagy egy teljes bemeneti könyvtár feldolgozása;
- a futtatás grafikus felület nélkül is elvégezhető.

## Követelmények

- Python 3.14 vagy újabb;
- [uv](https://docs.astral.sh/uv/getting-started/installation/) a
  függőségek és a projekt futtatásához.

A függőségek között a PyQt6, a PyQt6-WebEngine és a PyInstaller szerepel.
Telepítésük és a virtuális környezet létrehozása:

```bash
uv sync
```

## Használat

### Grafikus mód

A grafikus felület a pályát, a Blockly-szerkesztőt, a generált MineScriptet és
a futási naplót jeleníti meg:

```bash
uv run python src/main.py <bemeneti-fájl> <kimeneti-fájl>
```

Például:

```bash
uv run python src/main.py kisteszt.txt output.txt
```

A felületen a program normál futtatással vagy hibakeresési módban indítható.
Hibakeresés közben a végrehajtás előre és visszafelé is léptethető.

### Csendes mód

A `-q` vagy `--quiet` kapcsoló felhasználói beavatkozás nélkül futtatja a
feladatot, és a naplót a kimeneti fájlba írja:

```bash
uv run python src/main.py kisteszt.txt output.txt --quiet
```

### Több feladat feldolgozása

A `-a` vagy `--all` kapcsoló a bemeneti könyvtár minden fájlját feldolgozza,
és a kimeneti könyvtárban azonos fájlnevekkel hozza létre a naplókat:

```bash
uv run python src/main.py feladatok/ eredmenyek/ --all
```

A `--quiet` és a `--all` kapcsoló egyszerre nem használható.

## Bemeneti fájl formátuma

Az első sorban a pálya magassága és szélessége szerepel, szóközzel
elválasztva. Ezt követi a megadott számú, egyenként pontosan a szélességnek
megfelelő sor. A pálya után található a futtatandó MineScript-kód.

| Jel | Jelentés |
| --- | --- |
| `.` | szabad mező |
| `#` | szikla vagy fal |
| `@` | arany |
| `^`, `>`, `v`, `<` | a robot kezdőpozíciója és iránya |

Egy feladatfájl minimális példája:

```text
3 5
.....
..@..
..>..
step by 2
mine
```

Egy pályán pontosan egy robotnak kell szerepelnie.

## MineScript – rövid példa

```text
set steps to 2
while steps > 0
    step by 1
    set steps to steps - 1
if isThere 2
    mine
else
    turn by 1
```

A használt alapvető utasítások:

- `set <név> to <kifejezés>` – változó beállítása;
- `step by <kifejezés>` – előrelépés;
- `turn by <kifejezés>` – negyedfordulatok száma;
- `mine` – arany kibányászása az aktuális mezőről;
- `isThere <0|1|2>` – a robot előtti mező vizsgálata (`0`: szabad, `1`:
  szikla, `2`: arany);
- `print <kifejezés>` – érték kiírása a futási naplóba;
- `if ...` / `else` és `while ...` – feltételes végrehajtás és ciklus.

A blokkok behúzással készülnek. A futtató legfeljebb 1000 utasítást hajt végre
egy programból; a korlát túllépése a naplóban
`INSTRUCTION_COUNT_LIMIT_EXCEEDED` bejegyzést eredményez.

## Fordított futtatható fájl készítése

PyInstallerrel egyetlen futtatható fájl készíthető:

```bash
uv run pyinstaller --onefile \
  --add-data "src/assets:assets" \
  --add-data "src/blockly:blockly" \
  src/main.py
```

A létrejövő fájl helye: `dist/main` (Windows alatt jellemzően
`dist/main.exe`).

## Tesztek futtatása

A tesztek a MineScript-értelmező és a robot működését ellenőrzik. Ha a
PyTest még nincs telepítve a környezetben, a `--with` kapcsoló ideiglenesen
biztosítja:

```bash
uv run --with pytest pytest
```

## Könyvtárszerkezet

```text
src/
├── main.py                 # Parancssori belépési pont
├── ide.py                  # Grafikus IDE
├── blockly_editor.py       # Blockly-szerkesztő
├── map_viewer.py           # Pálya- és robotszimulációs nézet
├── interpreter/            # MineScript-értelmező és robotmodell
├── utils/                  # Segédmodulok
├── assets/                 # Ikonok és sprite-ok
└── blockly/                # Blockly erőforrások
tests/                      # Automatikus tesztek
```

## Licenc

A projekt dokumentációja és a versenyhez kapcsolódó anyagok a
[`docs/`](docs/) könyvtárban találhatók.