def ReadInput(file_path: str):
    with open(file_path, "r") as fs:
        first_line = fs.readline()
        [h, w] = map(int, first_line.split())

        map_data = [['' for _ in range(w)]]*h

        for y in range(h):
            line = fs.readline().removesuffix("\n")
            for x in range(w):
                map_data[y][x] = line[x]

        code = ""
        line = fs.readline()
        while line:
            code += line
            line = fs.readline()
        return map_data, code


