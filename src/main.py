import argparse

from ide import Ide
from read_input import read_input


def main():
    parser = argparse.ArgumentParser(
        prog="2026-os Dusza Árpád Országos Programozói Emlékverseny-re készült beadandó projekt",
        description="""
            Beolvassa a bemeneti állományt, majd a grafikus felületet megnyitja.
            A program futása során a naplófájl tartalmát a kimeneti állományba fogja írni.
            A program futtatható felhasználói beavatkozás nélkül is a csendes opcióval (-q)""",
        add_help=False
    )

    parser.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS, help="Megjeleníti ezt az üzenetet és kilép")
    parser.add_argument("input", help="Elérési út a bemeneti állományhoz vagy a bemeneti állományok könyvtárához")
    parser.add_argument("output", help="Elérési út a kimeneti állományhoz vagy kimeneti állományok könyvtárához")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true", help="Ha meg van adva, akkor a program nem fog semmilyen felhasználói beavatkozást kérni (csendes mód)")
    group.add_argument("-a", "--all", action="store_true", help="Ugyan az mint a -q opció, csak a bemeneti könyvtárban található összes fájlra le fogja futtatni a programot. A naplófájlokat a kimeneti könyvtárba fogja írni.")

    args = parser.parse_args()

    print(args)

    map_data, code = read_input(args.input)
    print(map_data, code)

    Ide()

if __name__ == "__main__":
    main()
