import argparse
import os

from ide import Ide
from interpreter.interpreter import Interpreter
from interpreter.robot import Robot
from read_input import read_input


def main():
    parser = argparse.ArgumentParser(
        prog="2026-os Dusza Árpád Országos Programozói Emlékverseny-re készült beadandó projekt",
        description="""
            Beolvassa a bemeneti állományt, majd a grafikus felületet megnyitja.
            A program futása során a naplófájl tartalmát a kimeneti állományba fogja írni.
            A program futtatható felhasználói beavatkozás nélkül is a csendes opcióval (-q)""",
        add_help=False,
    )

    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Megjeleníti ezt az üzenetet és kilép",
    )
    parser.add_argument(
        "input",
        help="Elérési út a bemeneti állományhoz vagy a bemeneti állományok könyvtárához",
    )
    parser.add_argument(
        "output",
        help="Elérési út a kimeneti állományhoz vagy kimeneti állományok könyvtárához",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Ha meg van adva, akkor a program nem fog semmilyen felhasználói beavatkozást kérni (csendes mód)",
    )
    group.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Ugyan az mint a -q opció, csak a bemeneti könyvtárban található összes fájlra le fogja futtatni a programot. A naplófájlokat a kimeneti könyvtárba fogja írni.",
    )

    args = parser.parse_args()

    if args.quiet:
        generate(args.input, args.output)
    elif args.all:
        files = os.listdir(args.input)
        os.mkdir(args.output)
        for file in files:
            input_file = os.path.join(args.input, file)
            output_file = os.path.join(args.output, file)
            generate(input_file, output_file)

    else:
        map_data, w, h, code = read_input(args.input)
        Ide(map_data, w, h, code, args.output)

def generate(input_file: str, output_file: str):
    map_data, _w, _h, code = read_input(input_file)
    robot = Robot.from_map(map_data)
    out = Interpreter(robot).run(code)
    out.write(output_file)


if __name__ == "__main__":
    main()
