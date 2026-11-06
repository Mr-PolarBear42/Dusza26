from sys import exit

if __name__ != "__main__":
    exit()

import sys

from read_input import ReadInput

quiet = False
input_file_name = None
output_file_name = None

def handle_arguments():
    global quiet, input_file_name, output_file_name
    if len(sys.argv) <= 1:
        return False
    if sys.argv[1] == "-q":
        if len(sys.argv) != 4:
            return False
        quiet = True
        input_file_name = sys.argv[2]
        output_file_name = sys.argv[3]
        return True
    elif len(sys.argv) == 3:
        input_file_name = sys.argv[1]
        output_file_name = sys.argv[2]
        return True
    else: 
        return False

if not handle_arguments():
    exit()

map_data, code = ReadInput(input_file_name)
print(map_data, code)